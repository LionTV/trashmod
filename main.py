import json
import discord
import datetime
from discord import Member, Guild, User
from discord import message
from discord.ext import commands
from discord.ext.tasks import loop
from twitch import get_notify
from keep_alive import keep_alive

time = datetime.datetime.now().strftime("%H:%M %p")

client = commands.Bot(command_prefix= '.t')

@client.event
async def on_ready():
    print('Dein Bot ist online!')
    client.loop.create_task(status_task())

async def status_task():
    while True:
      activity = discord.Activity(type=discord.ActivityType.watching, name='.tcmds')
      await client.change_presence(activity=activity)

@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    print(channel)
    await channel.connect()

@client.command()
@commands.has_permissions(kick_members = True)
async def kick(message, member: discord.Member, *, reason=None):
    for i in member.roles:
        try:
            await member.remove_roles(i)
        except:
          print('Cant remove this role')
    else:
      pass
    await member.kick(reason=reason)
    embed = discord.Embed(description=f'Der Spieler {member} wurde gekickt.', color=discord.Color.orange())
    await message.channel.send(embed=embed)
@client.command()
async def roles(ctx, member : discord.Member):
  await ctx.send('Seine/ihre Rollen:')
  for i in member.roles:
    await ctx.send(i)

@client.command()
async def msg(ctx,*, message):
  embed = discord.Embed(title="Information",description=message, color=discord.Color.orange())
  await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(administrator = True)
async def clear(ctx, amount=5):
  await ctx.channel.purge(limit=amount + 1)

@client.command()
@commands.has_permissions(ban_members = True)
async def ban(message, member: discord.Member, *, reason=None):
    for i in member.roles:
        try:
            await member.remove_roles(i)
        except:
          print('Cant remove this role')
    else:
      pass
    await member.ban(reason=reason)
    embed = discord.Embed(description=f'Der Spieler {member} wurde gebannt.', color=discord.Color.orange())
    await message.channel.send(embed=embed)

@client.command()
@commands.has_permissions(administrator = True)
async def unban(message, *, member):
    banned_users = await message.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await message.guild.unban(user)
            embed = discord.Embed(description=f'Der Spieler {user} wurde entbannt.', color=discord.Color.orange())
            await message.channel.send(embed=embed)
            return

@client.command()
async def member(ctx):
    id = ctx.message.guild.id
    Dis = client.get_guild(id)
    embed = discord.Embed(description=f'Der Server hat **{Dis.member_count}** Member.', color=discord.Color.orange())
    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(administrator = True)
async def mute(message, member: discord.Member, *, reason=None):
    guild = message.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=True, send_messages=False)
    await member.add_roles(mutedRole, reason=reason)
    embed = discord.Embed(description=f'Der Member {member.mention} wurde für {reason} gemuted.', color=discord.Color.orange())
    await message.send(embed=embed)
    await member.send(f"Du wurdest auf dem Server **{guild.name}** für **{reason}** gemuted.")

@client.command()
@commands.has_permissions(administrator = True)
async def unmute(ctx, member: discord.Member):
    
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

    await member.remove_roles(mutedRole)
    embed = discord.Embed(description=f'Der Member {member.mention} wurde entmuted.', color=discord.Color.orange())

    await ctx.send(embed=embed)
    await member.send(f"Du wurdest auf dem Server **{ctx.guild.name}** entstummt.")

@client.command()
async def cmds(ctx):
    embed = discord.Embed(title="Commands", description=f'---------------------------------------------------------------------------\n**1) .tmute @member reason** (reason doesn`t have to be filled out)\n(only as administrator)\n---------------------------------------------------------------------------\n**2) .tunmute @member** (only as administrator)\n---------------------------------------------------------------------------\n**3) .tban @member**\n---------------------------------------------------------------------------\n**4) .tunban @member** (only as administrator)\n---------------------------------------------------------------------------\n**5) .tkick @member**\n---------------------------------------------------------------------------\n**6) .tmember**\n---------------------------------------------------------------------------\n**7) .tpoll reason**\n---------------------------------------------------------------------------\n**8) .tid**\n---------------------------------------------------------------------------\n**9) .troles @member**\n---------------------------------------------------------------------------\n**10) .tclear amount** (only as administrator)\n---------------------------------------------------------------------------\n**11) .tinvite**\n---------------------------------------------------------------------------\n**12) .tmsg message**\n---------------------------------------------------------------------------', color=discord.Color.orange())
    await ctx.send(embed=embed)

@client.command()
async def poll(ctx, *, message):
    embed = discord.Embed(title="Abstimmung", description=f'{message}', color=discord.Color.orange())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@client.command()
async def invite(ctx):
  embed = discord.Embed(title="Invite Bot", description=f'https://bit.ly/3zkEdZu', color=discord.Color.orange())
  await ctx.send(embed=embed)

@client.command()
async def id(message):
    embed = discord.Embed(title="Discord ID", description=f'Deine Discord-Id ist: **{message.author.id}**', color=discord.Color.orange())
    await message.channel.send(embed=embed)

@loop(seconds=30)
async def check_twitch_online_streamers():
    channel = client.get_channel(832649579320836158)
    #845292725539438672
    if not channel:
        return
    
    notifications = get_notify()
    for notification in notifications:
      user = notification["user_login"]
      url = "https://www.twitch.tv/" + user
      await channel.send("@everyone der Streamer " + user + " ist jetzt live! Sein/ihr Twitch: " + url)
      
with open("config.json") as config_file:
    config = json.load(config_file)

check_twitch_online_streamers.start()
keep_alive()
client.run(config["client"])