# Quick Setup Guide

## Step 1: Reset Your Token (IMPORTANT!)

Your token was exposed. Reset it first:

1. Go to: https://discord.com/developers/applications
2. Select your bot application
3. Click "Bot" in left sidebar
4. Click **"Reset Token"**
5. Click "Yes, do it!"
6. **Copy the NEW token immediately**

## Step 2: Create .env File

In the project root directory, create a file named `.env`:

```bash
# In the project root (/home/wars09/Cursor/discord-bot/)
nano .env
```

Add this content (replace with your NEW token):
```env
DISCORD_TOKEN=your_new_token_here
DISCORD_PREFIX=!
```

**Replace `your_new_token_here` with the NEW token from Step 1!**

Save and exit (Ctrl+X, then Y, then Enter in nano).

## Step 3: Run the Bot

### Option A: With Docker
```bash
docker-compose up -d
docker-compose logs -f
```

### Option B: Without Docker
```bash
pip install -r requirements.txt
python bot.py
```

## Step 4: Verify It Works

1. Check logs - you should see:
   ```
   BotName has connected to Discord!
   Synced 10 slash command(s)
   ```

2. In Discord, the bot should appear online

3. Try: `/help` or `!help` in a text channel

## Troubleshooting

**"Invalid token" error:**
- Make sure you used the NEW token (after reset)
- Check for extra spaces in `.env` file
- Verify the token is on one line

**"Token not found" error:**
- Make sure `.env` file is in the project root
- Check file is named exactly `.env` (not `.env.txt`)
- Verify `DISCORD_TOKEN=` is correct

## Remember

- ✅ `.env` file is gitignored (safe)
- ❌ Never share your token again
- ✅ Reset token if you accidentally share it

