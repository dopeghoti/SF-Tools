#!/usr/bin/env python3
import discord, asyncio
from discord.ext import tasks # type: ignore
from bot_config import ConfigManager
import satisfactory

heart_beats = 0
conf = ConfigManager()
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot()
sf = satisfactory.API()

@bot.event
async def on_ready():
    print( f'We have logged in as {bot.user}.' )
    print( f'Guild info:  {bot.guilds=}' )
    chan_id = conf.get( 'DISCORD_STATUS_CHANNEL' )
    channel = await bot.fetch_channel( chan_id )
    print( f'Special channel info:  {channel=}' )
    repr( bot )
    sf_server_monitor.start()

@tasks.loop( seconds = 15 )
async def sf_server_monitor():
    global heart_beats
    print( f'heartbeat: {heart_beats:4}' )
    heart_beats += 1
    udpstatus = sf.probe_udp( conf )
    server_state = sf.serverStates[udpstatus['ServerState']]
    print( f'\tUDP Probe complete.  {server_state=}' )
    server_name = udpstatus['ServerName']
    server_version = udpstatus['ServerNetCL']
    if server_state != 'Offline':
        prefix_icon = '✅'
    else:
        prefix_icon = '❌'
        server_version = '-server'
    server_name = udpstatus['ServerName']
    server_version = udpstatus['ServerNetCL']
    chan_id = conf.get( 'DISCORD_STATUS_CHANNEL' )
    channel = await bot.fetch_channel( chan_id )
    await channel.edit( name = f'{prefix_icon}SFv{server_version}-{server_state}' )

@bot.slash_command( guild_ids = [ conf.get( 'DISCORD_GUILD') ] )
async def hello( ctx ):
    await ctx.respond( 'Hello!' )

@bot.slash_command( name="setserveraddress", description="Set the hostname or IP address of the server",  guild_ids = [ conf.get( 'DISCORD_GUILD') ] )
async def setserveraddress( ctx, address ):
    if conf.set( 'SATISFACTORY_HOST', address ):
        try:
            await ctx.respond( f'Satisfactory server address has been set to `{address}`.', ephemeral=True, delete_after = 3.0 )
        except:
            await ctx.respond( f'There was a problem setting the address to {address}.', ephemeral=True )

@bot.slash_command( name="setserverport", description="Set the TCP/UDP port of the server", guild_ids = [ conf.get( 'DISCORD_GUILD') ] )
async def setserverport( ctx, port ):
    try:
        port = int( port )
    except ValueError as e:
        await ctx.respond( f'There was a problem parsing the given port of `{port}`: {e}.', ephemeral=True )
    if conf.set( 'SATISFACTORY_PORT', port ):
        try:
            await ctx.respond( f'Satisfactory server port has been set to `{port}`.', ephemeral=True, delete_after = 3.0 )
        except:
            await ctx.respond( f'There was a problem setting the port to {port}.', ephemeral=True )

bot.run( conf.get( 'DISCORD_TOKEN' ) )
