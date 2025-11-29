import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
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
    # Get the best quality audio stream URL directly
    'extract_flat': False,
    # Prefer higher quality audio formats
    'prefer_ffmpeg': True,
}

# FFmpeg options for refined and smooth audio quality
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -reconnect_at_eof 1 -fflags +genpts+discardcorrupt -err_detect ignore_err',
    'options': '-vn -af "bass=g=3:f=80,treble=g=1,volume=0.95" -b:a 256k -ar 48000 -ac 2 -bufsize 512k -maxrate 256k'
}

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Disable default help command so we can use our custom one
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
tree = bot.tree  # Slash command tree


class MusicPlayer:
    def __init__(self):
        self.queue = []
        self.current = None
        self.voice_client = None
        self.is_playing = False
        self.is_paused = False
        self.control_view = None  # Store the current control view

    async def join_voice_channel(self, channel):
        """Join a voice channel"""
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.move_to(channel)
        else:
            self.voice_client = await channel.connect()
        return self.voice_client

    async def leave_voice_channel(self):
        """Leave the voice channel"""
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
        self.queue.clear()
        self.current = None
        self.is_playing = False
        self.is_paused = False

    def get_audio_source(self, url):
        """Get audio source from URL with high-quality settings"""
        return discord.FFmpegOpusAudio(
            url,
            **FFMPEG_OPTIONS
        )

    async def play_next(self):
        """Play the next song in the queue"""
        if len(self.queue) > 0:
            self.is_playing = True
            self.is_paused = False
            self.current = self.queue.pop(0)
            
            source = self.get_audio_source(self.current['url'])
            self.voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(), bot.loop
                ) if e is None else None
            )
        else:
            self.is_playing = False
            self.current = None

    async def add_to_queue(self, url, title):
        """Add a song to the queue"""
        self.queue.append({'url': url, 'title': title})
        if not self.is_playing and self.voice_client and not self.voice_client.is_playing():
            await self.play_next()

    def pause(self):
        """Pause the current song"""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            self.is_paused = True

    def resume(self):
        """Resume the paused song"""
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            self.is_paused = False

    def stop(self):
        """Stop the current song"""
        if self.voice_client:
            self.voice_client.stop()
        self.is_playing = False
        self.current = None


# Global music player instance
music_player = MusicPlayer()


# Music Player Control Buttons
class MusicPlayerControls(discord.ui.View):
    def __init__(self, timeout=300):
        super().__init__(timeout=timeout)
        self.control_message = None
    
    async def update_buttons(self):
        """Update button states based on player status"""
        # Update play/pause button
        if music_player.is_paused:
            self.play_pause_button.emoji = "▶️"
            self.play_pause_button.label = "Resume"
        else:
            self.play_pause_button.emoji = "⏸️"
            self.play_pause_button.label = "Pause"
        
        # Enable/disable buttons based on state
        has_music = music_player.current is not None
        self.play_pause_button.disabled = not has_music
        self.stop_button.disabled = not has_music
        self.next_button.disabled = len(music_player.queue) == 0
        self.previous_button.disabled = True  # Previous not implemented yet
    
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary, label="Previous")
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to previous song (not implemented - would need history)"""
        await interaction.response.send_message("⏮️ Previous song feature not available yet", ephemeral=True)
    
    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.primary, label="Pause")
    async def play_pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle play/pause"""
        if music_player.is_paused:
            music_player.resume()
            await interaction.response.send_message("▶️ Resumed", ephemeral=True)
        elif music_player.voice_client and music_player.voice_client.is_playing():
            music_player.pause()
            await interaction.response.send_message("⏸️ Paused", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is currently playing", ephemeral=True)
            return
        
        # Update button state
        await self.update_buttons()
        if self.control_message:
            try:
                await self.control_message.edit(view=self)
            except:
                pass
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, label="Stop")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Stop playback"""
        music_player.stop()
        await interaction.response.send_message("⏹️ Stopped", ephemeral=True)
        
        # Update button state
        await self.update_buttons()
        if self.control_message:
            try:
                await self.control_message.edit(view=self)
            except:
                pass
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, label="Next")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Skip to next song"""
        if music_player.voice_client and music_player.voice_client.is_playing():
            music_player.voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped", ephemeral=True)
        elif len(music_player.queue) > 0:
            await music_player.play_next()
            await interaction.response.send_message("⏭️ Playing next song", ephemeral=True)
        else:
            await interaction.response.send_message("No songs in queue", ephemeral=True)
            return
        
        # Update button state
        await self.update_buttons()
        if self.control_message:
            try:
                await self.control_message.edit(view=self)
            except:
                pass


