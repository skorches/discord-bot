import discord
from discord.ext import commands
import yt_dlp
import asyncio
import logging
import os
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("musicbot")

# ── Bot configuration ────────────────────────────────────────────────────────
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('DISCORD_PREFIX', '!')

# yt-dlp options for high-quality audio streaming
YDL_OPTIONS = {
    'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytmsearch',
    'source_address': '0.0.0.0',
    'extract_flat': False,
    'prefer_ffmpeg': True,
}

# FFmpeg options optimized for stability
FFMPEG_BEFORE = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
FFMPEG_OPTS = '-vn -b:a 256k -ar 48000 -ac 2 -bufsize 512k'

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Disable default help command so we can use our custom one
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
tree = bot.tree  # Slash command tree


# ── Per-guild music player ───────────────────────────────────────────────────
class MusicPlayer:
    """Manages queue, playback, and voice state for a single guild."""

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.queue: list[dict] = []          # [{'query': ..., 'title': ..., 'duration': ..., 'thumbnail': ...}]
        self.current: dict | None = None
        self.voice_client: discord.VoiceClient | None = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.5                     # default 50 %

    # ── Voice helpers ────────────────────────────────────────────────────
    async def join_voice_channel(self, channel: discord.VoiceChannel):
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.move_to(channel)
        else:
            self.voice_client = await channel.connect()
        return self.voice_client

    async def leave_voice_channel(self):
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
        self.queue.clear()
        self.current = None
        self.is_playing = False
        self.is_paused = False

    # ── Audio source (PCM + VolumeTransformer) ───────────────────────────
    def _make_source(self, url: str):
        """Return a volume-controllable audio source."""
        raw = discord.FFmpegPCMAudio(
            url,
            before_options=FFMPEG_BEFORE,
            options=FFMPEG_OPTS,
        )
        return discord.PCMVolumeTransformer(raw, volume=self.volume)

    # ── Playback ─────────────────────────────────────────────────────────
    async def play_next(self):
        if not self.queue:
            self.is_playing = False
            self.current = None
            return

        self.is_playing = True
        self.is_paused = False
        self.current = self.queue.pop(0)

        # Extract fresh URL at play-time so it doesn't expire while queued
        info = await asyncio.to_thread(_extract_audio_url, self.current['query'])
        if info is None:
            log.warning("Failed to extract URL for '%s', skipping", self.current.get('title', '?'))
            await self.play_next()
            return

        source = self._make_source(info['url'])

        def _after(error):
            if error:
                log.error("Playback error: %s", error)
            asyncio.run_coroutine_threadsafe(self.play_next(), bot.loop)

        self.voice_client.play(source, after=_after)

    async def add_to_queue(self, entry: dict):
        """Add a song dict to the queue and start playing if idle."""
        self.queue.append(entry)
        if not self.is_playing and self.voice_client and not self.voice_client.is_playing():
            await self.play_next()

    def pause(self):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            self.is_paused = True

    def resume(self):
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            self.is_paused = False

    def stop_playback(self):
        """Stop playback without disconnecting."""
        if self.voice_client:
            self.voice_client.stop()
        self.is_playing = False
        self.current = None

    def set_volume(self, vol_pct: int):
        self.volume = vol_pct / 100
        if self.voice_client and self.voice_client.source:
            self.voice_client.source.volume = self.volume


# Guild-id → MusicPlayer mapping
_players: dict[int, MusicPlayer] = {}


def get_player(guild_id: int) -> MusicPlayer:
    if guild_id not in _players:
        _players[guild_id] = MusicPlayer(guild_id)
    return _players[guild_id]


