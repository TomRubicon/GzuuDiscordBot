import os

import random
from datetime import datetime

import discord
from dotenv import load_dotenv

load_dotenv(verbose=True)

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    
    print(f'{client.user} has connected to Discord in Guild: {guild.name} GID: {guild.id}')

    members = '\n - '.join([member.display_name for member in guild.members])
    print(f'Guild Members: \n - {members}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    help_text = ''.join(('```Command list \n',
                        '-----------------------------\n',
                        '!test - Extremely useful```'))

    replies = ['Huh?',
                'I\'m going to need you to speak louder!',
                'Oh. Yeah I have no idea how to read.'
    ]

    if message.content == '!help':
        await message.channel.send(help_text)
    elif message.content == '!test':
        response = random.choice(replies)
        await message.channel.send(response)
    elif message.content == '!raise-exception':
        raise discord.DiscordException

@client.event
async def on_error(event, *args, **kwargs):
    now = datetime.now()
    with open('error.log', 'a') as f:
        if event == 'on_message':
            f.write(f'<{now}> Unhandled message: {args[0]}\n')
        else:
            raise


client.run(TOKEN)