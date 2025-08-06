import os
import logging
import requests
from uuid import uuid4
from telegram import Update, InlineQueryResultAudio, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    filters,
    CallbackContext,
    ContextTypes,
)
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import asyncio
import time
from datetime import datetime, timedelta

# Track first-time users
first_time_users = set()

# Admin list (add your Telegram user ID here)
ADMINS = [7928993116]  # Replace with your actual Telegram ID

# Banned users list
banned_users = set()

# Bot start time for uptime calculation
bot_start_time = time.time()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = "7744151945:AAHXY_czuBvJzpVM435egDK5n5jU0OTRsBg"
SPOTIFY_CLIENT_ID = "539a3af17aa24fbab30bd16b9a6551cd"
SPOTIFY_CLIENT_SECRET = "c5c1d9354966474eb4a705bf3e2c8880"

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Create downloads directory if not exists
if not os.path.exists('downloads'):
    os.makedirs('downloads')

async def start(update: Update, context: CallbackContext) -> None:
    """Send welcome message"""
    user_id = update.message.from_user.id
    
    # Check if user is banned
    if user_id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    # Check if first time user
    if user_id not in first_time_users:
        first_time_users.add(user_id)
    
    # Send GIF first
    gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDF1b3RjY3R5Y2Z6eWl1Y3V1eXZ1Y2R5Z2RjZ3B1eTJ6eGZ1eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7abAHdYvZdBNnGZq/giphy.gif"
    await update.message.reply_animation(gif_url)
    
    # Send welcome message
    welcome_msg = await update.message.reply_text(
        "🎵 Ai Music Bot😊 🎵\n\n"
        "Yoh dawg!! I'm an Ai Music Bot developed by Tylor. I can search and play music from:\n"
        "- YouTube\n"
        "- Spotify\n"
        "- JioSaavn\n"
        "- Google Music\n\n"
        "How to use this Ai Music Bot:\n"
        "1. Send me a song name or URL\n"
        "2. Use inline mode: @Aimusicsearchbot <song name>\n"
        "3. Send a voice note with song name\n"
        "4. Use /menu for quick options\n\n"
        "for help send any of this 👇 command ⤵️\n"
        "⛔ /help 😂\n\n"
        "Bot Developed by Tylor ~ Heis_Tech😊"
    )
    
    # Send startup audio directly after message
    startup_audio_url = "https://youtube.com/shorts/Mgz24YTx5J8?si=97oeHhHz-L7Yur2z"
    await asyncio.sleep(0.1)  # Small delay to ensure message order
    await download_and_send_audio(context.bot, update.message.chat_id, startup_audio_url, "Welcome to Ai Music Bot Dawg!☺️")

async def ping_command(update: Update, context: CallbackContext) -> None:
    """Test bot response speed"""
    start_time = time.time()
    message = await update.message.reply_text("🏓 Pong!")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    
    await message.edit_text(f"🏓 Pong!\n⏱ Bot latency: {latency}ms")

async def uptime_command(update: Update, context: CallbackContext) -> None:
    """Show bot uptime"""
    current_time = time.time()
    uptime_seconds = current_time - bot_start_time
    uptime = timedelta(seconds=int(uptime_seconds))
    
    await update.message.reply_text(
        f"⏱ Bot Uptime:\n"
        f"Started at: {datetime.fromtimestamp(bot_start_time).strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Uptime: {str(uptime)}"
    )

async def menu_command(update: Update, context: CallbackContext) -> None:
    """Show menu with quick options"""
    if update.message.from_user.id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    menu_text = (
        "🎵 Music Bot Menu 🎵\n\n"
        "🔍 Search Options:\n"
        "/song <name> - Search for a song\n"
        "Or just type the song name\n"
        "Or send a voice note with song name\n\n"
        "ℹ️ Information:\n"
        "/help - Show all commands\n"
        "/about - About this bot\n"
        "/stats - Bot statistics\n"
        "/ping - Test bot response speed\n"
        "/uptime - Show bot uptime\n\n"
        "🎧 Quick Search:\n"
        "Type any of these and send:\n"
        "- Song name\n"
        "- Artist name\n"
        "- YouTube/Spotify URL\n"
        "- Voice note with song name"
    )
    
    await update.message.reply_text(menu_text)

