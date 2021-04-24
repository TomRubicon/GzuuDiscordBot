import os
import random
import youtube_dl
import asyncio
import discord

from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(verbose=True)

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

#poll class
class Poll:
    def clear(self):
        self.active = False
        self.owner = ''
        self.nick = ''
        self.topic = ''
        self.choices = []
        self.votes = []
        self.voters = []
        self.channel = ''
        return

    def __init__(self):
        self.clear()

poll = {}

#Youtube DL set up
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format' : 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""
    
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        length = data['duration']
        return filename, length

#Globals for song queues
queue = []
is_playing = False;

#Start him up!
@bot.event
async def on_ready():
    global poll

    guild = discord.utils.get(bot.guilds, name=GUILD)
    
    print(f'{bot.user.name} has connected to Discord in Guild: {guild.name} GID: {guild.id}')

    for member in guild.members:
        poll[member.name] = Poll()
        print(f'Poll object created for {member.name}')

    members = '\n - '.join([member.display_name for member in guild.members])
    print(f'Guild Members: \n - {members}')

#Just a fun little test command
@bot.command(name='test', help='Gzuu bot will give you a very thoughtful response.')
async def test_command(ctx):
    replies = ['Huh?',
                'I\'m going to need you to speak louder!',
                'Oh. Yeah I have no idea how to read.'
    ]

    response = random.choice(replies)
    await ctx.send(response)

#Dice roll!
@bot.command(name='roll', help='Roll some dice! !roll number_of_dice sides')
async def dice_roll(ctx, number: int, sides: int):
    if number > 100:
        await ctx.send('Look, I like you, but I am not rolling more than 100 fucking dice.')
        return   
    if sides > 1000:
        await ctx.send(f'*stares at {sides} sided dice in extreme confusion*')
        await ctx.send('The most sides I can handle is 1000.')
        return

    dice = [
        str(random.choice(range(1, sides + 1)))
        for _ in range(number)
    ]
    total = 0

    for roll in dice:
        total += int(roll)

    result = 'Roll that shit!\n' + ', '.join(dice) + '\nTotal: ' + str(total)
    await ctx.send(result)

async def start_poll():

    return

