import os

import random
from datetime import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv

import youtube_dl
import asyncio

load_dotenv(verbose=True)

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

#global vars for poll command
poll_active = False
poll_owner = ''
poll_nick = ''
poll_topic = ''
poll_choices = []
poll_votes = []
poll_voters = []
poll_channel = ''

def clear_poll():
    global poll_active, poll_owner, poll_nick, poll_topic, poll_choices, poll_votes, poll_voters, poll_channel
    poll_active = False
    poll_owner = ''
    poll_nick = ''
    poll_topic = ''
    poll_choices = []
    poll_votes = []
    poll_voters = []
    poll_channel = ''

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
        return filename

#Start him up!
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    
    print(f'{bot.user.name} has connected to Discord in Guild: {guild.name} GID: {guild.id}')

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
async def poll(ctx, subcommand: str, arg = ''):
    global poll_active, poll_owner, poll_nick, poll_topic, poll_choices, poll_votes, poll_voters, poll_channel
    no_poll = 'There is no active poll!'

    if subcommand == 'topic':
        if not poll_active:
            poll_active = True
            poll_topic = arg
            print(f'New poll named {poll_topic}')
            poll_owner = ctx.author.name
            poll_nick = ctx.author.display_name
            poll_channel = ctx.channel
            await ctx.send(f'A new poll named "**{poll_topic}**" has been created by **{poll_nick}({poll_owner})** for the channel: **{poll_channel}**\nTo add choices to vote on **"!poll choice "your choice here""**\nThe creator of the poll can end it with **"!poll end"**!\nUse **"!poll status"** to see voting options. Vote by typing **"!poll vote option_number"**')
        else:
            await ctx.send(f'A poll is already active, started by **{poll_nick}**!\nTopic is: "**{poll_topic}**"')

    elif subcommand == 'choice':
        if poll_active:
            if ctx.author.name == poll_owner:
                poll_choices.append(arg)
                poll_votes.append(0)
                await ctx.send(f'Added poll option: "**{arg}**"')
            else:
                await ctx.send(f'You are not the author of this poll! Only **{poll_nick}({poll_owner})** can add choices!')
        else:
            await ctx.send(no_poll)

    elif subcommand == 'status':
        if poll_active:
            response = f'Poll topic: "{poll_topic}"\n- Choices: ```'
            for choice in poll_choices:
                position = poll_choices.index(choice) + 1
                votes = poll_votes[poll_choices.index(choice)]
                response += f'-- {position}: {choice} - Votes: {votes}\n'
            response += '```'
            await ctx.send(response)
        else:
            await ctx.send(no_poll)
    
    elif subcommand == 'vote':
        if poll_active:
            if ctx.author.name in poll_voters:
                await ctx.send('You already voted! Settle down.')
                return
            else:
                arg = int(arg)
                try:
                    int(arg)
                except ValueError:
                    await ctx.send('Choice must be a number!')
                    return
                
                if arg == 0 or arg > len(poll_choices):
                    await ctx.send('Please vote for a valid choice number!')
                else:
                    poll_votes[arg - 1] += 1
                    poll_voters.append(ctx.author.name)
                    await ctx.send(f'{ctx.author.display_name} just voted for "{poll_choices[arg - 1]}"')            
        else:
            await ctx.send(no_poll)

    elif subcommand == 'end':
        if poll_active:
            if ctx.author.name == poll_owner:
                poll_dict = dict(zip(poll_choices, poll_votes))
                poll_dict = sorted(poll_dict.items(), key=lambda x: x[1], reverse=True)
            
                results = f'**--The results for the poll "{poll_topic}" are in!--**\n\nThe winner is: '
                
                for k, v in poll_dict:
                    results += f'**{k}** - Votes: **{v}**\n'

                results += "\nThe following users voted on this poll: \n"

                for u in poll_voters:
                    results += f'-{u}'

                clear_poll()
                await ctx.send(results)
            else:
                await ctx.send(f'You are not the author of this poll! Only **{poll_nick}({poll_owner})** can end the poll!')
        else:
            await ctx.send(no_poll)

    elif subcommand == 'clear':
        role = discord.utils.find(lambda r: r.name == '@Admin', ctx.guild.roles)
        if role in ctx.author.roles:
            clear_poll()
            await ctx.send('Clearing poll!')
        else:
            await ctx.send('Only admins can clear polls!')

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
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send('I\'m not in a voice channel!')

@bot.command(name='play', help='If Gzuu is connected to a voice channel play a youtube audio in that channel')
async def play(ctx, url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)

        voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))

        await ctx.send(f'**NOW PLAYING:** {filename}')
    except:
        await ctx.send('I\'m not connected to a voice channel!')

@bot.command(name='pause', help='Pauses the current song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send('I\'m not currently playing a song!')

@bot.command(name='resume', help='Resume playing current song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send('I\'m not currently playing a song!')

@bot.command(name='stop', help='Stops playing the current song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
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