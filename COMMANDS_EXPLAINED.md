# Discord Bot Commands - Explained

## How Commands Work

The bot comes with **two ways to interact** - you don't need to create any commands yourself! Discord and the bot handle everything automatically.

## 1. Slash Commands (Modern & Recommended)

**What are they?**
- Discord's modern command system
- Appear in Discord's autocomplete menu when you type `/`
- More user-friendly with built-in help text
- Automatically registered by the bot

**How to use:**
1. Type `/` in any text channel
2. Discord shows a menu with all available commands
3. Select a command and fill in the parameters
4. Press Enter

**Example:**
```
You type: /
Discord shows: [Menu with /join, /play, /pause, etc.]
You select: /play
Discord shows: [Text box for "query"]
You type: Never Gonna Give You Up
You press: Enter
Bot responds: [Song added to queue]
```

**All Slash Commands:**
- `/join` - Join your voice channel
- `/play <query>` - Play a song (YouTube URL or search)
- `/pause` - Pause current song
- `/resume` - Resume paused song
- `/skip` - Skip to next song
- `/queue` - Show current queue
- `/clear` - Clear the queue
- `/volume <0-100>` - Set volume
- `/leave` - Leave voice channel
- `/help` - Show help message

## 2. Prefix Commands (Traditional)

**What are they?**
- Traditional text-based commands
- Type commands directly in chat
- Start with `!` (or your custom prefix)
- Work like old-school IRC commands

**How to use:**
1. Type `!` followed by the command name
2. Add any parameters after the command
3. Press Enter

**Example:**
```
You type: !play Never Gonna Give You Up
You press: Enter
Bot responds: [Song added to queue]
```

**All Prefix Commands:**
- `!join` or `!j` - Join your voice channel
- `!play <song/url>` or `!p` - Play a song
- `!pause` - Pause current song
- `!resume` or `!r` - Resume paused song
- `!skip` or `!s` - Skip to next song
- `!queue` or `!q` - Show current queue
- `!clear` - Clear the queue
- `!volume <0-100>` or `!vol` - Set volume
- `!leave` or `!dc` - Leave voice channel
- `!help` - Show help message

## Do You Need to Create Commands?

**No!** The bot comes with all commands pre-built. Here's what happens:

### When You Start the Bot:
1. Bot connects to Discord
2. Bot automatically registers all slash commands with Discord
3. Commands appear in Discord's command menu within a few seconds
4. Both slash and prefix commands are ready to use immediately

### What Discord Does:
- **Slash Commands**: Discord automatically shows them in the `/` menu
- **Prefix Commands**: Work immediately when you type them

### What You Need to Do:
1. **Nothing!** Just invite the bot and start using commands
2. Make sure when inviting the bot, you select the `applications.commands` scope (this allows slash commands)

## Command Registration Process

When the bot starts, you'll see in the console:
```
BotName has connected to Discord!
Bot is in X guild(s)
Synced 10 slash command(s)
```

This means:
- ✅ Bot is online
- ✅ Slash commands are registered with Discord
- ✅ All commands are ready to use

## Troubleshooting Commands

### Slash commands don't appear:
1. **Wait a few seconds** - Commands can take up to 1 hour to appear globally (or instantly for your server)
2. **Check bot invite** - Make sure you selected `applications.commands` scope when inviting
3. **Restart the bot** - Commands sync when the bot starts
4. **Check console** - Look for "Synced X slash command(s)" message

### Prefix commands don't work:
1. **Check prefix** - Default is `!`, but you can change it in `.env` file
2. **Bot permissions** - Bot needs "Read Messages" permission
3. **Bot is online** - Make sure the bot is running

### Both command types work:
- Slash commands: Type `/` and select from menu
- Prefix commands: Type `!command` in chat
- They do the same thing - use whichever you prefer!

## Summary

- ✅ **Commands are built-in** - No need to create them
- ✅ **Slash commands auto-register** - Just start the bot
- ✅ **Prefix commands work immediately** - Type `!command`
- ✅ **Both work the same way** - Choose your preference
- ✅ **Discord handles the UI** - For slash commands, Discord shows the menu

You just need to:
1. Start the bot
2. Use the commands (either `/` or `!`)
3. Enjoy the music!

