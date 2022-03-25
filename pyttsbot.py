import discord
import pyttsx3
from discord.ext import commands
import time

class Settings:
    def __init__(self, token, msgchannel='pytts', prefix='//'):
        self.echo = False
        self.msgchannel =msgchannel
        self.prefix = prefix
        self.rate = 170
        self.token = token
        self.delay = 1.5
        return
    def __str__(self):
        retstr = "### Settings ###\n"
        retstr += "echo : {}\n".format(self.echo)
        retstr += "msgchannel : {}\n".format(self.msgchannel)
        retstr += "prefix : {}\n".format(self.prefix)
        retstr += "rate : {}\n".format(self.rate)
        return retstr

class TTS:
    def __init__(self, rate):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
    
    def start(self, msg, filename):
        self.engine.save_to_file(msg, filename)
        self.engine.runAndWait()
        return


# Token for PyOfflineTTS_Bot :
token_file = open("token.txt", "r")
token = token_file.readline()
token_file.close()

setting = Settings(token)
client = commands.Bot(command_prefix=setting.prefix)

@client.event
async def on_ready():
    print('Logged on as', client.user)
    return

@client.event
async def on_message(message):
    #print('OnMessage')
    if message.author == client.user:
        return
    if message.content.startswith(setting.prefix):
        await client.process_commands(message)
        return
    else:
        msg = message.content
        channel = message.channel
        if(setting.msgchannel in str(channel)):
            if(setting.echo):
                await message.channel.send('Say msg : {'+ msg + '} from : ' + str(channel))
            message.content = setting.prefix +'speak "'+ msg.replace('"',"'") + '"'
            await client.process_commands(message)
            return
        else:
            return

@client.command(pass_context=True)
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send('The PyTTSBot is not connected to a voice channel.')

@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if(voice):
        if(voice.is_connected):
            #Already connected -> Force reconnect.
            await voice.disconnect(force=True)
    #channel = discord.utils.get(ctx.guild.voice_channels, name=ctx.message.author.voice.channel.name)
    await channel.connect()
    return
    
@client.command(pass_context=True)
async def speak(ctx, msg : str):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    channel = discord.utils.get(ctx.guild.voice_channels, name=ctx.message.author.voice.channel.name)
    if not voice:
        await channel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    tts = TTS(setting.rate)
    tts.start(msg, 'speech.mp3')
    time.sleep(setting.delay)
    #Because of bug of pyttsx3.
    del tts
    voice.play(discord.FFmpegPCMAudio('./speech.mp3'))
    #print('Spoken {}'.format(msg))
    return

@client.command(pass_context=True)
async def set_echo(ctx, val:str):
    setting.echo = (val=="True" or val=="true")
    await ctx.send('Setting.echo : {}'.format(setting.echo))
    return

@client.command(pass_context=True)
async def set_msgchannel(ctx, val:str):
    setting.msgchannel = str(val)
    await ctx.send('Setting.msgchannel : {}'.format(setting.msgchannel))
    return

@client.command(pass_context=True)
async def set_speed(ctx, val:str):
    settings.rate = int(val)
    engine.setProperty('rate', int(val))
    await ctx.send('Setting.rate : {}'.format(int(val)))
    return

@client.command(pass_context=True)
async def settings(ctx):
    await ctx.send(str(setting))
    return

#issue-1 : Language.
#-> https://stackoverflow.com/questions/65977155/change-pyttsx3-language
client.run(setting.token)
            
