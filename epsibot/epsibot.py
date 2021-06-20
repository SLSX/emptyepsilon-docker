#! /usr/bin/env python3

from datetime import datetime
from subprocess import Popen, TimeoutExpired
from discord.ext.commands import Bot
from emptyepsilon import EmptyEpsilon
import discord
import requests
import os


DISCORD_API_TOKEN = os.getenv('DISCORD_API_TOKEN')
DISCORD_BOT_OWNER = int(os.getenv('DISCORD_BOT_OWNER') or -1)
PRIVILEGED_ROLE = os.getenv('PRIVILEGED_ROLE')
EE_EXECUTABLE = '/usr/local/bin/EmptyEpsilon'
EE_SERVER_IP = requests.get('https://api.ipify.org').text
EE_API_PORT = 4042
VALID_PLAYERSHIPS = [
    'Atlantis',
    'Benedict',
    'Crucible',
    'Ender',
    'Flavia P.Falcon',
    'Hathcock',
    'Maverick',
    'MP52 Hornet',
    'Nautilus',
    'Phobos M3P',
    'Piranha',
    'Player Cruiser',
    'Player Fighter',
    'Player Missile Cr.',
    'Repulse',
    'Striker',
    'ZX-Lindworm',
]
    

# globale variablen
server_process = None
server_scenario = ''
server_start_time = datetime.now()


ee = EmptyEpsilon('localhost', EE_API_PORT)
bot = Bot('!')


def restrict_to(role):
    def wrapper(cmd):
        async def restricted_command(ctx, *args, **kwargs):
            if role not in [r.name for r in ctx.author.roles]:
                await ctx.send('Du hast keine Berechtigung das zu tun.')
            else:
                await cmd(ctx, *args, **kwargs)
        return restricted_command
    return wrapper


@bot.event
async def on_command_error(ctx, e):
    await ctx.send('Sorry, etwas ist schief gelaufen...')
    if DISCORD_BOT_OWNER != -1:
        user = await bot.fetch_user(DISCORD_BOT_OWNER)
        await user.send(f'Befehl: {ctx.message.content}\nException: {e}')


@bot.command(name='start')
@restrict_to(PRIVILEGED_ROLE)
async def start_server(ctx, scenario, variation=''):
    global server_process
    global server_scenario
    global server_start_time
    if server_process is None:
        await ctx.send('Starte Server...')
        variation_args = [f'variation={variation}'] if variation else []
        cmd = [EE_EXECUTABLE,
               f'headless={scenario}',
               *variation_args,
               f'httpserver={EE_API_PORT}',
               'startpaused=1']
        try:
            server_process = Popen(cmd)
            server_process.wait(10) # poke...
        except TimeoutExpired: # ...server process running
            server_start_time = datetime.now()
            server_scenario = ' - '.join([scenario, variation]) if variation else scenario
            game = discord.Game(name='EmptyEpsilon', start=server_start_time)
            await bot.change_presence(activity=game)
            await ctx.send('Server gestartet.')
        else: # ...server process crashed
            server_process.kill()
            server_process = None
            await ctx.send('Fehler beim Starten des Servers.')
    else:
        await ctx.send('Server läuft bereits.')


@bot.command(name='stop')
@restrict_to(PRIVILEGED_ROLE)
async def stop_server(ctx):
    global server_process
    global server_scenario
    if server_process is not None:
        try:
            server_process.terminate()
            server_process.wait(10)
        except TimeoutExpired:
            await ctx.send('Server reagiert nicht. Kill...')
            server_process.kill()
        await bot.change_presence(activity=None)
        server_process = None
        server_scenario = ''
        await ctx.send('Server gestoppt.')
    else:
        await ctx.send('Kein laufender Server.')


@bot.command(name='pause')
@restrict_to(PRIVILEGED_ROLE)
async def pause_game(ctx):
    ee.exec('pauseGame()')
    await ctx.send('Spiel pausiert.')


@bot.command(name='unpause')
@restrict_to(PRIVILEGED_ROLE)
async def unpause_game(ctx):
    ee.exec('unpauseGame()')
    await ctx.send('Spiel fortgesetzt.')


@bot.command(name='spawn')
@restrict_to(PRIVILEGED_ROLE)
async def spawn_playership(ctx, template, callsign=None, faction=None):
    def safe(arg):
        return arg.replace('"', r'\"') if isinstance(arg, str) else arg
    if template in VALID_PLAYERSHIPS:
        cmd = ['PlayerSpaceship()',
               'setFaction("{}")'.format(safe(faction) or 'Human Navy'),
               f'setTemplate("{safe(template)}")']
        if callsign is not None:
            cmd.append(f'setCallSign("{safe(callsign)}")')
        ee.exec(':'.join(cmd))
        await ctx.send('Schiff bereit.')
    else:
        await ctx.send('Ein Schiff diesen Typs existiert nicht.')


@bot.command(name='status', aliases=['s'])
async def server_status(ctx):
    if server_process is None:
        await ctx.send('Server geschlossen.')
    else:
        delta = datetime.now() - server_start_time
        minutes = int(delta.total_seconds() % 3600 // 60)
        hours = int(delta.total_seconds() // 3600) 
        uptime = '{}h {}m'.format(hours, minutes)
        await ctx.send(f'IP: {EE_SERVER_IP}\nSzenario: {server_scenario}\nUptime: {uptime}')
        

@bot.command(name='hilfe', aliases=['h'])
async def show_help(ctx):
    help = f"""Ich bin EpsiBot, ich kontrollieren den EmptyEpsilon-Server, diese Befehle kannst du mir geben...
    ...wenn du *Brückencrew* bist:
        **!hilfe**, **!h**: Zeigt diese Nachricht.
        **!status**, **!s**: Zeigt den Serverstatus/-IP.
    ...wenn du *{PRIVILEGED_ROLE}* bist:
        **!start *scenario* [*variation*]**: Startet den Server mit *scenario* und ggf. *variation*.
        **!stop**: Stoppt den Server.
        **!pause**: Pausiert das Spiel.
        **!unpause**: Startet das Spiel.
        **!spawn *template* [*callsign*] [*faction*]**: Erstellt ein neues Schiff vom Typ *template*."""
    await ctx.send(help)


bot.run(DISCORD_API_TOKEN)