async def broadcast_command(update: Update, context: CallbackContext) -> None:
    """Broadcast message to all users (admin only)"""
    user_id = update.message.from_user.id
    
    # Check if user is admin
    if user_id not in ADMINS:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    
    message = ' '.join(context.args)
    total_sent = 0
    failed_users = []
    
    broadcast_msg = await update.message.reply_text("📢 Starting broadcast...")
    
    for user in first_time_users:
        try:
            await context.bot.send_message(user, f"📢 Broadcast from admin:\n\n{message}")
            total_sent += 1
        except Exception as e:
            failed_users.append(user)
            logger.error(f"Failed to send to user {user}: {e}")
    
    result_text = (
        f"📢 Broadcast completed!\n\n"
        f"Total users: {len(first_time_users)}\n"
        f"Successfully sent: {total_sent}\n"
        f"Failed: {len(failed_users)}\n"
    )
    
    if failed_users:
        result_text += f"\nFailed users: {', '.join(map(str, failed_users[:10]))}"
        if len(failed_users) > 10:
            result_text += f" and {len(failed_users)-10} more..."
    
    await broadcast_msg.edit_text(result_text)

async def add_admin(update: Update, context: CallbackContext) -> None:
    """Add a new admin to the bot"""
    user_id = update.message.from_user.id
    
    # Check if user is already admin
    if user_id not in ADMINS:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /addadmin <user_id>")
        return
    
    try:
        new_admin_id = int(context.args[0])
        if new_admin_id not in ADMINS:
            ADMINS.append(new_admin_id)
            await update.message.reply_text(f"✅ User {new_admin_id} has been added as admin.")
        else:
            await update.message.reply_text(f"User {new_admin_id} is already an admin.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a numeric ID.")

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send help message"""
    if update.message.from_user.id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Show welcome message\n"
        "/menu - Show quick menu\n"
        "/help - Show this help\n"
        "/song <name> - Search for a song\n"
        "/about - About this bot\n"
        "/stats - Bot statistics\n"
        "/ping - Test bot response speed\n"
        "/uptime - Show bot uptime\n\n"
        "Admin commands:\n"
        "/broadcast <message> - Broadcast to all users\n"
        "/addadmin <user_id> - Add a new admin\n"
        "/ban <user_id> - Ban a user\n"
        "/unban <user_id> - Unban a user\n\n"
        "You can also:\n"
        "- Send song name\n"
        "- Send artist name\n"
        "- Send YouTube/Spotify URL\n"
        "- Send voice note with song name"
    )

async def about_command(update: Update, context: CallbackContext) -> None:
    """Show about information"""
    if update.message.from_user.id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    await update.message.reply_text(
        "🤖 Ai Music Bot 🤖\n\n"
        "Version: 2.0\n"
        "Developer: Tylor\n"
        "Framework: python-telegram-bot\n"
        "Features:\n"
        "- Search and play music from YouTube, Spotify, JioSaavn, Google Music\n"
        "- Inline mode support\n"
        "- Voice note recognition\n"
        "- Admin controls\n"
        "- Uptime monitoring\n\n"
        "Credits to my Developer ➡️ Tylor ~ Heis_Tech,,For Creating Me😊"
    )

async def stats_command(update: Update, context: CallbackContext) -> None:
    """Show bot statistics"""
    if update.message.from_user.id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    # Basic stats (you can expand this)
    stats_text = (
        "📊 Bot Statistics 📊\n\n"
        f"Total users: {len(first_time_users)}\n"
        f"Total banned users: {len(banned_users)}\n"
        f"Total admins: {len(ADMINS)}\n"
        f"Uptime: {str(timedelta(seconds=int(time.time() - bot_start_time)))}\n"
        "More stats coming soon..."
    )
    await update.message.reply_text(stats_text)

async def ban_user(update: Update, context: CallbackContext) -> None:
    """Ban a user from using the bot"""
    user_id = update.message.from_user.id
    
    # Check if user is admin
    if user_id not in ADMINS:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    
    try:
        target_id = int(context.args[0])
        banned_users.add(target_id)
        await update.message.reply_text(f"✅ User {target_id} has been banned.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a numeric ID.")

async def unban_user(update: Update, context: CallbackContext) -> None:
    """Unban a user"""
    user_id = update.message.from_user.id
    
    # Check if user is admin
    if user_id not in ADMINS:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    
    try:
        target_id = int(context.args[0])
        if target_id in banned_users:
            banned_users.remove(target_id)
            await update.message.reply_text(f"✅ User {target_id} has been unbanned.")
        else:
            await update.message.reply_text(f"User {target_id} is not banned.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a numeric ID.")

async def search_song(update: Update, context: CallbackContext) -> None:
    """Handle song search command"""
    if update.message.from_user.id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Please provide a song name after /song")
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("Your request is being processed, please wait a few seconds... 😊")
    
    try:
        await search_and_send_audio(update, context, query)
    finally:
        # Delete processing message
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=processing_msg.message_id)

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle all text messages"""
    user_id = update.message.from_user.id
    
    # Check if user is banned
    if user_id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    # Check if first time user
    if user_id not in first_time_users:
        first_time_users.add(user_id)
        # Send GIF first
        gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDF1b3RjY3R5Y2Z6eWl1Y3V1eXZ1Y2R5Z2RjZ3B1eTJ6eGZ1eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7abAHdYvZdBNnGZq/giphy.gif"
        await update.message.reply_animation(gif_url)
        
        # Send welcome message
        welcome_msg = await update.message.reply_text(
            "🎵 Ai Music Bot😊 🎵\n\n"
            "Yoh dawg!! I'm an Ai Music Bot developed by Tylor. I can search and play music from:\n"
            "- YouTube\n"
            "- Spotify\n"
            "- JioSaavn\n"
            "- Google Music\n\n"
            "How to use this Ai Music Bot:\n"
            "1. Send me a song name or URL\n"
            "2. Use inline mode: @Aimusicsearchbot <song name>\n"
            "3. Send a voice note with song name\n"
            "4. Use /menu for quick options\n\n"
            "for help send any of this 👇 command ⤵️\n"
            "⛔ /help 😂\n\n"
            "Bot Developed by Tylor ~ Heis_Tech😊"
        )
        
        # Send startup audio directly after message
        startup_audio_url = "https://youtube.com/shorts/Mgz24YTx5J8?si=97oeHhHz-L7Yur2z"
        await asyncio.sleep(0.1)  # Small delay to ensure message order
        await download_and_send_audio(context.bot, update.message.chat_id, startup_audio_url, "Welcome to Ai Music Bot!😊")
    
    text = update.message.text
    
    # Check if it's a URL
    if "youtube.com" in text or "youtu.be" in text or "spotify.com" in text or "jiosaavn.com" in text:
        await handle_url(update, context, text)
    else:
        # Treat as search query
        # Send processing message
        processing_msg = await update.message.reply_text("Your request is being processed, please wait a few seconds... 😊")
        
        try:
            await search_and_send_audio(update, context, text)
        finally:
            # Delete processing message
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=processing_msg.message_id)

