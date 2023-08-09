import asyncio
import socketio
import threading
from dggbot import DGGBot, DGGLive
from dggbot.live import StreamInfo
from queue import Queue
import json

########################### Config ###########################
config_path = "rafflebot/config.json"


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


config = load_json(config_path)


botOwner = config["botOwner"]
botPrefix = config["botPrefix"]
botSecret = config["botSecret"]
raffleSocketURL = config["raffleSocketURL"]

whiteListedUsers = config["whiteListedUsers"]
notifyUserList = config["notifyUserList"]

statsURL = config["statsURL"]
againstMalariaURL = config["againstMalariaURL"]
watchedURL = config["watchedURL"]

print("loaded config")

########################### Synchronized variables ###########################
messageQueue = Queue()
destinyIsLive = False

########################### Initialization ###########################
bot = DGGBot(
    botSecret,
    owner=botOwner,
    prefix=botPrefix,
)

live = DGGLive()

sio = socketio.AsyncClient()  # (logger=True, engineio_logger=True)

########################### Helper Functions ###########################


def isWhiteListed(nick):
    if nick in whiteListedUsers:
        return True
    else:
        return False


def isWhiteListedWithHandler(msg):
    if isWhiteListed(msg.nick):
        return True
    else:
        bot.send_privmsg(
            "You are not whitelisted. If you believe this is a mistake, contact "
            + botOwner,
            msg.nick,
        )
        return False


def dgg_whisper_broadcast(msg, users):
    for user in users:
        bot.send_privmsg(msg, user)


def dgg_whisper_broadcast_whitelist(msg):
    dgg_whisper_broadcast(msg, whiteListedUsers)


def dgg_whisper_broadcast_notify(msg):
    dgg_whisper_broadcast(msg, notifyUserList)


########################### Websocket Event Handlers ###########################


@sio.event
async def connect():
    print("connection established")


@sio.event
async def ping(data):
    print("ping received with ", data)


@sio.event
async def donations(data):
    msg = (
        "Klappa "
        + data["sponsor"]
        + " for donating "
        + data["amount"]
        + " USD with the message: "
        + data["message"]
    )
    print("queueing donation message")
    messageQueue.put(msg)


@sio.event
async def broadcast(data):
    msg = data["message"]
    print("queueing broadcast message")
    messageQueue.put(msg)


@sio.event
async def raffle(data):
    msg = (
        "Raffle was rolled| sponsor: "
        + data["sponsor"]
        + " amount:"
        + data["amount"]
        + " message:"
        + data["message"]
    )

    dgg_whisper_broadcast_notify(msg)


@sio.event
async def disconnect():
    print("disconnected from server")


########################### Live Bot Event Handlers ###########################


@live.event()
def on_streaminfo(streaminfo: StreamInfo):
    global destinyIsLive  # Declare destinyIsLive as a global variable

    if streaminfo.is_live() and not destinyIsLive:
        print("Destiny is live")
        destinyIsLive = True

    if not streaminfo.is_live() and destinyIsLive:
        print("Destiny is not live")
        destinyIsLive = False


########################### Bot Command Handlers ###########################


@bot.command(aliases=["s"])
def stats(msg):
    print("stats " + msg.nick)
    if isWhiteListedWithHandler(msg):
        msg.reply("Stats: " + statsURL)


@bot.command(aliases=["d"])
def donate(msg):
    print("donate " + msg.nick)
    if isWhiteListedWithHandler(msg):
        msg.reply("Donate: " + againstMalariaURL)


@bot.command(aliases=["w"])
def watched(msg):
    print("watched " + msg.nick)
    if isWhiteListedWithHandler(msg):
        msg.reply("Watched: " + watchedURL)


########################### Bot Event Handlers ###########################


@bot.event()
def on_refresh(msg):
    print("on_refresh")
    print(msg)


@bot.event()
def on_privmsg(msg):
    print("on_privmsg")
    if isWhiteListed:
        if msg.split()[0] == "!bc":
            bcmsg = msg[4:]
            dgg_whisper_broadcast_whitelist(msg.nick + ": " + bcmsg)
        else:
            bot.send_privmsg(msg.nick, "You can broadcast messages with !bc <message>")
    else:
        bot.send_privmsg(
            msg.nick,
            "FeelsDankMan I'm a bot. I'm not allowed to reply to private messages. Maybe try gpt71?",
        )

    bot.send_privmsg(botOwner, msg.nick + " sent a private message: " + msg.content)


########################### Running Threads  ###########################


async def run_socket():
    print("Connecting to socket")
    await sio.connect(raffleSocketURL)
    await sio.wait()


# Send messages from the queue every 60 seconds
async def run_SendMessages():
    while True:
        if not messageQueue.empty() and not destinyIsLive:
            msg = messageQueue.get()
            print("sending message")
            print(msg)
            bot.send(msg)
        await asyncio.sleep(60)


def run_bot():
    print("running bot")
    bot.run_forever()


def run_live_bot():
    print("running live bot")
    live.run_forever()


async def aioMain():
    taskSocket = asyncio.create_task(run_socket())
    taskMessages = asyncio.create_task(run_SendMessages())

    await taskMessages
    await taskSocket


if __name__ == "__main__":
    # dggBto does not support asyncio, so we need to run it in a thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    live_bot_thread = threading.Thread(target=run_live_bot)
    live_bot_thread.start()

    asyncio.run(aioMain())