def get_video_info(query):
    """Extract video information using yt-dlp"""
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            # If it's not a URL, treat it as a search query
            if not query.startswith(('http://', 'https://', 'www.', 'music.youtube.com')):
                # Try YouTube Music first for better quality and full-length tracks
                search_query = f"ytmsearch:{query}"
                try:
                    info = ydl.extract_info(search_query, download=False)
                    # If it's a search result, get the first video
                    if 'entries' in info:
                        if info['entries']:
                            info = info['entries'][0]
                        else:
                            raise Exception("No results from YouTube Music")
                    else:
                        raise Exception("Invalid response from YouTube Music")
                except Exception as e:
                    # Fallback to regular YouTube search if YouTube Music fails
                    print(f"YouTube Music search failed ({e}), trying regular YouTube search...")
                    search_query = f"ytsearch:{query}"
                    info = ydl.extract_info(search_query, download=False)
                    # If it's a search result, get the first video
                    if 'entries' in info:
                        if info['entries']:
                            info = info['entries'][0]
                        else:
                            return None
                    else:
                        return None
            else:
                search_query = query
                info = ydl.extract_info(search_query, download=False)
            # Get the best audio URL from the format list
            if 'url' in info:
                audio_url = info['url']
            elif 'formats' in info:
                # Find the best audio format
                formats = info.get('formats', [])
                audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                if audio_formats:
                    # Sort by bitrate/quality and get the best one
                    audio_formats.sort(key=lambda x: x.get('abr', 0) or x.get('tbr', 0), reverse=True)
                    audio_url = audio_formats[0]['url']
                else:
                    # Fallback to best format with audio
                    best_format = formats[0] if formats else None
                    audio_url = best_format['url'] if best_format else None
            else:
                audio_url = None
            
            if not audio_url:
                raise Exception("Could not extract audio URL")
            
            return {
                'url': audio_url,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', '')
            }
        except Exception as e:
            print(f"Error extracting info: {e}")
            import traceback
            traceback.print_exc()
            return None


@bot.event
async def on_ready():
    try:
        print(f'{bot.user} has connected to Discord!')
        print(f'Bot is in {len(bot.guilds)} guild(s)')
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{PREFIX}help"))
        # Sync slash commands
        try:
            synced = await tree.sync()
            print(f'Synced {len(synced)} slash command(s)')
        except Exception as e:
            print(f'Failed to sync slash commands: {e}')
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f'Error in on_ready: {e}')
        import traceback
        traceback.print_exc()


@bot.command(name='join', aliases=['j', 'connect'])
async def join(ctx):
    """Join the voice channel the user is in"""
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to use this command!")
        return
    
    channel = ctx.author.voice.channel
    try:
        await music_player.join_voice_channel(channel)
        await ctx.send(f"Joined {channel.name}")
    except Exception as e:
        await ctx.send(f"Failed to join voice channel: {e}")


@bot.command(name='leave', aliases=['disconnect', 'dc', 'stop'])
async def leave(ctx):
    """Leave the voice channel"""
    await music_player.leave_voice_channel()
    await ctx.send("Left the voice channel")