# ── Interactive control buttons ──────────────────────────────────────────────
class MusicPlayerControls(discord.ui.View):
    def __init__(self, guild_id: int, timeout=900):
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
        self.control_message = None

    @property
    def player(self) -> MusicPlayer:
        return get_player(self.guild_id)

    async def update_buttons(self):
        p = self.player
        if p.is_paused:
            self.play_pause_button.emoji = "▶️"
            self.play_pause_button.label = "Resume"
        else:
            self.play_pause_button.emoji = "⏸️"
            self.play_pause_button.label = "Pause"

        has_music = p.current is not None
        self.play_pause_button.disabled = not has_music
        self.stop_button.disabled = not has_music
        self.next_button.disabled = len(p.queue) == 0
        self.previous_button.disabled = True  # needs history

    async def _refresh(self):
        await self.update_buttons()
        if self.control_message:
            try:
                await self.control_message.edit(view=self)
            except discord.NotFound:
                pass

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary, label="Previous")
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏮️ Previous song feature not available yet", ephemeral=True)

    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.primary, label="Pause")
    async def play_pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        p = self.player
        if p.is_paused:
            p.resume()
            await interaction.response.send_message("▶️ Resumed", ephemeral=True)
        elif p.voice_client and p.voice_client.is_playing():
            p.pause()
            await interaction.response.send_message("⏸️ Paused", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is currently playing", ephemeral=True)
            return
        await self._refresh()

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, label="Stop")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.stop_playback()
        await interaction.response.send_message("⏹️ Stopped", ephemeral=True)
        await self._refresh()

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, label="Next")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        p = self.player
        if p.voice_client and p.voice_client.is_playing():
            p.voice_client.stop()  # after-callback triggers play_next
            await interaction.response.send_message("⏭️ Skipped", ephemeral=True)
        elif p.queue:
            await p.play_next()
            await interaction.response.send_message("⏭️ Playing next song", ephemeral=True)
        else:
            await interaction.response.send_message("No songs in queue", ephemeral=True)
            return
        await self._refresh()


# ── yt-dlp helpers (synchronous – run via asyncio.to_thread) ─────────────────
def _search_video(query: str) -> dict | None:
    """Return metadata (title, duration, thumbnail, query) WITHOUT a stream URL.

    The actual stream URL is extracted later at play-time to avoid expiry.
    """
    with yt_dlp.YoutubeDL({**YDL_OPTIONS, 'extract_flat': True}) as ydl:
        try:
            if not query.startswith(('http://', 'https://', 'www.', 'music.youtube.com')):
                for prefix in ('ytmsearch:', 'ytsearch:'):
                    try:
                        info = ydl.extract_info(f"{prefix}{query}", download=False)
                        if 'entries' in info and info['entries']:
                            info = info['entries'][0]
                            break
                    except Exception as exc:
                        log.debug("Search with %s failed: %s", prefix, exc)
                        continue
                else:
                    return None
            else:
                info = ydl.extract_info(query, download=False)

            return {
                'query': info.get('url') or info.get('webpage_url') or query,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0) or 0,
                'thumbnail': info.get('thumbnail', ''),
            }
        except Exception:
            log.exception("Error searching for '%s'", query)
            return None


def _extract_audio_url(query: str) -> dict | None:
    """Full extraction – returns dict with 'url' key (stream URL)."""
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0] if info.get('entries') else None
            if info is None:
                return None

            if 'url' in info:
                audio_url = info['url']
            elif 'formats' in info:
                formats = info['formats']
                audio_only = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                if audio_only:
                    audio_only.sort(key=lambda f: f.get('abr', 0) or f.get('tbr', 0), reverse=True)
                    audio_url = audio_only[0]['url']
                elif formats:
                    audio_url = formats[0]['url']
                else:
                    return None
            else:
                return None

            return {'url': audio_url}
        except Exception:
            log.exception("Error extracting audio URL for '%s'", query)
            return None


# ── Shared command logic (used by both prefix and slash commands) ─────────────
def _require_voice(user) -> discord.VoiceChannel | None:
    """Return the user's voice channel or None."""
    return user.voice.channel if user.voice else None


