import discord
import pyttsx3
from discord.ext import commands, tasks
import time
from time import sleep
from requests import get


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
        self.engine.startLoop(False)
        #List of TTSItem.
        self.queue = []
        self.lock = False
    
    def speak_to_file(self, msg, filename):
        #print(msg)
        self.engine.save_to_file(msg, filename)
        self.engine.iterate()
        #Just constant waiting time is more helpful.
        time.sleep(1)
        #time.sleep(len(msg) * (1/setting.rate) * 1.0 + 0.1)
        print("Speak_to_file_return")
        return
    
    def stop(self):
        self.engine.endLoop()
        return

class TTSItem:
    def __init__(self, voice, channel, usrname, msg, ctx):
        self.voice = voice
        self.channel = channel
        self.usrname = usrname
        self.msg = msg
        self.ctx = ctx
        return
    def __str__(self):
        return "{}_{}".format(self.usrname, self.msg)


# Token for PyOfflineTTS_Bot :
token_file = open("token.txt", "r")
token = token_file.readline()
token_file.close()

setting = Settings(token)
client = commands.Bot(command_prefix=setting.prefix)

tts = TTS(setting.rate)

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

    tts.queue.append(TTSItem(voice,channel,ctx.message.author.id,msg, ctx))
    '''if not voice:
        await channel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    tts.speak_to_file(msg, 'speech.mp3')
    voice.play(discord.FFmpegPCMAudio('./speech.mp3'))'''
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
    tts.engine.setProperty('rate', int(val))
    await ctx.send('Setting.rate : {}'.format(int(val)))
    return

@client.command(pass_context=True)
async def available_voices(ctx):
    voices = tts.engine.getProperty('voices')
    voice_str = ""
    for voice in voices:
        voice_str += (str(voice.id) +"\n")
    await ctx.send('Available_Voices : \n{}'.format(voice_str))
    return

@client.command(pass_context=True)
async def voice(ctx):
    voice = tts.engine.getProperty('voice')
    await ctx.send('Voice : {}'.format(str(voice)))
    return

@client.command(pass_context=True)
async def set_voice(ctx, voice):
    voices = tts.engine.getProperty('voices')
    vid = 0
    for v in voices:
        if str(v.id) == str(voice):
            await ctx.send('Found_Voice : {}'.format(str(v.id)))
            vid = v.id
            break
    if not (vid == 0):
        await ctx.send('Set_Voice : {}'.format(str(v.id)))
        tts.engine.setProperty('voice', v.id)
        tts.engine.iterate()
    now_voice = tts.engine.getProperty('voice')
    await ctx.send('Now_Voice : {}'.format(str(now_voice)))
    return

@client.command(pass_context=True)
async def set_voice_force(ctx, voice):
    await ctx.send('Set_Voice : {}'.format(voice))
    tts.engine.setProperty('voice', voice)
    tts.engine.iterate()
    now_voice = tts.engine.getProperty('voice')
    await ctx.send('Now_Voice : {}'.format(str(now_voice)))
    return

@client.command(pass_context=True)
async def check_ip(ctx):
    ip = get('https://api.ipify.org').text
    await ctx.send('IP Addr : {}'.format(ip))
    return

@client.command(pass_context=True)
async def umjunsik(ctx):
    await ctx.send('엄준식은 살아있다')
    return

@client.command(pass_context=True)
async def settings(ctx):
    await ctx.send(str(setting))
    return

#LOOP
@tasks.loop(seconds = 1) # repeat after every 10 seconds
async def TTSLoop():
    # work
    if len(tts.queue) > 0 and tts.lock == False:
        tsit:TTSItem = tts.queue[0]
        #print(tsit.voice)
        summon_channel = tsit.channel
        if summon_channel is None:
            return False
        
        voice = discord.utils.get(client.voice_clients, guild=tsit.ctx.guild)
        if not (voice):
            await summon_channel.connect()
            voice = discord.utils.get(client.voice_clients, guild=tsit.ctx.guild)
        tts.speak_to_file(tsit.msg, 'speech.mp3')

        
        #print(bool(voice))
        try:
            tts.lock = True
            voice.play(discord.FFmpegPCMAudio('./speech.mp3'))
            while voice.is_playing():
                #print("is_playing")
                sleep(0.1)
            tts.lock = False
        except:
            print("Formal Discord Py Bug")
        print("Loop End")
        del tts.queue[0]
    return


TTSLoop.start()
#issue-1 : Language.
#-> https://stackoverflow.com/questions/65977155/change-pyttsx3-language
client.run(setting.token)