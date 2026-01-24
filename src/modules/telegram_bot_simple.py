#!/usr/bin/env python3
"""
Simple Telegram Bot for KRWL HOF Community Events

A straightforward bot that handles:
1. Photo/document uploads (flyers) - cached and dispatched for OCR processing
2. PIN publishing (format: "PIN:1234") - for trusted organizers  
3. Contact messages - forwarded to admins via GitHub issues

This bot uses a simple stateless design and dispatches processing to GitHub Actions
via repository_dispatch events. It shares utilities with the scraper modules.

Integration with scraper modules:
- Uses pin_manager.py for PIN validation (via GitHub Actions)
- Processing jobs in website-maintenance.yml use smart_scraper OCR capabilities
- Event data follows same schema as scraped events

Usage:
    # As standalone script
    python3 src/modules/telegram_bot_simple.py
    
    # Or import the class
    from src.modules.telegram_bot_simple import SimpleTelegramBot
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import telegram library
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot not installed. Install with: pip install python-telegram-bot>=20.0")

# Try to import requests for GitHub API
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    logger.warning("requests not installed. GitHub dispatch will not work.")
    REQUESTS_AVAILABLE = False

# Try to import shared OCR infrastructure from smart_scraper
try:
    from .smart_scraper.sources.social.telegram import TelegramSource, process_telegram_flyer
    from .smart_scraper.image_analyzer.ocr import is_ocr_available
    LOCAL_OCR_AVAILABLE = is_ocr_available()
except ImportError:
    LOCAL_OCR_AVAILABLE = False
    TelegramSource = None
    process_telegram_flyer = None
    logger.info("Local OCR not available - will dispatch to GitHub Actions for processing")


class SimpleTelegramBot:
    """Simple Telegram bot for event submissions via dispatch to GitHub Actions.
    
    This bot integrates with the smart_scraper infrastructure:
    - Uses shared OCR/image_analyzer for local flyer processing (when available)
    - Falls back to GitHub Actions dispatch for CI processing
    - Shares event schema and validation with other scrapers
    """
    
    def __init__(self, bot_token: str, github_token: Optional[str] = None, 
                 github_repo: Optional[str] = None, use_local_ocr: bool = True):
        """
        Initialize the simple Telegram bot.
        
        Args:
            bot_token: Telegram bot token from @BotFather
            github_token: GitHub personal access token (optional, for repository_dispatch)
            github_repo: GitHub repository in format "owner/repo" (optional)
            use_local_ocr: If True, process flyers locally when OCR is available
        """
        self.bot_token = bot_token
        self.github_token = github_token
        self.github_repo = github_repo
        self.use_local_ocr = use_local_ocr and LOCAL_OCR_AVAILABLE
        
        # Set up cache directory
        self.cache_dir = Path.cwd() / ".cache" / "telegram"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Cache directory: {self.cache_dir}")
        
        # Build application
        self.application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, self.handle_media))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        welcome_msg = (
            "🎉 Welcome to KRWL HOF Events Bot!\n\n"
            "📸 Send a flyer image/PDF - I'll process it with OCR\n"
            "📝 Send a message - I'll forward it as a contact form\n"
            "🔐 Trusted organizers: Start message with PIN:1234 to publish directly\n\n"
            "Use /help for more information."
        )
        
        await update.message.reply_text(welcome_msg)
        logger.info(f"User {user.id} ({user.username}) started bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_msg = (
            "📋 How to use this bot:\n\n"
            "🖼️ **Flyer Upload:**\n"
            "Send a photo or PDF of an event flyer. I'll save it and trigger OCR processing.\n\n"
            "💬 **Contact Message:**\n"
            "Send a text message. I'll create a GitHub issue for the admins.\n\n"
            "🔐 **PIN Publishing (Trusted Organizers):**\n"
            "Format your message as:\n"
            "```\n"
            "PIN:1234\n"
            "{\n"
            '  "title": "Event Title",\n'
            '  "start_time": "2026-01-25T18:00:00",\n'
            '  ...\n'
            "}\n"
            "```\n"
            "Replace 1234 with your 4-digit PIN. The event JSON will be validated and published directly.\n\n"
            "All submissions are processed via GitHub Actions workflows."
        )
        
        await update.message.reply_text(help_msg, parse_mode='Markdown')
    
    async def handle_media(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo or document upload (flyers).
        
        Uses shared OCR infrastructure from smart_scraper when available locally,
        otherwise dispatches to GitHub Actions for processing.
        """
        user = update.effective_user
        
        # Determine media type and get file
        if update.message.photo:
            file_obj = update.message.photo[-1]  # Highest resolution
            file_type = "photo"
            extension = "jpg"
        elif update.message.document:
            file_obj = update.message.document
            file_type = "document"
            extension = file_obj.file_name.split('.')[-1] if '.' in file_obj.file_name else 'bin'
        else:
            await update.message.reply_text("❌ Unsupported media type.")
            return
        
        logger.info(f"Received {file_type} from user {user.id}: {file_obj.file_id}")
        
        try:
            # Download file
            file = await context.bot.get_file(file_obj.file_id)
            
            # Generate cache filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cache_filename = f"flyer_{user.id}_{timestamp}.{extension}"
            cache_path = self.cache_dir / cache_filename
            
            # Download to cache
            await file.download_to_drive(cache_path)
            logger.info(f"Saved to cache: {cache_path}")
            
            # Save metadata
            metadata = {
                'file_id': file_obj.file_id,
                'file_type': file_type,
                'file_name': cache_filename,
                'user_id': user.id,
                'username': user.username,
                'timestamp': timestamp,
                'caption': update.message.caption or ''
            }
            
            metadata_path = cache_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Try local OCR processing first (uses shared smart_scraper infrastructure)
            if self.use_local_ocr and process_telegram_flyer:
                logger.info("Using local OCR processing (shared with smart_scraper)")
                event = process_telegram_flyer(
                    str(cache_path),
                    user_id=str(user.id),
                    username=user.username or 'unknown',
                    caption=update.message.caption or ''
                )
                
                if event:
                    # Save extracted event to pending
                    await self._save_pending_event(event)
                    
                    confidence = event.get('metadata', {}).get('ocr_confidence', 0)
                    await update.message.reply_text(
                        "✅ Flyer processed!\n\n"
                        f"OCR confidence: {confidence:.0%}\n"
                        "A draft event has been created for review."
                    )
                    logger.info(f"Local OCR extracted event with confidence {confidence}")
                    return
                else:
                    logger.warning("Local OCR failed to extract event data")
            
            # Fall back to GitHub Actions dispatch
            await self._dispatch_to_github(
                event_type='telegram_flyer_submission',
                client_payload={
                    'file_id': file_obj.file_id,  # Include file_id for workflow to download
                    'file_name': cache_filename,
                    'user_id': user.id,
                    'username': user.username or 'unknown',
                    'timestamp': timestamp,
                    'caption': update.message.caption or ''
                }
            )
            
            await update.message.reply_text(
                "✅ Flyer received!\n\n"
                "I've saved it and triggered OCR processing. "
                "A draft event will be created for review shortly."
            )
            
            
        except Exception as e:
            logger.error(f"Error handling media: {e}")
            await update.message.reply_text(
                "❌ Error processing file. Please try again or contact support."
            )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (PIN publishing or contact form)."""
        user = update.effective_user
        text = update.message.text.strip()
        
        logger.info(f"Received text from user {user.id}")
        
        # Check if this is a PIN publishing request
        if text.startswith('PIN:'):
            await self._handle_pin_publishing(update, context, text)
        else:
            await self._handle_contact_message(update, context, text)
    
    async def _handle_pin_publishing(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Handle PIN publishing for trusted organizers."""
        user = update.effective_user
        
        try:
            # Extract PIN and event data
            lines = text.split('\n', 1)
            pin_line = lines[0].strip()
            
            # Extract PIN (strip whitespace)
            pin = pin_line.split(':', 1)[1].strip()
            
            # Validate PIN format (4 digits)
            if not pin.isdigit() or len(pin) != 4:
                # Silent confirmation (don't reveal validity)
                await update.message.reply_text("✅ Submission received.")
                logger.warning(f"Invalid PIN format from user {user.id}: {pin}")
                return
            
            # Get event data (rest of message)
            if len(lines) < 2:
                await update.message.reply_text("✅ Submission received.")
                logger.warning(f"No event data provided by user {user.id}")
                return
            
            event_data = lines[1].strip()
            
            # Validate JSON format
            try:
                event_json = json.loads(event_data)
            except json.JSONDecodeError as e:
                await update.message.reply_text("✅ Submission received.")
                logger.warning(f"Invalid JSON from user {user.id}: {e}")
                return
            
            # Dispatch to GitHub Actions (PIN validation happens there)
            await self._dispatch_to_github(
                event_type='telegram_pin_submission',
                client_payload={
                    'pin': pin,
                    'event_data': event_json,
                    'user_id': user.id,
                    'username': user.username or 'unknown',
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Always return silent confirmation (don't reveal if PIN is valid)
            await update.message.reply_text("✅ Submission received.")
            logger.info(f"PIN submission from user {user.id} dispatched")
            
        except Exception as e:
            logger.error(f"Error handling PIN publishing: {e}")
            await update.message.reply_text("✅ Submission received.")
    
    async def _handle_contact_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Handle regular contact form messages."""
        user = update.effective_user
        
        try:
            # Dispatch to GitHub Actions
            await self._dispatch_to_github(
                event_type='telegram_contact_submission',
                client_payload={
                    'message': text,
                    'user_id': user.id,
                    'username': user.username or 'unknown',
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            await update.message.reply_text(
                "✅ Message received!\n\n"
                "Thank you for reaching out. An admin will review your message soon."
            )
            
            logger.info(f"Contact message from user {user.id} dispatched")
            
        except Exception as e:
            logger.error(f"Error handling contact message: {e}")
            await update.message.reply_text(
                "❌ Error sending message. Please try again or contact support."
            )
    
    async def _save_pending_event(self, event: Dict[str, Any]):
        """Save extracted event to pending_events.json.
        
        Uses the shared utils module for consistent event storage.
        
        Args:
            event: Event dictionary to save
        """
        try:
            # Try to use shared utils
            from .utils import load_pending_events, save_pending_events
            
            base_path = Path.cwd()
            pending = load_pending_events(base_path)
            
            # Add to pending list
            if 'pending_events' not in pending:
                pending['pending_events'] = []
            pending['pending_events'].append(event)
            
            save_pending_events(base_path, pending)
            logger.info(f"Saved event {event.get('id')} to pending_events.json")
            
        except ImportError:
            # Fallback: save directly to JSON file
            pending_file = Path.cwd() / 'assets' / 'json' / 'pending_events.json'
            
            try:
                if pending_file.exists():
                    with open(pending_file, 'r') as f:
                        pending = json.load(f)
                else:
                    pending = {'pending_events': []}
                
                pending['pending_events'].append(event)
                
                with open(pending_file, 'w') as f:
                    json.dump(pending, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Saved event {event.get('id')} to {pending_file}")
                
            except Exception as e:
                logger.error(f"Error saving pending event: {e}")
                raise
    
    async def _dispatch_to_github(self, event_type: str, client_payload: Dict[str, Any]):
        """
        Dispatch event to GitHub Actions via repository_dispatch API.
        
        Args:
            event_type: Type of event (telegram_flyer_submission, telegram_pin_submission, etc.)
            client_payload: Payload data to send
        """
        if not REQUESTS_AVAILABLE or not self.github_token or not self.github_repo:
            logger.warning(f"Cannot dispatch {event_type}: GitHub integration not configured")
            return
        
        url = f"https://api.github.com/repos/{self.github_repo}/dispatches"
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        data = {
            'event_type': event_type,
            'client_payload': client_payload
        }
        
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, json=data, headers=headers, timeout=10)
            )
            
            if response.status_code == 204:
                logger.info(f"Successfully dispatched {event_type} to GitHub Actions")
            else:
                logger.error(f"Failed to dispatch {event_type}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error dispatching to GitHub: {e}")
    
    async def run(self):
        """Run the bot with polling."""
        logger.info("Starting Telegram bot...")
        
        try:
            # Initialize and start
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES
            )
            
            logger.info("Bot is running. Press Ctrl+C to stop.")
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info("Bot polling cancelled")
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
            raise
        finally:
            # Clean shutdown
            logger.info("Shutting down bot...")
            try:
                if self.application.updater and self.application.updater.running:
                    await self.application.updater.stop()
                if self.application.running:
                    await self.application.stop()
                await self.application.shutdown()
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")


def main():
    """Main entry point."""
    # Get configuration from environment
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        sys.exit(1)
    
    github_token = os.environ.get('GITHUB_TOKEN')
    github_repo = os.environ.get('GITHUB_REPOSITORY')  # Automatically set in GitHub Actions
    
    if not github_token:
        logger.warning("GITHUB_TOKEN not set - repository_dispatch will not work")
    
    if not github_repo:
        logger.warning("GITHUB_REPOSITORY not set - repository_dispatch will not work")
    
    # Create and run bot
    bot = SimpleTelegramBot(bot_token, github_token, github_repo)
    
    # Use explicit event loop creation (GitHub Actions compatible)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        # Clean up
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()


if __name__ == '__main__':
    main()