def _format_duration(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{int(m)}:{int(s):02d}"


async def _cmd_join(guild_id: int, channel: discord.VoiceChannel) -> str:
    player = get_player(guild_id)
    await player.join_voice_channel(channel)
    return f"Joined {channel.name}"


async def _cmd_leave(guild_id: int) -> str:
    player = get_player(guild_id)
    await player.leave_voice_channel()
    return "Left the voice channel"


async def _cmd_play(guild_id: int, channel: discord.VoiceChannel, query: str):
    """Returns (embed, view) on success or a str error message."""
    player = get_player(guild_id)

    if not player.voice_client or not player.voice_client.is_connected():
        await player.join_voice_channel(channel)

    info = await asyncio.to_thread(_search_video, query)
    if not info:
        return "❌ Could not find the requested song. Please try a different search term or URL."

    will_play_now = (
        not player.is_playing
        and player.voice_client
        and not player.voice_client.is_playing()
    )

    await player.add_to_queue(info)

    embed = discord.Embed(
        title="🎵 Now Playing" if will_play_now else "🎵 Added to Queue",
        description=f"**{info['title']}**",
        color=discord.Color.green(),
    )
    embed.add_field(name="Duration", value=_format_duration(info['duration']), inline=True)
    if not will_play_now:
        embed.add_field(name="Position in Queue", value=str(len(player.queue)), inline=True)
    if info['thumbnail']:
        embed.set_thumbnail(url=info['thumbnail'])

    view = MusicPlayerControls(guild_id)
    await view.update_buttons()
    return (embed, view)


def _cmd_pause(guild_id: int) -> str:
    player = get_player(guild_id)
    if player.voice_client and player.voice_client.is_playing():
        player.pause()
        return "⏸️ Paused"
    return "Nothing is currently playing"


def _cmd_resume(guild_id: int) -> str:
    player = get_player(guild_id)
    if player.voice_client and player.voice_client.is_paused():
        player.resume()
        return "▶️ Resumed"
    return "Nothing is currently paused"


def _cmd_skip(guild_id: int) -> str:
    player = get_player(guild_id)
    if player.voice_client and player.voice_client.is_playing():
        player.voice_client.stop()
        return "⏭️ Skipped"
    return "Nothing is currently playing"


def _cmd_stop(guild_id: int) -> str:
    player = get_player(guild_id)
    player.stop_playback()
    player.queue.clear()
    return "⏹️ Stopped playback and cleared queue"


def _cmd_queue(guild_id: int) -> discord.Embed | str:
    player = get_player(guild_id)
    if not player.current and not player.queue:
        return "The queue is empty"
    embed = discord.Embed(title="📋 Music Queue", color=discord.Color.blue())
    if player.current:
        embed.add_field(name="🎵 Now Playing", value=player.current['title'], inline=False)
    if player.queue:
        lines = [f"{i+1}. {s['title']}" for i, s in enumerate(player.queue[:10])]
        if len(player.queue) > 10:
            lines.append(f"... and {len(player.queue) - 10} more")
        embed.add_field(name="Up Next", value="\n".join(lines), inline=False)
    return embed


def _cmd_clear(guild_id: int) -> str:
    get_player(guild_id).queue.clear()
    return "🗑️ Queue cleared"


def _cmd_volume(guild_id: int, vol: int | None) -> str:
    player = get_player(guild_id)
    if vol is None:
        return f"Current volume: {int(player.volume * 100)}%"
    if not 0 <= vol <= 100:
        return "Volume must be between 0 and 100"
    player.set_volume(vol)
    return f"🔊 Volume set to {vol}%"


def _cmd_help() -> discord.Embed:
    embed = discord.Embed(
        title="🎵 Music Bot Commands",
        description=f"Use `/` for slash commands or `{PREFIX}` for prefix commands",
        color=discord.Color.blue(),
    )
    cmds = [
        (f"`/join` or `{PREFIX}join`", "Join your voice channel"),
        (f"`/leave` or `{PREFIX}leave`", "Leave the voice channel and clear queue"),
        (f"`/play <song/url>` or `{PREFIX}play`", "Play a song from YouTube or other sources"),
        (f"`/pause` or `{PREFIX}pause`", "Pause the current song"),
        (f"`/resume` or `{PREFIX}resume`", "Resume the paused song"),
        (f"`/skip` or `{PREFIX}skip`", "Skip the current song"),
        (f"`/stop` or `{PREFIX}stop`", "Stop playback and clear queue"),
        (f"`/queue` or `{PREFIX}queue`", "Show the current queue"),
        (f"`/clear` or `{PREFIX}clear`", "Clear the queue"),
        (f"`/volume <0-100>` or `{PREFIX}volume`", "Set or show the volume"),
        (f"`/help` or `{PREFIX}help`", "Show this help message"),
    ]
    for name, desc in cmds:
        embed.add_field(name=name, value=desc, inline=False)
    return embed


# ── Permission check: user must be in a voice channel ────────────────────────
def voice_required(func):
    """Decorator for prefix commands that require the author to be in a voice channel."""
    @wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command!")
            return
        return await func(ctx, *args, **kwargs)
    return wrapper


# ── Events ───────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    log.info("%s has connected to Discord!", bot.user)
    log.info("Bot is in %d guild(s)", len(bot.guilds))
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name=f"{PREFIX}help")
    )
    try:
        synced = await tree.sync()
        log.info("Synced %d slash command(s)", len(synced))
    except Exception:
        log.exception("Failed to sync slash commands")