@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query):
    """Play a song from YouTube or other sources"""
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to use this command!")
        return
    
    # Join voice channel if not already connected
    if not music_player.voice_client or not music_player.voice_client.is_connected():
        channel = ctx.author.voice.channel
        await music_player.join_voice_channel(channel)
    
    # Show loading message
    loading_msg = await ctx.send("🔍 Searching for the song...")
    
    try:
        # Extract video info
        info = get_video_info(query)
        
        if not info:
            await loading_msg.edit(content="❌ Could not find the requested song. Please try a different search term or URL.")
            return
        
        # Check if this song will start playing immediately (before adding to queue)
        will_play_now = not music_player.is_playing and music_player.voice_client and not music_player.voice_client.is_playing()
        
        # Add to queue
        await music_player.add_to_queue(info['url'], info['title'])
        
        # Format duration
        duration = info['duration']
        minutes, seconds = divmod(duration, 60)
        duration_str = f"{int(minutes)}:{int(seconds):02d}"
        
        embed = discord.Embed(
            title="🎵 Added to Queue" if not will_play_now else "🎵 Now Playing",
            description=f"**{info['title']}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Duration", value=duration_str, inline=True)
        if not will_play_now:
            embed.add_field(name="Position in Queue", value=len(music_player.queue), inline=True)
        
        if info['thumbnail']:
            embed.set_thumbnail(url=info['thumbnail'])
        
        # Always show control buttons when there's music (playing or queued)
        view = MusicPlayerControls()
        await view.update_buttons()
        
        await loading_msg.edit(content=None, embed=embed, view=view)
        
        # Store control message reference
        view.control_message = loading_msg
        
    except Exception as e:
        await loading_msg.edit(content=f"❌ An error occurred: {str(e)}")


@bot.command(name='pause')
async def pause(ctx):
    """Pause the current song"""
    if music_player.voice_client and music_player.voice_client.is_playing():
        music_player.pause()
        await ctx.send("⏸️ Paused")
    else:
        await ctx.send("Nothing is currently playing")


@bot.command(name='resume', aliases=['r'])
async def resume(ctx):
    """Resume the paused song"""
    if music_player.voice_client and music_player.voice_client.is_paused():
        music_player.resume()
        await ctx.send("▶️ Resumed")
    else:
        await ctx.send("Nothing is currently paused")


@bot.command(name='skip', aliases=['s', 'next'])
async def skip(ctx):
    """Skip the current song"""
    if music_player.voice_client and music_player.voice_client.is_playing():
        music_player.voice_client.stop()
        await ctx.send("⏭️ Skipped")
    else:
        await ctx.send("Nothing is currently playing")


@bot.command(name='queue', aliases=['q'])
async def queue(ctx):
    """Show the current queue"""
    if not music_player.current and len(music_player.queue) == 0:
        await ctx.send("The queue is empty")
        return
    
    embed = discord.Embed(title="📋 Music Queue", color=discord.Color.blue())
    
    if music_player.current:
        embed.add_field(
            name="🎵 Now Playing",
            value=music_player.current['title'],
            inline=False
        )
    
    if len(music_player.queue) > 0:
        queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(music_player.queue[:10])])
        if len(music_player.queue) > 10:
            queue_list += f"\n... and {len(music_player.queue) - 10} more"
        embed.add_field(name="Up Next", value=queue_list, inline=False)
    
    await ctx.send(embed=embed)


@bot.command(name='clear')
async def clear(ctx):
    """Clear the queue"""
    music_player.queue.clear()
    await ctx.send("🗑️ Queue cleared")


@bot.command(name='volume', aliases=['vol'])
async def volume(ctx, vol: int = None):
    """Set or show the volume (0-100)"""
    if vol is None:
        if music_player.voice_client and music_player.voice_client.source:
            current_vol = int(music_player.voice_client.source.volume * 100)
            await ctx.send(f"Current volume: {current_vol}%")
        else:
            await ctx.send("No audio source is currently playing")
    else:
        if 0 <= vol <= 100:
            if music_player.voice_client and music_player.voice_client.source:
                music_player.voice_client.source.volume = vol / 100
                await ctx.send(f"🔊 Volume set to {vol}%")
            else:
                await ctx.send("No audio source is currently playing")
        else:
            await ctx.send("Volume must be between 0 and 100")


