# Discord Bot Setup Guide

## Getting Started

Follow these steps to get your Discord bot up and running.

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create Your Discord Bot

1. Navigate to the [Discord Developer Portal](https://discord.com/developers/docs/intro)
2. Click on **"New Application"** to create a new bot
3. Go to the **Bot** section in the left sidebar
4. Click **"Add Bot"** to create your bot
5. Under the **Token** section, click **"Reset Token"** to generate a new bot token
6. **Copy this token** - you'll need it in the next step

> ⚠️ **Important:** Keep your bot token secret! Never share it or commit it to version control.

### 3. Configure Environment Variables

Create a `.env` file in the root directory of the project:

```bash
touch .env
```

Add your bot token to the `.env` file:

```
DISCORD_BOT_TOKEN=your_bot_token_here
```

Replace `your_bot_token_here` with the token you copied in step 2.

### 4. Run the Bot

Execute the following command to start your bot:

```bash
npm start
```

or

```bash
node index.js
```

---

**That's it!** Your Discord bot should now be running. Check your console for confirmation messages.
