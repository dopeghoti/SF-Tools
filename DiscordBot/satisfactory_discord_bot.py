#!/usr/bin/env python3
import discord, asyncio
from discord.ext import commands # type: ignore
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

@tasks.loop( seconds = 5 )
async def sf_server_monitor():
    global heart_beats
    heart_beats += 1
    print( f'heartbeat: {heart_beats:4}' )
    udpstatus = sf.probe_udp( conf )
    server_state = sf.serverStates[udpstatus['ServerState']]
    print( f'\tUDP Probe complete.  {server_state=}' )
    #server_name = udpstatus['ServerName']
    if server_state != 'Offline':
        prefix_icon = '✅'
        server_version = udpstatus['ServerNetCL']
    else:
        prefix_icon = '❌'
        server_version = '-server'
    chan_id = conf.get( 'DISCORD_STATUS_CHANNEL' )
    channel = await bot.fetch_channel( chan_id )
    await channel.edit( name = f'{prefix_icon}SFv{server_version}-{server_state}' )

@bot.slash_command( name="shutdown", description="Shut down the Satisfactory server",  guild_ids = [ conf.get( 'DISCORD_GUILD') ] )
@commands.has_role( conf.get( 'DISCORD_ADMIN_ROLE' ) )
async def shutdownsfserver( ctx ):
    response = sf.shutdown_server( conf )
    if response != -1:
        if response == 204:
            await ctx.respond( f'Shutdown command has been sent to the server.', ephemeral=True, delete_after = 5.0 )
        else:
            await ctx.respond( f'Unexpected response code {response} received when trying to send shutdown command to the server.', ephemeral=True, delete_after = 5.0 )
    else:
        await ctx.respond( f'Something really odd happened shutting down the server.  No REST response?', ephemeral=True, delete_after = 5.0 )


@bot.slash_command( name="setserveraddress", description="Set the hostname or IP address of the server",  guild_ids = [ conf.get( 'DISCORD_GUILD') ] )
@commands.has_role( conf.get( 'DISCORD_ADMIN_ROLE' ) )
async def setserveraddress( ctx, address ):
    if conf.set( 'SATISFACTORY_HOST', address ):
        try:
            await ctx.respond( f'Satisfactory server address has been set to `{address}`.', ephemeral=True, delete_after = 3.0 )
        except:
            await ctx.respond( f'There was a problem setting the address to {address}.', ephemeral=True )

@bot.slash_command( name="setserverport", description="Set the TCP/UDP port of the server", guild_ids = [ conf.get( 'DISCORD_GUILD') ] )
@commands.has_role( conf.get( 'DISCORD_ADMIN_ROLE' ) )
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

@bot.slash_command( name="botstatus", description="How long has the bot been alive?", guild_ids = [ conf.get( 'DISCORD_GUILD') ] )
@commands.has_role( conf.get( 'DISCORD_ADMIN_ROLE' ) )
async def botstatus( ctx ):
    global heart_beats
    await ctx.respond( f'Bot has been alive for {heart_beats} cycle{"" if heart_beats == 1 else "s"}.', ephemeral=True, delete_after = 3.0 )

bot.run( conf.get( 'DISCORD_TOKEN' ) )