# ── Prefix commands ──────────────────────────────────────────────────────────
@bot.command(name='join', aliases=['j', 'connect'])
@voice_required
async def cmd_join(ctx):
    """Join your voice channel"""
    try:
        msg = await _cmd_join(ctx.guild.id, ctx.author.voice.channel)
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"Failed to join voice channel: {e}")


@bot.command(name='leave', aliases=['disconnect', 'dc'])
async def cmd_leave(ctx):
    """Leave the voice channel"""
    await ctx.send(await _cmd_leave(ctx.guild.id))


@bot.command(name='play', aliases=['p'])
@voice_required
async def cmd_play(ctx, *, query: str):
    """Play a song from YouTube or other sources"""
    loading_msg = await ctx.send("🔍 Searching for the song...")
    try:
        result = await _cmd_play(ctx.guild.id, ctx.author.voice.channel, query)
        if isinstance(result, str):
            await loading_msg.edit(content=result)
        else:
            embed, view = result
            await loading_msg.edit(content=None, embed=embed, view=view)
            view.control_message = loading_msg
    except Exception as e:
        await loading_msg.edit(content=f"❌ An error occurred: {e}")


@bot.command(name='pause')
async def cmd_pause(ctx):
    """Pause the current song"""
    await ctx.send(_cmd_pause(ctx.guild.id))


@bot.command(name='resume', aliases=['r'])
async def cmd_resume(ctx):
    """Resume the paused song"""
    await ctx.send(_cmd_resume(ctx.guild.id))


@bot.command(name='skip', aliases=['s', 'next'])
async def cmd_skip(ctx):
    """Skip the current song"""
    await ctx.send(_cmd_skip(ctx.guild.id))


@bot.command(name='stop')
async def cmd_stop(ctx):
    """Stop playback and clear queue (stays in channel)"""
    await ctx.send(_cmd_stop(ctx.guild.id))


@bot.command(name='queue', aliases=['q'])
async def cmd_queue(ctx):
    """Show the current queue"""
    result = _cmd_queue(ctx.guild.id)
    if isinstance(result, str):
        await ctx.send(result)
    else:
        await ctx.send(embed=result)


@bot.command(name='clear')
async def cmd_clear(ctx):
    """Clear the queue"""
    await ctx.send(_cmd_clear(ctx.guild.id))


