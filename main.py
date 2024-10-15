import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os
import logging
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import asyncio
from config import *

song_queue = []

class TkinterHandler(logging.Handler):
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self.write_log, msg)

    def write_log(self, msg):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.configure(state='disabled')
        self.text_widget.yview(tk.END)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


def setup_logging(text_widget):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    tkinter_handler = TkinterHandler(text_widget)
    logger.addHandler(tkinter_handler)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    tkinter_handler.setFormatter(formatter)


@bot.event
async def on_disconnect():
    log("Bot disconnected from Discord")


@bot.event
async def on_ready():
    log(f"{bot.user} | Bot connected to Discord")


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_running_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


async def play_next(ctx):
    if song_queue:
        url = song_queue.pop(0)
        log(f"Playing next song in queue: {url}")
        player = await YTDLSource.from_url(url,loop=bot.loop,stream=True)
        voice_client = discord.utils.get(bot.voice_clients,guild=ctx.guild)

        voice_client.play(player,after=lambda e: bot.loop.create_task(play_next(ctx)))
        await ctx.send(f"Now playing next in queue: ``{player.title}``")


@bot.command(name='play', help='Connects to your current voice channel and starts playing the requested song.')
async def play(ctx, *, url):
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        log("User tried to play music but was not found in any voice channel!")
        await ctx.send("You need to be connected to a voice channel to start playing music.")
        return

    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        voice_client = await channel.connect()

    async with ctx.typing():
        if not voice_client.is_playing():
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            voice_client.play(player, after=lambda e: bot.loop.create_task(play_next(ctx)))
            log(f"Now playing (first in queue): <{player.title}>")
            await ctx.send(f'Now playing (first in queue): ``{player.title}``')

        elif voice_client.is_playing():
            song_queue.append(url)
            log(f"Added to queue: <{url}>")
            await ctx.send(f"Music already playing. Added next in queue: ``{url}``")





@bot.command(name='stop', help='Stops the currently playing song and disconnects the bot from the voice channel.')
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client:
        log("User requested Bot to stop and disconnect!")
        await ctx.send("Stopping and disconencting from voice channel...")
        await voice_client.disconnect()


def start_gui():
    root = tk.Tk()
    root.title("MusicBot logs")
    text_area = ScrolledText(root, state='disabled', wrap='word', width=80, height=20)
    text_area.grid(column=0, row=0, padx=10, pady=10)

    setup_logging(text_area)

    root.mainloop()


def log(x):
    if DEBUG:
        logging.info(x)


if __name__ == "__main__":
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)

    gui_task = new_loop.run_in_executor(None, start_gui)

    token = TOKEN
    try:
        new_loop.run_until_complete(bot.start(token))
    except KeyboardInterrupt:
        pass
    finally:
        new_loop.run_until_complete(new_loop.shutdown_asyncgens())
        new_loop.close()