@bot.command(name='help')
async def help_command(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="🎵 Music Bot Commands",
        description="Commands for the high-quality audio streaming bot",
        color=discord.Color.blue()
    )
    
    commands_list = [
        ("!join / !j", "Join your voice channel"),
        ("!leave / !dc", "Leave the voice channel"),
        ("!play <song/url> / !p", "Play a song from YouTube or other sources"),
        ("!pause", "Pause the current song"),
        ("!resume / !r", "Resume the paused song"),
        ("!skip / !s", "Skip the current song"),
        ("!queue / !q", "Show the current queue"),
        ("!clear", "Clear the queue"),
        ("!volume <0-100> / !vol", "Set or show the volume"),
        ("!help", "Show this help message"),
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    await ctx.send(embed=embed)


# ==================== SLASH COMMANDS ====================

@tree.command(name="join", description="Join your voice channel")
async def slash_join(interaction: discord.Interaction):
    """Slash command to join voice channel"""
    if not interaction.user.voice:
        await interaction.response.send_message("You need to be in a voice channel to use this command!", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    try:
        await music_player.join_voice_channel(channel)
        await interaction.response.send_message(f"Joined {channel.name}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to join voice channel: {e}", ephemeral=True)


@tree.command(name="leave", description="Leave the voice channel")
async def slash_leave(interaction: discord.Interaction):
    """Slash command to leave voice channel"""
    await music_player.leave_voice_channel()
    await interaction.response.send_message("Left the voice channel")


@tree.command(name="play", description="Play a song from YouTube or other sources")
async def slash_play(interaction: discord.Interaction, query: str):
    """Slash command to play music"""
    # Defer response IMMEDIATELY (must be within 3 seconds)
    try:
        await interaction.response.defer()
    except (discord.errors.NotFound, discord.errors.InteractionResponded):
        # Interaction already expired or responded to, just return
        return
    
    # Check voice channel after deferring
    if not interaction.user.voice:
        try:
            await interaction.followup.send("You need to be in a voice channel to use this command!", ephemeral=True)
        except:
            pass
        return
    
    # Join voice channel if not already connected
    if not music_player.voice_client or not music_player.voice_client.is_connected():
        channel = interaction.user.voice.channel
        await music_player.join_voice_channel(channel)
    
    try:
        # Extract video info
        info = get_video_info(query)
        
        if not info:
            await interaction.followup.send("❌ Could not find the requested song. Please try a different search term or URL.")
            return
        
        # Check if this song will start playing immediately (before adding to queue)
        will_play_now = not music_player.is_playing and music_player.voice_client and not music_player.voice_client.is_playing()
        
        # Add to queue
        await music_player.add_to_queue(info['url'], info['title'])
        
        # Format duration
        duration = info['duration']
        minutes, seconds = divmod(duration, 60)
        duration_str = f"{int(minutes)}:{int(seconds):02d}"
        
        embed = discord.Embed(
            title="🎵 Added to Queue" if not will_play_now else "🎵 Now Playing",
            description=f"**{info['title']}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Duration", value=duration_str, inline=True)
        if not will_play_now:
            embed.add_field(name="Position in Queue", value=len(music_player.queue), inline=True)
        
        if info['thumbnail']:
            embed.set_thumbnail(url=info['thumbnail'])
        
        # Always show control buttons when there's music (playing or queued)
        view = MusicPlayerControls()
        await view.update_buttons()
        
        msg = await interaction.followup.send(embed=embed, view=view)
        
        # Store control message reference
        view.control_message = msg
        
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {str(e)}")


@tree.command(name="pause", description="Pause the current song")
async def slash_pause(interaction: discord.Interaction):
    """Slash command to pause music"""
    if music_player.voice_client and music_player.voice_client.is_playing():
        music_player.pause()
        await interaction.response.send_message("⏸️ Paused")
    else:
        await interaction.response.send_message("Nothing is currently playing", ephemeral=True)


@tree.command(name="resume", description="Resume the paused song")
async def slash_resume(interaction: discord.Interaction):
    """Slash command to resume music"""
    if music_player.voice_client and music_player.voice_client.is_paused():
        music_player.resume()
        await interaction.response.send_message("▶️ Resumed")
    else:
        await interaction.response.send_message("Nothing is currently paused", ephemeral=True)


@tree.command(name="skip", description="Skip the current song")
async def slash_skip(interaction: discord.Interaction):
    """Slash command to skip music"""
    if music_player.voice_client and music_player.voice_client.is_playing():
        music_player.voice_client.stop()
        await interaction.response.send_message("⏭️ Skipped")
    else:
        await interaction.response.send_message("Nothing is currently playing", ephemeral=True)


@tree.command(name="queue", description="Show the current queue")
async def slash_queue(interaction: discord.Interaction):
    """Slash command to show queue"""
    if not music_player.current and len(music_player.queue) == 0:
        await interaction.response.send_message("The queue is empty", ephemeral=True)
        return
    
    embed = discord.Embed(title="📋 Music Queue", color=discord.Color.blue())
    
    if music_player.current:
        embed.add_field(
            name="🎵 Now Playing",
            value=music_player.current['title'],
            inline=False
        )
    
    if len(music_player.queue) > 0:
        queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(music_player.queue[:10])])
        if len(music_player.queue) > 10:
            queue_list += f"\n... and {len(music_player.queue) - 10} more"
        embed.add_field(name="Up Next", value=queue_list, inline=False)
    
    await interaction.response.send_message(embed=embed)


