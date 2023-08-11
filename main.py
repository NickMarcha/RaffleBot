import asyncio
import socketio
from dggbot import DGGBot, DGGLive
from dggbot.live import StreamInfo
from queue import Queue
import json
import time
import datetime
import logging

########################### Version ###########################
DEVELOPMENT = False
# DEVELOPMENT = True
versionNumber = "0.0.2"


########################### Logging ###########################
if DEVELOPMENT:
    logFilePath = "logs/dev.log"
else:
    logFilePath = "logs/app.log"

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(logFilePath, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

logger.info("Version: %s", versionNumber)
logger.info("Development: %s", DEVELOPMENT)

########################### Config ###########################
if DEVELOPMENT:
    config_path = "config/dev.config.json"
else:
    config_path = "config/config.json"


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

current_timestamp = datetime.datetime.now() - datetime.timedelta(
    seconds=messageThrottleTime
)
logger.info("Starting: %s", current_timestamp)
logger.info("loaded config")

########################### Synchronized variables ###########################
messageQueue = Queue()
destinyIsLive = False
last_message_time = time.time()

########################### Initialization ###########################
bot = DGGBot(
    botSecret,
    owner=botOwner,
    prefix=botPrefix,
)

if DEVELOPMENT:
    bot = DGGBot(
        botSecret,
        owner=botOwner,
        prefix=botPrefix,
        config={
            "wss": "wss://chat.omniliberal.dev/ws",
            "wss-origin": "https://www.omniliberal.dev",
            "baseurl": "https://www.omniliberal.dev",
            "endpoints": {"user": "/api/chat/me", "userinfo": "/api/userinfo"},
            "flairs": "https://cdn.omniliberal.dev/flairs/flairs.json",
        },
    )

live = DGGLive()

sio = socketio.AsyncClient(
    reconnection=True,
    reconnection_attempts=0,
    reconnection_delay=1,
    reconnection_delay_max=5,
    randomization_factor=0.5,
    handle_sigint=True,
    logger=True,
    engineio_logger=True,
)

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
        # TODO: re-enable this when the bot is old enough to whisper
        # disabled until the bot is old enough to whisper
        #    bot.send_privmsg(
        #        "You are not whitelisted. If you believe this is a mistake, contact "
        #        + botOwner,
        #        msg.nick,
        #    )
        return False


# TODO: re-enable this when the bot is old enough to whisper
# Sends a message to all users in a list
# def dgg_whisper_broadcast(msg, users):
#    for user in users:
#        bot.send_privmsg(msg, user)

# TODO: re-enable this when the bot is old enough to whisper
# def dgg_whisper_broadcast_whitelist(msg):
#    dgg_whisper_broadcast(msg, whiteListedUsers)

# TODO: re-enable this when the bot is old enough to whisper
# def dgg_whisper_broadcast_notify(msg):
#    dgg_whisper_broadcast(msg, notifyUserList)


########################### Websocket Event Handlers ###########################


@sio.event
async def connect():
    logger.info("connection established")


@sio.event
async def ping(data):
    logger.info("ping received with %s", str(data))


# Sends a message in dggchat when a user donates
@sio.event
async def donations(data):
    if data is not None and "sponsor" in data:
        msg = (
            "Klappa "
            + data["sponsor"]
            + " for donating "
            + data["amount"]
            + " with the message: "
            + data["message"]
        )
        logger.info("queueing donation message")
        messageQueue.put(msg)
    else:
        # Handle the case when data is None or "sponsor" is missing
        logger.warn(
            "Received null object, bug on node backend"
        )  # this is when the dev DB is missing data due to not being updated actively, run MultiPageScrape
        pass


# Custom message sent in dgg chat, currently used for "RaffleRoll:SendResults"  on frontend
@sio.event
async def broadcast(data):
    msg = data["message"]
    logger.info("queueing broadcast message %s", str(msg))
    messageQueue.put(msg)


# TODO: re-enable this when the bot is old enough to whisper
# dgg whisper broadcast message to all users in notifyUserList
# @sio.event
# async def raffle(data):
#    msg = (
#        "Raffle was rolled| sponsor: "
#        + data["sponsor"]
#        + " amount:"
#        + str(data["amount"])
#        + " message:"
#        + data["message"]
#    )

#    dgg_whisper_broadcast_notify(msg)


@sio.event
async def disconnect():
    logger.warning("disconnected from server")


########################### Live Bot Event Handlers ###########################
# determines whether destiny is streaming


@live.event()
def on_streaminfo(streaminfo: StreamInfo):
    global destinyIsLive  # Declare destinyIsLive as a global variable

    if streaminfo.is_live() and not destinyIsLive:
        logger.info("Destiny is live")
        destinyIsLive = True

    if not streaminfo.is_live() and destinyIsLive:
        logger.info("Destiny is not live")
        destinyIsLive = False


########################### Bot Command Handlers ###########################
# only allowed whitelisted users can use these commands


@bot.command(aliases=["ams"])
def amstats(msg):
    logger.info("stats " + msg.nick)
    if isWhiteListedWithHandler(msg):
        msg.reply("Stats: " + statsURL)


@bot.command(alias=["amd"])
def amdonate(msg):
    logger.info("donate " + msg.nick)
    if isWhiteListedWithHandler(msg):
        msg.reply("Donate: " + againstMalariaURL)


@bot.command(aliases=["amw"])
def amwatched(msg):
    logger.info("watched " + msg.nick)
    if isWhiteListedWithHandler(msg):
        msg.reply("Watched: " + watchedURL)


########################### Bot Event Handlers ###########################


# trying to figure out what this does LUL
@bot.event()
def on_refresh(msg):
    logger.info("on_refresh")
    logger.info(msg)


# Leaving this here for debug purposes
@bot.event()
def on_msg(msg):
    if msg.nick == botOwner:
        print(botOwner)
        print(msg.data)


# TODO: re-enable this when the bot is old enough to whisper
# Handle private messages towards the bot
# @bot.event()
# def on_privmsg(msg):
#    logger.info("on_privmsg")
#    if isWhiteListed:
#        if msg.data.split()[0] == "#bc":
#            bcmsg = msg.data[4:]
#            dgg_whisper_broadcast_whitelist(msg.nick + ": " + bcmsg)
#        else:
#            bot.send_privmsg(msg.nick, "You can broadcast messages with !bc <message>")
#    else:
#        bot.send_privmsg(
#            msg.nick,
#            "FeelsDankMan I'm a bot. I'm not allowed to reply to private messages. Maybe try gpt71?",
#        )
#
#    bot.send_privmsg(botOwner, msg.nick + " sent a private message: " + msg.data)


########################### Running Threads  ###########################


# Connect to Socket.io server
async def run_socket():
    logger.info("Connecting to socket")
    await sio.connect(raffleSocketURL)
    await sio.wait()


# Send messages from the queue every 60 seconds
async def run_SendMessages():
    global last_message_time
    while True:
        # If there is a message in the queue and destiny is not live, send the message
        if not messageQueue.empty() and not destinyIsLive:
            current_time = time.time()
            time_since_last_message = current_time - last_message_time
            if time_since_last_message > messageThrottleTime:  # Throttle messages
                msg = messageQueue.get()
                logger.info("sending message")
                logger.info(msg)
                bot.send(msg)
                last_message_time = time.time()
        await asyncio.sleep(2)


# Run the dgg bot
def run_bot():
    global bot  # Declare destinyIsLive as a global variable
    logger.info("connecting bot")
    bot.run_forever()


# Run the dgg live bot
def run_live_bot():
    if DEVELOPMENT:
        logger.info("not running live bot, dev mode")

    else:
        logger.info("running live bot")
        live.run_forever()


async def aioMain():
    taskSocket = asyncio.create_task(run_socket())
    taskMessages = asyncio.create_task(run_SendMessages())

    await taskMessages
    await taskSocket


async def main():
    bot_thread = asyncio.to_thread(run_bot)

    live_bot_thread = asyncio.to_thread(run_live_bot)

    await asyncio.gather(bot_thread, live_bot_thread, aioMain())


if __name__ == "__main__":
    asyncio.run(main())