async def handle_voice(update: Update, context: CallbackContext) -> None:
    """Handle voice messages by converting to text and searching"""
    if update.message.from_user.id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    voice = update.message.voice
    voice_file = await context.bot.get_file(voice.file_id)
    
    # In a real implementation, you would use a speech-to-text API here
    # For this example, we'll just prompt the user to type the song name
    
    await update.message.reply_text(
        "🎤 Voice note received!\n\n"
        "Currently, I can't process voice notes directly. Please type the song name you want to search for.\n\n"
        "Coming soon: Automatic voice recognition!"
    )

async def handle_url(update: Update, context: CallbackContext, url: str) -> None:
    """Handle music URLs from different platforms"""
    if update.message.from_user.id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    chat_id = update.message.chat_id
    
    try:
        message = await update.message.reply_text("Processing your request............                                               Please wait for a few seconds.................")
        
        if "spotify.com" in url:
            # Handle Spotify URL
            track_info = sp.track(url)
            query = f"{track_info['name']} {track_info['artists'][0]['name']}"
            await search_and_send_audio(update, context, query, is_spotify=True)
        elif "jiosaavn.com" in url:
            # Handle JioSaavn URL (would need JioSaavn API)
            await update.message.reply_text("JioSaavn support coming soon!")
        else:
            # Handle YouTube URL
            await download_youtube_audio(update, context, url)
        
        await context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        await update.message.reply_text("Sorry, I couldn't process that URL. Please try another one.")

async def download_youtube_audio(update: Update, context: CallbackContext, url: str) -> None:
    """Download audio from YouTube"""
    if update.message.from_user.id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    chat_id = update.message.chat_id
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            title = info.get('title', 'audio')
            
        with open(audio_file, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio,
                title=title,
                performer="YouTube",
                caption=f"🎵 {title}\n\nBot developed by Tylor ~ Heis_Tech ✅"
            )
        
        os.remove(audio_file)
    except Exception as e:
        logger.error(f"YouTube download error: {e}")
        await update.message.reply_text("Failed to download from YouTube. Please try another link.")

