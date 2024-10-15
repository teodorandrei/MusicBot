# Discord Music Bot

A simple music bot for Discord that allows users to play songs from YouTube directly in a voice channel. The bot supports a queue system for managing songs and features a GUI for logging, built with Tkinter.

## Features

- Play songs from YouTube
- Queue system to add songs for playback
- Graphical user interface for viewing logs
- Simple commands for controlling playback

## Technologies Used

- [Discord.py](https://discordpy.readthedocs.io/en/stable/) - Library for interacting with the Discord API
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video downloader that extracts audio
- [Tkinter](https://wiki.python.org/moin/TkInter) - Standard Python interface to the Tk GUI toolkit

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
2. Set up a virtual environment (optional but recommended):
   ```python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate` 
3. Install the required packages:
   ```pip install -r requirements.txt```

## Configuration
Before running the bot, you need to set your Discord bot token. Replace the placeholder in the code with your actual bot token.

## Usage 
1. Run the Bot
   ```python main.py```
2. Use the following commands in your Discord server:
   - ```play <YT URL/Song Name>```
   - ```stop```
   - ```skip```