@bot.command(name='volume', aliases=['vol'])
async def cmd_volume(ctx, vol: int = None):
    """Set or show the volume (0-100)"""
    await ctx.send(_cmd_volume(ctx.guild.id, vol))


@bot.command(name='help')
async def cmd_help(ctx):
    """Show available commands"""
    await ctx.send(embed=_cmd_help())


# ── Slash commands ───────────────────────────────────────────────────────────
@tree.command(name="join", description="Join your voice channel")
async def slash_join(interaction: discord.Interaction):
    ch = _require_voice(interaction.user)
    if not ch:
        await interaction.response.send_message("You need to be in a voice channel!", ephemeral=True)
        return
    try:
        msg = await _cmd_join(interaction.guild_id, ch)
        await interaction.response.send_message(msg)
    except Exception as e:
        await interaction.response.send_message(f"Failed to join: {e}", ephemeral=True)


@tree.command(name="leave", description="Leave the voice channel")
async def slash_leave(interaction: discord.Interaction):
    await interaction.response.send_message(await _cmd_leave(interaction.guild_id))


@tree.command(name="play", description="Play a song from YouTube or other sources")
async def slash_play(interaction: discord.Interaction, query: str):
    try:
        await interaction.response.defer()
    except (discord.errors.NotFound, discord.errors.InteractionResponded):
        return

    ch = _require_voice(interaction.user)
    if not ch:
        await interaction.followup.send("You need to be in a voice channel!", ephemeral=True)
        return

    try:
        result = await _cmd_play(interaction.guild_id, ch, query)
        if isinstance(result, str):
            await interaction.followup.send(result)
        else:
            embed, view = result
            msg = await interaction.followup.send(embed=embed, view=view)
            view.control_message = msg
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {e}")


@tree.command(name="pause", description="Pause the current song")
async def slash_pause(interaction: discord.Interaction):
    await interaction.response.send_message(_cmd_pause(interaction.guild_id))


@tree.command(name="resume", description="Resume the paused song")
async def slash_resume(interaction: discord.Interaction):
    await interaction.response.send_message(_cmd_resume(interaction.guild_id))


@tree.command(name="skip", description="Skip the current song")
async def slash_skip(interaction: discord.Interaction):
    await interaction.response.send_message(_cmd_skip(interaction.guild_id))


@tree.command(name="stop", description="Stop playback and clear queue")
async def slash_stop(interaction: discord.Interaction):
    await interaction.response.send_message(_cmd_stop(interaction.guild_id))


@tree.command(name="queue", description="Show the current queue")
async def slash_queue(interaction: discord.Interaction):
    result = _cmd_queue(interaction.guild_id)
    if isinstance(result, str):
        await interaction.response.send_message(result, ephemeral=True)
    else:
        await interaction.response.send_message(embed=result)


@tree.command(name="clear", description="Clear the queue")
async def slash_clear(interaction: discord.Interaction):
    await interaction.response.send_message(_cmd_clear(interaction.guild_id))


@tree.command(name="volume", description="Set or show the volume (0-100)")
async def slash_volume(interaction: discord.Interaction, volume: int = None):
    await interaction.response.send_message(_cmd_volume(interaction.guild_id, volume))


@tree.command(name="help", description="Show available commands")
async def slash_help(interaction: discord.Interaction):
    await interaction.response.send_message(embed=_cmd_help(), ephemeral=True)


# ── Error handling ───────────────────────────────────────────────────────────
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument. Use `{PREFIX}help` for command usage.")
    else:
        await ctx.send(f"An error occurred: {error}")
        log.error("Command error: %s", error, exc_info=error)


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not TOKEN:
        log.critical("DISCORD_TOKEN not found in environment variables!")
        log.critical("Please create a .env file with your Discord bot token.")
    else:
        bot.run(TOKEN, log_handler=None)  # we already configured logging

