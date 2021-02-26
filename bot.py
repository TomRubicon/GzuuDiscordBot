import os

import random
from datetime import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(verbose=True)

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

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

@bot.event
async def on_error(event, *args, **kwargs):
    now = datetime.now()
    with open('error.log', 'a') as f:
        if event == 'on_message':
            f.write(f'<{now}> Unhandled message: {args[0]}\n')
        else:
            raise # type: ignore

bot.run(TOKEN)