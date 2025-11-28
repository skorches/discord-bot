# Discord Music Bot - High Quality Audio Streaming

A Discord bot that streams high-quality audio from YouTube and other sources to Discord voice channels.

## Features

- 🎵 High-quality audio streaming (192kbps Opus, 48kHz sample rate)
- 📋 Queue management system
- 🎮 Play, pause, resume, skip controls
- 🔊 Volume control
- 🔍 Supports YouTube URLs and search queries
- 🎨 Beautiful embed messages

## Prerequisites

1. **Python 3.8+** - Make sure Python is installed
2. **FFmpeg** - Required for audio processing
   - **Linux**: `sudo apt-get install ffmpeg` (Debian/Ubuntu) or `sudo pacman -S ffmpeg` (Arch)
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH
3. **Discord Bot Token** - Create a bot at [Discord Developer Portal](https://discord.com/developers/applications)

## Installation

### Option 1: Docker (Recommended for Production)

1. **Install Docker** ([Get Docker](https://docs.docker.com/get-docker/))

2. **Create a `.env` file** in the project root:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   DISCORD_PREFIX=!
   ```

3. **Get your Discord Bot Token** (see [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed instructions):
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application → Go to "Bot" section
   - Click "Add Bot" → Copy the token
   - Enable "Message Content Intent" under Privileged Gateway Intents

4. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

5. **View logs**:
   ```bash
   docker-compose logs -f
   ```

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for complete Docker setup guide.

### Option 2: Local Python Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**:
   - **Linux**: `sudo apt-get install ffmpeg` (Debian/Ubuntu) or `sudo pacman -S ffmpeg` (Arch)
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH

4. **Create a `.env` file** in the project root:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   DISCORD_PREFIX=!
   ```

5. **Get your Discord Bot Token**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" section
   - Click "Add Bot"
   - Copy the token and paste it in your `.env` file
   - Enable the following Privileged Gateway Intents:
     - Message Content Intent
     - Server Members Intent (if needed)

6. **Invite your bot to your server**:
   - In the Developer Portal, go to "OAuth2" > "URL Generator"
   - Select scopes: `bot` and `applications.commands`
   - Select bot permissions: `Connect`, `Speak`, `Use Voice Activity`
   - Copy the generated URL and open it in your browser
   - Select your server and authorize

## Usage

### With Docker:
```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Without Docker:
1. **Start the bot**:
   ```bash
   python bot.py
   ```

2. **Commands**:

   The bot supports **two types of commands**:
   
   **Slash Commands** (Recommended - Modern Discord feature):
   - Type `/` in Discord and the bot's commands will appear in the autocomplete menu
   - `/join` - Join your voice channel
   - `/play <song/url>` - Play a song (supports YouTube URLs or search queries)
   - `/pause` - Pause the current song
   - `/resume` - Resume the paused song
   - `/skip` - Skip the current song
   - `/queue` - Show the current queue
   - `/clear` - Clear the queue
   - `/volume <0-100>` - Set the volume
   - `/leave` - Leave the voice channel
   - `/help` - Show all commands
   
   **Prefix Commands** (Traditional - Type in chat):
   - `!join` or `!j` - Join your voice channel
   - `!play <song/url>` or `!p` - Play a song (supports YouTube URLs or search queries)
   - `!pause` - Pause the current song
   - `!resume` or `!r` - Resume the paused song
   - `!skip` or `!s` - Skip the current song
   - `!queue` or `!q` - Show the current queue
   - `!clear` - Clear the queue
   - `!volume <0-100>` or `!vol` - Set the volume
   - `!leave` or `!dc` - Leave the voice channel
   - `!help` - Show all commands
   
   **Note**: Slash commands are automatically registered when the bot starts. You don't need to create them manually - they're built into the bot!

## Example Usage

**Using Slash Commands** (Type `/` and select from menu):
```
/join
/play query:Never Gonna Give You Up
/play query:https://www.youtube.com/watch?v=dQw4w9WgXcQ
/pause
/resume
/skip
/volume volume:50
/queue
```

**Using Prefix Commands** (Type `!` commands in chat):
```
!join
!play Never Gonna Give You Up
!play https://www.youtube.com/watch?v=dQw4w9WgXcQ
!pause
!resume
!skip
!volume 50
!queue
```

Both command types work identically - use whichever you prefer!

## Audio Quality Settings

The bot is configured for high-quality audio streaming:
- **Codec**: Opus
- **Bitrate**: 192kbps
- **Sample Rate**: 48kHz
- **Format**: Best available audio from source

These settings can be adjusted in the `YDL_OPTIONS` and `FFMPEG_OPTIONS` dictionaries in `bot.py`.

## Troubleshooting

### Bot doesn't join voice channel
- Make sure you're in a voice channel when using `!join`
- Check that the bot has "Connect" and "Speak" permissions

### No audio plays
- Verify FFmpeg is installed: `ffmpeg -version`
- Check that your bot has proper permissions in the voice channel
- Ensure your Discord client has audio enabled

### "Command not found" errors
- Make sure the bot is running and connected
- Check that you're using the correct prefix (default: `!`)
- Verify the bot has "Read Message History" permission

### Audio quality issues
- The bot streams at 192kbps by default, which is high quality
- You can adjust the bitrate in `FFMPEG_OPTIONS` in `bot.py`
- Higher bitrates require more bandwidth

## Dependencies

- `discord.py[voice]` - Discord API wrapper with voice support
- `yt-dlp` - YouTube and other site audio extraction
- `python-dotenv` - Environment variable management
- `PyNaCl` - Voice encryption library

## License

This project is open source and available for modification and distribution.

## Notes

- The bot requires an active internet connection to stream audio
- Some YouTube videos may be restricted or unavailable
- The bot uses yt-dlp which supports many video/audio sources beyond YouTube
- Make sure to keep your bot token secret and never commit it to version control

