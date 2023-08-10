import asyncio
import socketio
import threading
from dggbot import DGGBot, DGGLive
from dggbot.live import StreamInfo
from queue import Queue
import json
import datetime

current_timestamp = datetime.datetime.now()
print("Starting: ", current_timestamp)
########################### Config ###########################
config_path = "config.json"


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

messageThrottleTime = config["messageThrottleTime"]

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


# Checks if user is whitelisted, if not, clarifying whisper to user
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


# Sends a message to all users in a list
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


# Sends a message in dggchat when a user donates
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


# Custom message sent in dgg chat, currently used for "RaffleRoll:SendResults"  on frontend
@sio.event
async def broadcast(data):
    msg = data["message"]
    print("queueing broadcast message")
    messageQueue.put(msg)


# dgg whisper broadcast message to all users in notifyUserList
@sio.event
async def raffle(data):
    msg = (
        "Raffle was rolled| sponsor: "
        + data["sponsor"]
        + " amount:"
        + str(data["amount"])
        + " message:"
        + data["message"]
    )

    dgg_whisper_broadcast_notify(msg)


@sio.event
async def disconnect():
    print("disconnected from server")


########################### Live Bot Event Handlers ###########################
# determines whether destiny is streaming


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
# only allowed whitelisted users can use these commands


@bot.command()
def amstats(msg):
    print("stats " + msg.nick)
    if isWhiteListedWithHandler(msg):
        msg.reply("Stats: " + statsURL)


@bot.command()
def amdonate(msg):
    print("donate " + msg.nick)
    if isWhiteListedWithHandler(msg):
        msg.reply("Donate: " + againstMalariaURL)


@bot.command()
def amwatched(msg):
    print("watched " + msg.nick)
    if isWhiteListedWithHandler(msg):
        msg.reply("Watched: " + watchedURL)


########################### Bot Event Handlers ###########################


# trying to figure out what this does LUL
@bot.event()
def on_refresh(msg):
    print("on_refresh")
    print(msg)


# Handle private messages towards the bot
@bot.event()
def on_privmsg(msg):
    print("on_privmsg")
    if isWhiteListed:
        if msg.data.split()[0] == "#bc":
            bcmsg = msg.data[4:]
            dgg_whisper_broadcast_whitelist(msg.nick + ": " + bcmsg)
        else:
            bot.send_privmsg(msg.nick, "You can broadcast messages with !bc <message>")
    else:
        bot.send_privmsg(
            msg.nick,
            "FeelsDankMan I'm a bot. I'm not allowed to reply to private messages. Maybe try gpt71?",
        )

    bot.send_privmsg(botOwner, msg.nick + " sent a private message: " + msg.data)


########################### Running Threads  ###########################


# Connect to Socket.io server
async def run_socket():
    print("Connecting to socket")
    await sio.connect(raffleSocketURL)
    await sio.wait()


# Send messages from the queue every 60 seconds
async def run_SendMessages():
    while True:
        # If there is a message in the queue and destiny is not live, send the message
        if not messageQueue.empty() and not destinyIsLive:
            msg = messageQueue.get()
            print("sending message")
            print(msg)
            bot.send(msg)
        await asyncio.sleep(messageThrottleTime)


# Run the dgg bot
def run_bot():
    print("running bot")
    bot.run_forever()


# Run the dgg live bot
def run_live_bot():
    print("running live bot")
    live.run_forever()


# Run the socket and message sending in parallel
async def aioMain():
    taskSocket = asyncio.create_task(run_socket())
    taskMessages = asyncio.create_task(run_SendMessages())

    await taskMessages
    await taskSocket


if __name__ == "__main__":
    # dggBot does not support asyncio, so we need to run it in a thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    # dggLive does not support asyncio, so we need to run it in a thread
    live_bot_thread = threading.Thread(target=run_live_bot)
    live_bot_thread.start()

    asyncio.run(aioMain())