@tree.command(name="clear", description="Clear the queue")
async def slash_clear(interaction: discord.Interaction):
    """Slash command to clear queue"""
    music_player.queue.clear()
    await interaction.response.send_message("🗑️ Queue cleared")


@tree.command(name="volume", description="Set or show the volume")
async def slash_volume(interaction: discord.Interaction, volume: int = None):
    """Slash command to set volume"""
    if volume is None:
        if music_player.voice_client and music_player.voice_client.source:
            current_vol = int(music_player.voice_client.source.volume * 100)
            await interaction.response.send_message(f"Current volume: {current_vol}%", ephemeral=True)
        else:
            await interaction.response.send_message("No audio source is currently playing", ephemeral=True)
    else:
        if 0 <= volume <= 100:
            if music_player.voice_client and music_player.voice_client.source:
                music_player.voice_client.source.volume = volume / 100
                await interaction.response.send_message(f"🔊 Volume set to {volume}%")
            else:
                await interaction.response.send_message("No audio source is currently playing", ephemeral=True)
        else:
            await interaction.response.send_message("Volume must be between 0 and 100", ephemeral=True)


@tree.command(name="help", description="Show available commands")
async def slash_help(interaction: discord.Interaction):
    """Slash command to show help"""
    embed = discord.Embed(
        title="🎵 Music Bot Commands",
        description="Commands for the high-quality audio streaming bot\n\n**Use `/` for slash commands or `!` for prefix commands**",
        color=discord.Color.blue()
    )
    
    commands_list = [
        ("`/join` or `!join`", "Join your voice channel"),
        ("`/leave` or `!leave`", "Leave the voice channel"),
        ("`/play <song/url>` or `!play`", "Play a song from YouTube or other sources"),
        ("`/pause` or `!pause`", "Pause the current song"),
        ("`/resume` or `!resume`", "Resume the paused song"),
        ("`/skip` or `!skip`", "Skip the current song"),
        ("`/queue` or `!queue`", "Show the current queue"),
        ("`/clear` or `!clear`", "Clear the queue"),
        ("`/volume <0-100>` or `!volume`", "Set or show the volume"),
        ("`/help` or `!help`", "Show this help message"),
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument. Use `{PREFIX}help` for command usage.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")
        print(f"Error: {error}")


if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
    else:
        bot.run(TOKEN)

