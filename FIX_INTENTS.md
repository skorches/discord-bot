# Fix: Privileged Intents Required Error

## The Problem

Your bot is trying to use privileged intents that aren't enabled in the Discord Developer Portal.

## Solution: Enable Message Content Intent

### Step 1: Go to Discord Developer Portal

1. Visit: https://discord.com/developers/applications
2. Log in with your Discord account
3. Select your bot application

### Step 2: Enable Privileged Intents

1. Click **"Bot"** in the left sidebar
2. Scroll down to **"Privileged Gateway Intents"** section
3. Enable the following:
   - ✅ **MESSAGE CONTENT INTENT** (Required for prefix commands like `!play`)
   - ⚠️ **SERVER MEMBERS INTENT** (Optional - only if you need member info)

4. Click **"Save Changes"** at the bottom

### Step 3: Restart Your Bot

After enabling the intents:

```bash
docker-compose restart
```

Or:

```bash
docker-compose down
docker-compose up -d
```

### Step 4: Verify It Works

Check the logs:

```bash
docker-compose logs -f
```

You should now see:
```
BotName has connected to Discord!
Bot is in X guild(s)
Synced 10 slash command(s)
```

## Why This Is Needed

- **Message Content Intent**: Required for the bot to read message content for prefix commands (`!play`, `!pause`, etc.)
- **Voice States Intent**: Already enabled by default (not privileged)
- **Server Members Intent**: Optional, only needed for member-specific features

## Important Notes

- After enabling intents, it may take a few seconds for changes to propagate
- If your bot is in 100+ servers, you may need to verify your bot
- The bot will work with slash commands even without Message Content Intent, but prefix commands won't work

## Still Having Issues?

If you still see the error after enabling intents:

1. **Wait 1-2 minutes** - Changes can take time to propagate
2. **Verify intents are saved** - Go back to Developer Portal and confirm they're enabled
3. **Check bot permissions** - Make sure bot has proper permissions in your server
4. **Restart the container** - `docker-compose restart`





