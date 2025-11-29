# How to Engage with the Discord Music Bot

This guide explains step-by-step how to interact with the bot and what happens behind the scenes.

## Quick Start Workflow

### 1. **Start the Bot**
   - Run `python bot.py` on your server/computer
   - The bot will connect to Discord and appear online in your server
   - You'll see a status message: "Listening to !help"

### 2. **Join a Voice Channel**
   - You (the user) must first join a Discord voice channel
   - Then type in any text channel: `!join` or `!j`
   - **What happens:**
     - Bot checks if you're in a voice channel
     - Bot joins the same voice channel you're in
     - Bot sends confirmation: "Joined [Channel Name]"

### 3. **Play Music**
   - Type: `!play <song name or YouTube URL>`
   - Examples:
     - `!play Never Gonna Give You Up`
     - `!play https://www.youtube.com/watch?v=dQw4w9WgXcQ`
     - `!p Bohemian Rhapsody`
   
   **What happens behind the scenes:**
   1. Bot checks if you're in a voice channel
   2. If bot isn't connected, it automatically joins your channel
   3. Bot sends: "🔍 Searching for the song..."
   4. Bot uses yt-dlp to search YouTube or extract from URL
   5. Bot finds the best quality audio stream (192kbps Opus)
   6. Bot adds the song to the queue
   7. Bot displays an embed with:
      - Song title
      - Duration
      - Position in queue
      - Thumbnail image
   8. If no song is playing, it starts immediately
   9. Audio streams directly to Discord (no downloading!)

### 4. **Control Playback**
   - `!pause` - Pauses the current song
   - `!resume` or `!r` - Resumes playback
   - `!skip` or `!s` - Skips to next song in queue
   - `!volume 50` or `!vol 75` - Sets volume (0-100%)

### 5. **Manage Queue**
   - `!queue` or `!q` - Shows what's playing and what's next
   - `!play <another song>` - Adds more songs to queue
   - `!clear` - Clears all queued songs

### 6. **Leave**
   - `!leave` or `!dc` - Bot leaves voice channel and clears queue

## Detailed Interaction Examples

### Example 1: First Time Using the Bot

```
You: !join
Bot: Joined General

You: !play Rick Astley Never Gonna Give You Up
Bot: 🔍 Searching for the song...
Bot: [Embed] 🎵 Added to Queue
      **Rick Astley - Never Gonna Give You Up**
      Duration: 3:33
      Position in Queue: 1
      [Thumbnail image]

[Music starts playing in voice channel]
```

### Example 2: Building a Queue

```
You: !play Bohemian Rhapsody
Bot: [Embed] Added to Queue - Position: 1
[Song 1 starts playing]

You: !play Hotel California
Bot: [Embed] Added to Queue - Position: 2
[Song 1 continues, Song 2 queued]

You: !play Stairway to Heaven
Bot: [Embed] Added to Queue - Position: 3
[Song 1 continues, Songs 2 & 3 queued]

You: !queue
Bot: [Embed] 📋 Music Queue
      🎵 Now Playing: Bohemian Rhapsody
      Up Next:
      1. Hotel California
      2. Stairway to Heaven
```

### Example 3: Playback Controls

```
[Music is playing]

You: !pause
Bot: ⏸️ Paused
[Music stops]

You: !resume
Bot: ▶️ Resumed
[Music continues]

You: !volume 60
Bot: 🔊 Volume set to 60%

You: !skip
Bot: ⏭️ Skipped
[Next song in queue starts]
```

### Example 4: Using YouTube URLs

```
You: !play https://www.youtube.com/watch?v=dQw4w9WgXcQ
Bot: [Embed] 🎵 Added to Queue
      **Rick Astley - Never Gonna Give You Up (Official Video)**
      Duration: 3:33
      Position in Queue: 1
```

## How the Bot Processes Audio

### Audio Quality Pipeline:

1. **Search/Extract** (yt-dlp)
   - Searches YouTube or extracts from URL
   - Finds best available audio format
   - Gets direct streaming URL (no download)

2. **Stream Processing** (FFmpeg)
   - Receives audio stream from source
   - Converts to Opus codec (Discord's preferred format)
   - Applies quality settings:
     - Bitrate: 192kbps
     - Sample Rate: 48kHz
   - Handles reconnection if stream drops

3. **Discord Streaming**
   - Sends processed audio to Discord
   - Streams in real-time (low latency)
   - Maintains high quality throughout

### Queue System:

- **First song**: Plays immediately when added
- **Subsequent songs**: Added to queue, play automatically when current song ends
- **Auto-advance**: When a song finishes, next in queue starts automatically
- **Skip**: Immediately jumps to next song

## Error Handling

The bot handles common issues gracefully:

### "You need to be in a voice channel!"
- **Cause**: You're not in a voice channel
- **Solution**: Join a voice channel first, then use commands

### "Could not find the requested song"
- **Cause**: Search didn't find results or URL is invalid
- **Solution**: Try a different search term or check the URL

### "Failed to join voice channel"
- **Cause**: Bot lacks permissions or channel is full
- **Solution**: Check bot permissions (Connect, Speak) and channel capacity

### "Nothing is currently playing"
- **Cause**: No song is active
- **Solution**: Use `!play` to start music

## Tips for Best Experience

1. **Join voice channel first**: Always join before using `!play` (though `!play` will auto-join)
2. **Use specific searches**: More specific song names = better results
3. **Queue multiple songs**: Build a playlist before starting
4. **Check queue**: Use `!queue` to see what's coming up
5. **Adjust volume**: Default is 100%, lower if too loud
6. **Use aliases**: `!p` instead of `!play`, `!s` instead of `!skip`, etc.

## Command Reference

| Command | Aliases | Description |
|---------|---------|-------------|
| `!join` | `!j`, `!connect` | Join your voice channel |
| `!play <song>` | `!p` | Play a song (URL or search) |
| `!pause` | - | Pause current song |
| `!resume` | `!r` | Resume paused song |
| `!skip` | `!s`, `!next` | Skip to next song |
| `!queue` | `!q` | Show current queue |
| `!clear` | - | Clear the queue |
| `!volume <0-100>` | `!vol` | Set volume |
| `!leave` | `!dc`, `!disconnect` | Leave voice channel |
| `!help` | - | Show all commands |

## Behind the Scenes: Technical Flow

```
User Command → Bot Receives → Validation → Action → Response

Example: !play song
1. User types: !play Never Gonna Give You Up
2. Bot receives command in text channel
3. Bot validates: Is user in voice channel? ✓
4. Bot checks: Is bot in voice channel? If not, join
5. Bot searches YouTube via yt-dlp
6. Bot extracts best audio URL
7. Bot adds to queue
8. Bot starts streaming if queue was empty
9. Bot sends embed confirmation
10. Audio streams to Discord voice channel
```

The entire process is optimized for **high-quality, low-latency streaming** without downloading files to disk!