#Poll system commands. Likely a terrible way to do this but lets gooooooo
@bot.command(name='poll', help='Start a new poll for the server to vote on')
async def poll_(ctx, subcommand: str, *args):
    global poll
    user = ctx.author.name
    nick = ctx.author.display_name
    no_poll = 'You have not started a poll!'
    response = ''

    if subcommand == 'topic':
        if not poll[user].active:
            poll[user].active = True
            poll[user].topic = args[0]
            print(f'New poll named {poll[user].topic} created by {user}')
            poll[user].owner = user
            poll[user].nick = nick
            poll[user].channel = ctx.channel
            
            response += f'A new poll named **{poll[user].topic}**' 
            response += f' has been created by **{poll[user].nick}({poll[user].owner})**'
            response += f'for the channel: **{poll[user].channel}**\n'
            response += f'To add choices to vote on: `!poll choice "your choice here"`\n'
            response += f'To end the poll: `!poll end`\nSee options and current votes: `!poll status`\n'
            response += f'To vote: `!poll vote {poll[user].owner} choice_number`'

            await ctx.send(response)
        else:
            await ctx.send(f'You are already running a poll!')

    elif subcommand == 'choice':
        if poll[user].active:
            poll[user].choices.append(args[0])
            poll[user].votes.append(0)
            await ctx.send(f'Added poll choice: "**{args[0]}**"')
        else:
            await ctx.send(no_poll)
    
    elif subcommand == 'status':
        if poll[user].active:
            response = f'Poll topic: "{poll[user].topic}"\n- Choices: ```'
            if len(poll[user].choices) > 0:
                for choice in poll[user].choices:
                    position = poll[user].choices.index(choice) + 1
                    votes = poll[user].votes[poll[user].choices.index(choice)]
                    response += f'-- {position}: {choice} - Votes: {votes}\n'
            else:
                response += 'There are no poll choices yet!\nAdd some with !poll choice "Your choice here"'
            response += '```'
            response += f'To vote: `!poll vote {poll[user].owner} choice_number`'
            await ctx.send(response)
        else:
            await ctx.send(no_poll)
    
    elif subcommand == 'vote':
        if args[0] not in poll:
            await ctx.send(f'User {args[0]} does not exist')
            return
        
        p = args[0]

        if poll[p].active:
            if user in poll[p].voters:
                await ctx.send('You already voted! Settle down.')
                return
            else:
                arg = int(args[1])
                try:
                    int(arg)
                except ValueError:
                    await ctx.send('Choice must be a number!')
                    return
                
                if arg == 0 or arg > len(poll[p].choices):
                    await ctx.send('Please vote for a valid choice number!')
                else:
                    poll[p].votes[arg - 1] += 1
                    poll[p].voters.append(ctx.author.name)
                    await ctx.send(f'{ctx.author.display_name} just voted for "{poll[p].choices[arg - 1]}"')            
        else:
            await ctx.send('This user has not started a poll!')

    elif subcommand == 'end':
        if poll[user].active:
            poll_dict = dict(zip(poll[user].choices, poll[user].votes))
            poll_dict = sorted(poll_dict.items(), key=lambda x: x[1], reverse=True)
        
            results = f'**--The results for the poll "{poll[user].topic}" are in!--**\n\nThe winner is: '
            
            for k, v in poll_dict:
                results += f'**{k}** - Votes: **{v}**\n'

            results += "\nThe following users voted on this poll: \n"

            for u in poll[user].voters:
                results += f'-{u}'

            poll[user].clear()
            await ctx.send(results)
        else:
            await ctx.send(no_poll)
    
    elif subcommand == 'list':
        for p in poll:
            if poll[p].active:
                response += f'**{poll[p].topic}** by **{poll[p].owner}**\n'
                if len(poll[p].choices) > 0:
                    for choice in poll[p].choices:
                        position = poll[p].choices.index(choice) + 1
                        votes = poll[p].votes[poll[p].choices.index(choice)]
                        response += f'-- {position}: {choice} - Votes: {votes}\n'
                    response += f'To vote: `!poll vote {poll[p].owner} choice_number`'
                else:
                    response += '*No choices for this poll*\n'
                response += '\n'

        if response == '':
            response = 'No polls are active!'
        await ctx.send(response)
                
#Youtube music player commands
@bot.command(name='join', help='Makes Gzuu join the voice channel you are currently active in')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f'{ctx.message.author.name} is not connected to a voice channel!')
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='Make Gzuu leave current voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send('I\'m not in a voice channel!')

# @bot.command(name='queue', help='Lists the songs currently in queue')
# async def queue(ctx):
#     pass



@bot.command(name='play', help='If Gzuu is connected to a voice channel play a youtube audio in that channel')
async def play(ctx, url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_client = ctx.message.guild.voice_client

        if voice_client and voice_client.is_playing():
            await ctx.send('I am already playing a song! use !stop to end the current song.')
        else:
            async with ctx.typing():
                filename, length = await YTDLSource.from_url(url, loop=bot.loop)
            print(filename)
            print(length)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
            await ctx.send(f'**NOW PLAYING:** {filename}')

    except:
        await ctx.send('I\'m not connected to a voice channel!')

@bot.command(name='pause', help='Pauses the current song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send('I\'m not currently playing a song!')

@bot.command(name='resume', help='Resume playing current song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send('I\'m not currently playing a song!')

@bot.command(name='stop', help='Stops playing the current song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send('I\'m not currently playinga  song!')

#Error handling events
@bot.event
async def on_error(event, *args, **kwargs):
    now = datetime.now()
    with open('error.log', 'a') as f:
        if event == 'on_message':
            f.write(f'<{now}> Unhandled message: {args[0]}\n')
        else:
            raise # type: ignore

bot.run(TOKEN)