async def search_google_music(query: str) -> str:
    """Search for music on Google and return the first YouTube result"""
    try:
        # We'll use YouTube search as a proxy for Google Music search
        ydl_opts = {
            'format': 'bestaudio/best',
            'default_search': 'ytsearch1',
            'noplaylist': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if not info.get('entries'):
                raise ValueError("No results found")
            
            entry = info['entries'][0]
            return entry['url']
    except Exception as e:
        logger.error(f"Google music search error: {e}")
        raise

async def search_and_send_audio(update: Update, context: CallbackContext, query: str, is_spotify: bool = False) -> None:
    """Search for a song and send audio"""
    chat_id = update.message.chat_id if update.message else update.inline_query.from_user.id
    
    # Check if user is banned (for inline queries)
    if hasattr(update, 'inline_query') and update.inline_query.from_user.id in banned_users:
        await update.inline_query.answer([
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Error: You are banned",
                input_message_content=InputTextMessageContent("🚫 You are banned from using this bot.")
            )
        ])
        return
    
    try:
        if is_spotify:
            # Search YouTube for Spotify track
            query = f"{query} official audio"
        
        # First try YouTube search
        ydl_opts = {
            'format': 'bestaudio/best',
            'default_search': 'ytsearch1',
            'noplaylist': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if not info.get('entries'):
                raise ValueError("No results found")
            
            entry = info['entries'][0]
            audio_url = entry['url']
            title = entry.get('title', 'Audio Track')
            duration = entry.get('duration', 0)
            
            if update.inline_query:
                # For inline mode
                results = [
                    InlineQueryResultAudio(
                        id=str(uuid4()),
                        audio_url=audio_url,
                        title=title,
                        performer="Music Bot",
                        audio_duration=duration
                    )
                ]
                await update.inline_query.answer(results)
            else:
                # For chat mode
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio_url,
                    title=title,
                    performer="Music Bot",
                    caption=f"🎵 {title}\n\nBot developed by Tylor ~ Heis_Tech ✅"
                )
                
    except Exception as e:
        logger.error(f"Search error: {e}")
        try:
            # If YouTube search fails, try Google Music search
            audio_url = await search_google_music(query)
            title = query
            
            if update.inline_query:
                await update.inline_query.answer([
                    InlineQueryResultAudio(
                        id=str(uuid4()),
                        audio_url=audio_url,
                        title=title,
                        performer="Google Music",
                        audio_duration=0
                    )
                ])
            else:
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio_url,
                    title=title,
                    performer="Google Music",
                    caption=f"🎵 {title} (from Google Music)\n\nBot developed by Tylor ~ Heis_Tech ✅"
                )
        except Exception as e2:
            logger.error(f"Google music search error: {e2}")
            if update.inline_query:
                await update.inline_query.answer([
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title="Error: No results found",
                        input_message_content=InputTextMessageContent("Sorry, no results found for your query.")
                    )
                ])
            else:
                await update.message.reply_text("Sorry, I couldn't find that song. Please try another query.")

async def inline_query(update: Update, context: CallbackContext) -> None:
    """Handle inline music queries"""
    await search_and_send_audio(update, context, update.inline_query.query)

async def post_init(application: Application) -> None:
    """Function to run after the bot starts"""
    # Get the bot's info
    bot = application.bot
    me = await bot.get_me()
    
    # Log bot info
    logger.info(f"Bot started as @{me.username}")
    
    # Send startup message to all admins
    startup_audio_url = "https://youtube.com/shorts/Mgz24YTx5J8?si=97oeHhHz-L7Yur2z"
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, "Yoh Tylor ☺️ 🎵 Music Bot is now online!")
            await download_and_send_audio(bot, admin_id, startup_audio_url, "Music Bot is now online!")
        except Exception as e:
            logger.error(f"Couldn't send startup message to admin {admin_id}: {e}")

async def download_and_send_audio(bot, chat_id, url, caption=None):
    """Download and send audio from YouTube URL"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            title = info.get('title', 'audio')
            
            if not caption:
                caption = f"🎵 {title}\n\nBot developed by Tylor ~ Heis_Tech ✅"
            else:
                caption = f"{caption}\n\nBot developed by Tylor ~ Heis_Tech ✅"
            
        with open(audio_file, 'rb') as audio:
            await bot.send_audio(
                chat_id=chat_id,
                audio=audio,
                title=title,
                performer="Music Bot",
                caption=caption
            )
        
        os.remove(audio_file)
    except Exception as e:
        logger.error(f"Audio download error: {e}")

def main() -> None:
    """Start the bot."""
    # Create application with faster polling interval
    application = Application.builder().token(TOKEN).post_init(post_init).read_timeout(20).write_timeout(20).pool_timeout(20).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("song", search_song))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("addadmin", add_admin))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("uptime", uptime_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(InlineQueryHandler(inline_query))
    
    # Run the bot with faster polling
    application.run_polling(poll_interval=0.1)

if __name__ == "__main__":
    main()