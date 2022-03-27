# 'Gzuu' Discord Bot
Discord bot made for fun and learning! Can run polls, roll dice and play youtube links in voice channels. The name comes from a chaotic Lovecraftian god I introduced in a game of DnD played with my Discord server.

## Commands
### Polls
- `!poll topic "Your topic here"` Starts a new poll
- `!poll choice "Your choice here"` Adds a new choice to the poll
- `!poll end` Ends the poll
- `!poll status` Shows how many votes each choice has received
- `!poll vote choice_number` Cast your vote
### Youtube audio player
- `!join` Gzuu bot joins whatever voice channel you are in
- `!leave` Gzuu bot leaves the voice channel
- `!play youtubelink` Plays the audio from the YouTube link
- `!pause` Pauses audio
- `!resume` Resumes audio
- `!stop` Ends audio
### Misc
- `!roll number_of_dice sides_of_dice` Rolls x ammount of x sided dice
- `!test` Take some verbal abuse from Gzuu
- `!help` Lists commands

## Notes
ffmpeg.exe must be in base dir! https://ffmpeg.org/

## Libraries
- [Discord.py](https://discordpy.readthedocs.io/en/latest/index.html)
- [Youtube_DL](https://github.com/ytdl-org/youtube-dl)
