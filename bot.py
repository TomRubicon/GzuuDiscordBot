import os

import random
from datetime import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv

import asyncio

load_dotenv(verbose=True)

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

#global vars
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

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    
    print(f'{bot.user.name} has connected to Discord in Guild: {guild.name} GID: {guild.id}')

    members = '\n - '.join([member.display_name for member in guild.members])
    print(f'Guild Members: \n - {members}')

@bot.command(name='test', help='Gzuu bot will give you a very thoughtful response.')
async def test_command(ctx):
    replies = ['Huh?',
                'I\'m going to need you to speak louder!',
                'Oh. Yeah I have no idea how to read.'
    ]

    response = random.choice(replies)
    await ctx.send(response)

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

#Likely a terrible way to do this but lets gooooooo
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
            await ctx.send(f'A new poll named "**{poll_topic}**" has been created by **{poll_nick}({poll_owner})** for the channel: **{poll_channel}**\n The creator of the poll can end it with **"!poll end"**!')
        else:
            await ctx.send(f'A poll is already active, started by **{poll_nick}**!\nTopic is: "**{poll_topic}**"')

    elif subcommand == 'choice':
        if poll_active:
            if ctx.author.name == poll_owner:
                poll_choices.append(arg)
                poll_votes.append(0)
                await ctx.send(f'Added poll option: "**{arg}**"')
            else:
                await ctx.send(f'You are no the author of this poll! Only **{poll_nick}({poll_owner})** can add choices!')
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

    elif subcommand == 'clear':
        role = discord.utils.find(lambda r: r.name == '@Admin', ctx.guild.roles)
        if role in ctx.author.roles:
            clear_poll()
            await ctx.send('Clearing poll!')
        else:
            await ctx.send('Only admins can clear polls!')

@bot.event
async def on_error(event, *args, **kwargs):
    now = datetime.now()
    with open('error.log', 'a') as f:
        if event == 'on_message':
            f.write(f'<{now}> Unhandled message: {args[0]}\n')
        else:
            raise # type: ignore

bot.run(TOKEN)