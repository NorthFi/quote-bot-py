# flask_motivational_bot/app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import discord
from discord.ext import tasks, commands
import requests
import random
import threading
import asyncio
import json
import os

# ----- FLASK SETUP -----
app = Flask(__name__)
app.secret_key = "supersecretkey"

# ----- LOGIN -----
USERNAME = "admin"
PASSWORD = "admin"

# ----- BOT CONFIG -----
CONFIG_FILE = "config.json"
bot_token = ""
channel_id = 0
interval_seconds = 60  # interval in seconds
bot_active = False
active_apis = ["ZenQuotes Random", "ZenQuotes Today"]
use_image_quotes = True

# ----- DISCORD BOT SETUP -----
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)
quote_history = []

# ----- ZenQuotes APIs -----
QUOTE_APIS = {
    "ZenQuotes Random": "https://zenquotes.io/api/random",
    "ZenQuotes Today": "https://zenquotes.io/api/today"
}

INSPIROBOTS = ["https://inspirobot.me/api?generate=true"]

# ----- HELPER FUNCTIONS -----
def load_config():
    global bot_token, channel_id, interval_seconds, active_apis, use_image_quotes
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            bot_token = data.get("bot_token", "")
            channel_id = data.get("channel_id", 0)
            interval_seconds = data.get("interval_seconds", 60)
            active_apis = data.get("active_apis", list(QUOTE_APIS.keys()))
            use_image_quotes = data.get("use_image_quotes", True)

def save_config():
    data = {
        "bot_token": bot_token,
        "channel_id": channel_id,
        "interval_seconds": interval_seconds,
        "active_apis": active_apis,
        "use_image_quotes": use_image_quotes
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def fetch_text_quote():
    available_apis = [api for api in active_apis if api in QUOTE_APIS]
    if not available_apis:
        return "Stay motivated!", "Bot"
    api_name = random.choice(available_apis)
    api = QUOTE_APIS[api_name]
    try:
        response = requests.get(api, timeout=10)
        response.raise_for_status()
        data = response.json()
        quote = data[0] if isinstance(data, list) else data
        text = quote.get("q", "Keep pushing forward!")
        author = quote.get("a", "Unknown")
        if text in quote_history:
            return fetch_text_quote()
        quote_history.append(text)
        if len(quote_history) > 50:
            quote_history.pop(0)
        return text, author
    except Exception:
        return "Stay motivated!", "Bot"

def fetch_image_quote():
    if not use_image_quotes:
        return None
    api = random.choice(INSPIROBOTS)
    try:
        response = requests.get(api, timeout=10)
        response.raise_for_status()
        return response.text
    except:
        return None

def create_embed(text=None, author=None, image_url=None):
    embed = discord.Embed(
        title="",
        color=random.randint(0, 0xFFFFFF)
    )
    if text:
        embed.description = text
        if author:
            embed.set_footer(text=f"- {author}")
    if image_url:
        embed.set_image(url=image_url)
    return embed

async def post_quote():
    channel = bot.get_channel(channel_id)
    if channel:
        if use_image_quotes and random.random() < 0.3:
            image_url = fetch_image_quote()
            if image_url:
                embed = create_embed(image_url=image_url)
                await channel.send(embed=embed)
                return
        text, author = fetch_text_quote()
        embed = create_embed(text=text, author=author)
        await channel.send(embed=embed)

# ----- DYNAMIC INTERVAL TASK -----
send_motivational_quote = None  # global loop reference

async def send_quote_task():
    await bot.wait_until_ready()
    await post_quote()

async def start_loop_async():
    """Start or restart the task loop in the bot's event loop"""
    global send_motivational_quote
    if send_motivational_quote and send_motivational_quote.is_running():
        send_motivational_quote.stop()
    send_motivational_quote = tasks.loop(seconds=interval_seconds)(send_quote_task)
    send_motivational_quote.start()

# ----- RUN BOT IN THREAD -----
def run_bot():
    global bot_active
    if not bot_token:
        print("No bot token set")
        return

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")
        await start_loop_async()

    try:
        bot.run(bot_token)
    except Exception as e:
        bot_active = False
        print(f"Failed to start bot: {e}")

# ----- FLASK ROUTES -----
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("config"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/config", methods=["GET", "POST"])
def config():
    global bot_token, channel_id, interval_seconds, active_apis, use_image_quotes
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            bot_token = request.form["bot_token"].strip()
            channel_id = int(request.form["channel_id"])
            interval_seconds = int(request.form["interval_seconds"])
            active_apis = request.form.getlist("active_apis")
            use_image_quotes = "use_image_quotes" in request.form
            save_config()
            # schedule loop safely in bot's asyncio loop
            if bot.is_ready():
                asyncio.run_coroutine_threadsafe(start_loop_async(), bot.loop)
            flash("Configuration saved!", "success")
            return redirect(url_for("config"))
        except ValueError:
            flash("Invalid input.", "danger")

    return render_template("config.html",
                           bot_token=bot_token,
                           channel_id=channel_id,
                           interval_seconds=interval_seconds,
                           active_apis=active_apis,
                           use_image_quotes=use_image_quotes,
                           bot_active=bot_active,
                           all_apis=list(QUOTE_APIS.keys()))

@app.route("/activate", methods=["POST"])
def activate_bot():
    global bot_active
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if not bot_token or not channel_id:
        flash("Please set bot token and channel ID first.", "danger")
        return redirect(url_for("config"))
    if not bot_active:
        bot_active = True
        threading.Thread(target=run_bot, daemon=True).start()
        flash("Bot activated!", "success")
    else:
        flash("Bot is already running.", "info")
    return redirect(url_for("config"))

@app.route("/deactivate", methods=["POST"])
def deactivate_bot():
    global bot_active
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if bot_active:
        if send_motivational_quote and send_motivational_quote.is_running():
            send_motivational_quote.stop()
        bot_active = False
        flash("Bot deactivated! Restart Flask to reset Discord bot thread.", "success")
    else:
        flash("Bot is not running.", "info")
    return redirect(url_for("config"))

@app.route("/force_post", methods=["POST"])
def force_post():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    asyncio.run_coroutine_threadsafe(post_quote(), bot.loop)
    flash("Quote posted immediately.", "success")
    return redirect(url_for("config"))

@app.route("/clear_messages", methods=["POST"])
def clear_messages():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    async def delete_all_messages():
        channel = bot.get_channel(channel_id)
        if channel:
            async for msg in channel.history(limit=None):
                try:
                    await msg.delete()
                except:
                    pass

    try:
        asyncio.run_coroutine_threadsafe(delete_all_messages(), bot.loop)
        flash("All messages cleared.", "success")
    except Exception as e:
        flash(f"Failed to clear messages: {e}", "danger")
    return redirect(url_for("config"))

@app.route("/preview_quote")
def preview_quote():
    api_name = request.args.get("api")
    if api_name not in QUOTE_APIS:
        return jsonify({"quote": "API not found", "author": ""})
    global active_apis
    active_apis_backup = active_apis
    active_apis = [api_name]
    text, author = fetch_text_quote()
    active_apis = active_apis_backup
    return jsonify({"quote": text, "author": author})

# ----- LOAD CONFIG -----
load_config()

# ----- RUN FLASK -----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
