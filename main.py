import json
import logging
from datetime import datetime
from typing import Optional
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButtonRequestChat,
    ChatAdministratorRights
    )
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    CallbackContext
    )
from nitter import ReadRss

# Import configuration file
try:
    from config import env
except ImportError:
    print("""
    ERROR: Missing config.py!

    Please copy config.example.py into config.py and complete it!
    """)
    exit(1)

headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

default_bot_administrator_rights = ChatAdministratorRights(
    True, False, False, False, False, False, False, False, True, False, True
)
default_user_administrator_rights = ChatAdministratorRights(
    True, False, False, False, False, True, False, True, True, False, True
)

last_tweet_date = None

def update_channel_id(id):
    global channel_id
    channel_id = id
    env["CHANNEL_ID"] = channel_id

    env_str = json.dumps(env, indent=4, default=str)

    with open("config.py", "w") as f:
        f.write(f"env = {env_str}")
    
async def is_admin(update, context):
    user_id = update.effective_user.id
    if(user_id in admin_id):
        return True
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Unauthorized User!")
        return False

def is_newer_tweet(pub_date1: str, pub_date2: Optional[str]) -> bool:
    if pub_date2 is None:
        return True
    else:
        return datetime.strptime(pub_date1, '%a, %d %b %Y %H:%M:%S %Z') > datetime.strptime(pub_date2, '%a, %d %b %Y %H:%M:%S %Z')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello!")


async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        request_channel = KeyboardButtonRequestChat(request_id=1, chat_is_channel=True,
        user_administrator_rights=default_user_administrator_rights, bot_administrator_rights=default_bot_administrator_rights)
        reply_keyboard = [[KeyboardButton("-Select Channel-" ,request_chat=request_channel)]]
        await update.message.reply_text(
            "You must have admin rights to Add New Admins and Post Messages. \nWarning: If a channel is already added, selecting a new channel will replace it.",
            
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Select Channel"
            )
        )
        
async def channel_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        context.job_queue.run_repeating(callback=send_tweet, first=1, interval=900, chat_id=update.effective_chat.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Starting the bot! \nUpdate interval is 15 minutes")

async def channel_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Stoping the bot!")
        await context.job_queue.stop()

async def send_tweet(context: CallbackContext):
    try:
        global last_tweet_date
        query = "%23cybersecurity+OR+%23zeroday"
        url = f"https://nitter.net/search/rss?f=tweets&q={query}&f-verified=on&e-replies=on&e-nativeretweets=on"
        feed = ReadRss(url, headers)
        for t in reversed(feed.tweets_dicts):
            pub_date = t['pub_date']
            if last_tweet_date is None or is_newer_tweet(pub_date, last_tweet_date):
                tweet = t['title'] + "\n\n" + "By " + t['creator'] + "\n" + pub_date
                await context.bot.send_message(chat_id=channel_id, text=tweet)
                last_tweet_date = pub_date
    except Exception as e:
        if 'Chat' in str(e):
            await context.bot.send_message(chat_id=context._chat_id, text="Please configure the channel using 'add_channel' command first")

async def channel_shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = update.message.chat_shared.chat_id
    update_channel_id(channel_id)
    await context.bot.send_message(chat_id=channel_id, text="Channel Added Successfully!")
    await update.message.reply_text(
        "Channel Added Successfully! ",
        reply_markup=ReplyKeyboardRemove(),
    )
    
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Unknown Command!")

if __name__ == '__main__':
    bot_token = env['BOT_TOKEN']
    admin_id = env['ADMIN_ID']
    channel_id = str(env.get('CHANNEL_ID', ''))

    application = ApplicationBuilder().token(bot_token).build()

    start_handler = CommandHandler('start', start)
    add_channel_handler = CommandHandler('add_channel', add_channel)
    channel_start_handler = CommandHandler('channel_start', channel_start)
    channel_stop_handler = CommandHandler('channel_stop', channel_stop)
    channel_shared_handler = MessageHandler(filters.StatusUpdate.CHAT_SHARED, channel_shared)
    unkown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(add_channel_handler)
    application.add_handler(channel_start_handler)
    application.add_handler(channel_stop_handler)
    application.add_handler(channel_shared_handler)
    application.add_handler(unkown_handler)         #This handler must be added last.

    application.run_polling()