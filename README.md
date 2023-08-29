# Acid Music Bot

This is a Discord music bot written in Python using the Discord.py library. The bot is capable of playing songs from YouTube and Spotify, as well as handling basic playback controls.

## Features

- Connects to a voice channel in a Discord server.
- Disconnects from the voice channel.
- Plays songs from YouTube and Spotify.
- Stops the currently playing song.
- Pauses and resumes the playback.
- Skips the current song.
- Shows the current song queue.

## Setup

1. Clone the repository or download the code files.
2. Install the required dependencies by running the following command:
3. pip install -r requirements.txt
4. You can create a bot and obtain a token from the Discord Developer Portal.
5. Make sure you have FFmpeg installed on your system. FFmpeg is required for audio streaming and can be downloaded from the official website: https://ffmpeg.org/download.html
6. Run the bot by executing the following command: `python bot.py`

## Usage

The bot uses slash commands instead of prefix for commands. Here are the available commands:

- `/connect` - Connects the bot to a voice channel.
- `/disconnect` - Disconnects the bot from the voice channel.
- `/play [link]` - Plays a song or playlist from YouTube or Spotify.
- `/stop` - Stops the currently playing song.
- `/pause` - Pauses the currently playing song.
- `/resume` - Resumes the paused song.
- `/skip` - Skips the current song.
- `/queue` - Shows the current song queue.
- `/help` - Displays the help message with a list of available commands.

## Contributing

Contributions to the project are welcome. If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
