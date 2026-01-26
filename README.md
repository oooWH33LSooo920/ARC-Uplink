# ARC-Uplink Discord Bot

ARC-Uplink is a Discord bot for managing live events, weekly trials, expeditions, quests, and more. Designed for easy channel setup and automated updates, especially for ARC Raiders communities.

## Features

- Set channels for updates using **slash commands only** (`/setliveevents`, `/setweeklytrials`, `/setexpedition`, `/set_quest`)
- Unlink channels (`/unlink_channel`)
- Custom help command
- Owner-only self-update command (`!selfupdate`)

> **Note:** Set channel commands are available as slash commands (/) only. Prefix commands with ! are not supported for these actions.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/oooWH33LSooo920/ARC-Uplink.git
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Discord bot token:
   ```
   DISCORD_TOKEN=your_token_here
   ```
4. Run the bot:
   ```
   python bot.py
   ```

## License

MIT License

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

For questions or support, contact oooWH33LSooo920 on GitHub.
