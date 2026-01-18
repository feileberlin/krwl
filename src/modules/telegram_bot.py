"""
Telegram Bot for KRWL HOF Community Events

Provides a Telegram bot interface for:
1. Event submissions (manual entry via conversation)
2. Flyer uploads (OCR processing of event flyers)
3. Contact form (messaging admins)

All submissions are saved to pending_events.json for editorial review.
Note: The configuration mentions "incoming.json" as the new name, but
the actual file path is assets/json/pending_events.json.
"""

import os
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING

# Configure module logger
logger = logging.getLogger(__name__)

try:
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        ConversationHandler,
        filters,
        ContextTypes
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot not installed. Install with: pip install python-telegram-bot>=20.0")
    
    # Define dummy types when not available to prevent NameError
    if TYPE_CHECKING:
        from telegram import Update
        from telegram.ext import ContextTypes
    else:
        Update = Any
        ContextTypes = type('ContextTypes', (), {'DEFAULT_TYPE': Any})

# Try to import OCR functionality
try:
    from .smart_scraper.image_analyzer.ocr import extract_text, is_ocr_available
    OCR_AVAILABLE = is_ocr_available()
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR functionality not available")

from .utils import load_pending_events, save_pending_events


# Conversation states for event submission
(TITLE, DATE, TIME, LOCATION, DESCRIPTION, CONFIRMATION) = range(6)

# Conversation state for contact form
(CONTACT_MESSAGE,) = range(1)


class TelegramBot:
    """Telegram bot for community event submissions and contact form."""
    
    def __init__(self, config: Dict[str, Any], base_path: Path):
        """
        Initialize Telegram bot.
        
        Args:
            config: Configuration dictionary with telegram section
            base_path: Base path to repository root
        """
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot library not installed")
        
        self.config = config
        self.base_path = base_path
        self.telegram_config = config.get('telegram', {})
        
        # Get bot token from config or environment
        self.bot_token = self._get_bot_token()
        if not self.bot_token:
            raise ValueError("Telegram bot token not configured. Set 'telegram.bot_token' in config.json or TELEGRAM_BOT_TOKEN environment variable.")
        
        self.admin_chat_ids = self.telegram_config.get('admin_chat_ids', [])
        self.features = self.telegram_config.get('features', {})
        self.limits = self.telegram_config.get('limits', {})
        self.messages = self.telegram_config.get('messages', {})
        
        # Rate limiting (simple in-memory tracking)
        self.user_submissions = {}  # user_id: [timestamps]
        
        # Build application
        self.application = None
        
    def _get_bot_token(self) -> Optional[str]:
        """Get bot token from config or environment variable."""
        token = self.telegram_config.get('bot_token', '').strip()
        if token:
            return token
        
        # Try environment variable
        token = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
        return token if token else None
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """
        Check if user has exceeded rate limit.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if within limits, False if exceeded
        """
        max_per_hour = self.limits.get('rate_limit_per_user', 10)
        now = datetime.now().timestamp()
        hour_ago = now - 3600
        
        # Clean old entries
        if user_id in self.user_submissions:
            self.user_submissions[user_id] = [
                ts for ts in self.user_submissions[user_id] if ts > hour_ago
            ]
        else:
            self.user_submissions[user_id] = []
        
        # Check limit
        if len(self.user_submissions[user_id]) >= max_per_hour:
            return False
        
        # Add new submission
        self.user_submissions[user_id].append(now)
        return True
    
    def _save_to_incoming(self, event_data: Dict[str, Any]):
        """
        Save event data to pending_events.json.
        
        Note: This file may be referred to as "incoming.json" in documentation,
        but the actual file path is assets/json/pending_events.json.
        
        Args:
            event_data: Event dictionary to save
        """
        pending_data = load_pending_events(self.base_path)
        pending_data['pending_events'].append(event_data)
        save_pending_events(self.base_path, pending_data)
        logger.info(f"Saved event to pending_events.json: {event_data.get('title', 'Untitled')}")
    
    async def _notify_admins(self, message: str):
        """
        Send notification to admin users.
        
        Args:
            message: Notification message
        """
        for admin_id in self.admin_chat_ids:
            try:
                await self.application.bot.send_message(
                    chat_id=admin_id,
                    text=f"🔔 Admin Notification\n\n{message}"
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    # Command handlers
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        welcome_msg = self.messages.get('welcome', 
            "🎉 Welcome to KRWL HOF Events Bot!\n\nUse /help to see available commands.")
        
        # Show user their chat ID for admin configuration
        welcome_msg += f"\n\nYour Telegram ID: `{user.id}`"
        
        await update.message.reply_text(
            welcome_msg,
            parse_mode='Markdown'
        )
        
        logger.info(f"User {user.id} ({user.username}) started bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_msg = self.messages.get('help',
            "📋 Available Commands:\n\n"
            "/submit - Submit a new event\n"
            "/upload - Upload event flyer (image with OCR)\n"
            "/contact - Contact the admins\n"
            "/status - Check bot status\n"
            "/cancel - Cancel current operation"
        )
        
        # Filter commands based on enabled features
        if not self.features.get('event_submission'):
            help_msg = help_msg.replace("/submit - Submit a new event\n", "")
        if not self.features.get('flyer_upload'):
            help_msg = help_msg.replace("/upload - Upload event flyer (image with OCR)\n", "")
        if not self.features.get('contact_form'):
            help_msg = help_msg.replace("/contact - Contact the admins\n", "")
        
        await update.message.reply_text(help_msg)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        pending_data = load_pending_events(self.base_path)
        pending_count = len(pending_data.get('pending_events', []))
        
        status_msg = (
            f"🤖 Bot Status: Online\n\n"
            f"📊 Statistics:\n"
            f"• Pending events: {pending_count}\n"
            f"• Features enabled:\n"
        )
        
        if self.features.get('event_submission'):
            status_msg += "  ✅ Event submission\n"
        if self.features.get('flyer_upload'):
            status_msg += f"  ✅ Flyer upload {'(OCR available)' if OCR_AVAILABLE else '(OCR unavailable)'}\n"
        if self.features.get('contact_form'):
            status_msg += "  ✅ Contact form\n"
        
        await update.message.reply_text(status_msg)
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command."""
        await update.message.reply_text(
            "❌ Operation cancelled.\n\nUse /help to see available commands."
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    # Event submission conversation
    
    async def submit_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start event submission conversation."""
        if not self.features.get('event_submission'):
            await update.message.reply_text("❌ Event submission is currently disabled.")
            return ConversationHandler.END
        
        user_id = update.effective_user.id
        if not self._check_rate_limit(user_id):
            await update.message.reply_text(
                "⚠️ You've reached the submission limit. Please try again later."
            )
            return ConversationHandler.END
        
        await update.message.reply_text(
            "📝 Let's submit a new event!\n\n"
            "Please enter the event title (or /cancel to abort):"
        )
        return TITLE
    
    async def submit_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive event title."""
        context.user_data['title'] = update.message.text
        await update.message.reply_text(
            "📅 Please enter the event date (format: YYYY-MM-DD or DD.MM.YYYY):"
        )
        return DATE
    
    async def submit_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive event date."""
        date_str = update.message.text
        
        # Try to parse date (support multiple formats)
        parsed_date = self._parse_date(date_str)
        if not parsed_date:
            await update.message.reply_text(
                "❌ Invalid date format. Please use YYYY-MM-DD or DD.MM.YYYY:"
            )
            return DATE
        
        context.user_data['date'] = parsed_date
        await update.message.reply_text(
            "🕐 Please enter the event time (format: HH:MM) or 'skip' if unknown:"
        )
        return TIME
    
    async def submit_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive event time."""
        time_str = update.message.text.strip().lower()
        
        if time_str == 'skip':
            context.user_data['time'] = None
        else:
            parsed_time = self._parse_time(time_str)
            if not parsed_time:
                await update.message.reply_text(
                    "❌ Invalid time format. Please use HH:MM or 'skip':"
                )
                return TIME
            context.user_data['time'] = parsed_time
        
        await update.message.reply_text(
            "📍 Please enter the event location (name or address):"
        )
        return LOCATION
    
    async def submit_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive event location."""
        context.user_data['location'] = update.message.text
        
        max_length = self.limits.get('max_description_length', 1000)
        await update.message.reply_text(
            f"📄 Please enter the event description (max {max_length} characters)\n"
            "or 'skip' if not available:"
        )
        return DESCRIPTION
    
    async def submit_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive event description."""
        desc_text = update.message.text.strip()
        
        if desc_text.lower() != 'skip':
            max_length = self.limits.get('max_description_length', 1000)
            if len(desc_text) > max_length:
                await update.message.reply_text(
                    f"❌ Description too long (max {max_length} characters). Please shorten it:"
                )
                return DESCRIPTION
            context.user_data['description'] = desc_text
        else:
            context.user_data['description'] = None
        
        # Show summary
        await self._show_submission_summary(update, context)
        return CONFIRMATION
    
    async def submit_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle submission confirmation."""
        text = update.message.text.strip().lower()
        
        if text in ['yes', 'y', 'submit']:
            # Create event data
            event_data = self._create_event_from_context(context.user_data, update.effective_user)
            self._save_to_incoming(event_data)
            
            await update.message.reply_text(
                "✅ Event submitted successfully!\n\n"
                "Your event will be reviewed by our team and published soon.\n"
                "Thank you for your contribution! 🎉"
            )
            
            # Notify admins
            await self._notify_admins(
                f"New event submission from @{update.effective_user.username or update.effective_user.id}:\n"
                f"📌 {event_data.get('title')}\n"
                f"📅 {event_data.get('start_time')}\n"
                f"📍 {event_data.get('location', {}).get('name')}"
            )
            
            context.user_data.clear()
            return ConversationHandler.END
        
        elif text in ['no', 'n', 'cancel']:
            await update.message.reply_text("❌ Submission cancelled.")
            context.user_data.clear()
            return ConversationHandler.END
        
        else:
            await update.message.reply_text("Please reply with 'yes' to submit or 'no' to cancel:")
            return CONFIRMATION
    
    # Flyer upload handler
    
    async def upload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /upload command for flyer images."""
        if not self.features.get('flyer_upload'):
            await update.message.reply_text("❌ Flyer upload is currently disabled.")
            return
        
        if not OCR_AVAILABLE:
            await update.message.reply_text(
                "❌ OCR functionality is not available on this server.\n"
                "Please use /submit to enter event details manually."
            )
            return
        
        user_id = update.effective_user.id
        if not self._check_rate_limit(user_id):
            await update.message.reply_text(
                "⚠️ You've reached the submission limit. Please try again later."
            )
            return
        
        await update.message.reply_text(
            "📸 Please send the event flyer image.\n\n"
            "I'll try to extract event information using OCR.\n"
            "Supported formats: JPG, PNG, PDF"
        )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo upload for flyer OCR."""
        if not self.features.get('flyer_upload') or not OCR_AVAILABLE:
            return
        
        user = update.effective_user
        photo = update.message.photo[-1]  # Get highest resolution
        
        # Check file size
        max_size_mb = self.limits.get('max_flyer_size_mb', 10)
        if photo.file_size > max_size_mb * 1024 * 1024:
            await update.message.reply_text(
                f"❌ Image too large (max {max_size_mb}MB). Please send a smaller image."
            )
            return
        
        await update.message.reply_text("🔍 Processing flyer... This may take a moment.")
        
        try:
            # Download image
            file = await context.bot.get_file(photo.file_id)
            image_bytes = await file.download_as_bytearray()
            
            # Extract text via OCR
            extracted_text = extract_text(bytes(image_bytes), languages=['eng', 'deu'])
            
            if not extracted_text:
                await update.message.reply_text(
                    "❌ Could not extract text from image.\n"
                    "Please try a clearer image or use /submit to enter details manually."
                )
                return
            
            # Parse event information from OCR text
            event_data = self._parse_ocr_text(extracted_text, user, photo.file_id)
            self._save_to_incoming(event_data)
            
            await update.message.reply_text(
                "✅ Flyer processed successfully!\n\n"
                f"Extracted information:\n"
                f"📌 Title: {event_data.get('title', 'Not found')}\n"
                f"📅 Date: {event_data.get('start_time', 'Not found')}\n"
                f"📍 Location: {event_data.get('location', {}).get('name', 'Not found')}\n\n"
                "The event will be reviewed and published soon.\n"
                "Thank you! 🎉"
            )
            
            # Notify admins
            await self._notify_admins(
                f"New flyer upload from @{user.username or user.id}:\n"
                f"OCR extracted: {event_data.get('title', 'Unknown')}"
            )
            
        except Exception as e:
            logger.error(f"Flyer processing error: {e}")
            await update.message.reply_text(
                "❌ Error processing flyer. Please try again or use /submit."
            )
    
    # Contact form conversation
    
    async def contact_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start contact form conversation."""
        if not self.features.get('contact_form'):
            await update.message.reply_text("❌ Contact form is currently disabled.")
            return ConversationHandler.END
        
        user_id = update.effective_user.id
        if not self._check_rate_limit(user_id):
            await update.message.reply_text(
                "⚠️ You've reached the message limit. Please try again later."
            )
            return ConversationHandler.END
        
        await update.message.reply_text(
            "💬 Please enter your message for the admins\n"
            "(or /cancel to abort):"
        )
        return CONTACT_MESSAGE
    
    async def contact_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive contact message."""
        user = update.effective_user
        message_text = update.message.text
        
        # Create contact entry (marked for admins, not event)
        contact_data = {
            'id': f"contact_{user.id}_{int(datetime.now().timestamp())}",
            'type': 'contact_form',
            'title': f"Contact from @{user.username or user.id}",
            'description': message_text,
            'teaser': f"Contact form message from {user.first_name or 'user'}",
            'location': {
                'name': 'Contact Form',
                'lat': 50.3167,
                'lon': 11.9167,
                'address_hidden': True
            },
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'url': f"https://t.me/{user.username}" if user.username else None,
            'source': f"https://t.me/{user.username}" if user.username else "https://t.me",
            'scraped_at': datetime.now().isoformat(),
            'status': 'pending',
            'category': 'contact',
            'metadata': {
                'telegram_user_id': user.id,
                'telegram_username': user.username,
                'telegram_first_name': user.first_name,
                'telegram_last_name': user.last_name,
                'is_contact_form': True  # Special flag for filtering
            }
        }
        
        self._save_to_incoming(contact_data)
        
        await update.message.reply_text(
            "✅ Message sent to admins!\n\n"
            "Thank you for reaching out. We'll get back to you soon."
        )
        
        # Notify admins immediately
        contact_info = f"Reply via: https://t.me/{user.username}" if user.username else f"User ID: {user.id}"
        await self._notify_admins(
            f"📨 New contact message from @{user.username or user.id}:\n\n"
            f"{message_text}\n\n"
            f"{contact_info}"
        )
        
        return ConversationHandler.END
    
    # Helper methods
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format."""
        formats = ['%Y-%m-%d', '%d.%m.%Y', '%d.%m.%y', '%d/%m/%Y', '%d/%m/%y', '%Y/%m/%d']
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        return None
    
    def _parse_time(self, time_str: str) -> Optional[str]:
        """Parse time string to HH:MM format."""
        formats = ['%H:%M', '%H.%M', '%I:%M %p', '%I:%M%p']
        for fmt in formats:
            try:
                dt = datetime.strptime(time_str.strip(), fmt)
                return dt.strftime('%H:%M')
            except ValueError:
                continue
        return None
    
    async def _show_submission_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show event submission summary for confirmation."""
        data = context.user_data
        
        date_str = data.get('date', 'Unknown')
        time_str = data.get('time', 'Unknown')
        
        summary = (
            "📋 Event Summary:\n\n"
            f"📌 Title: {data.get('title')}\n"
            f"📅 Date: {date_str}\n"
            f"🕐 Time: {time_str or 'Not specified'}\n"
            f"📍 Location: {data.get('location')}\n"
            f"📄 Description: {data.get('description') or 'Not provided'}\n\n"
            "Is this correct? Reply 'yes' to submit or 'no' to cancel."
        )
        
        await update.message.reply_text(summary)
    
    def _create_event_from_context(self, user_data: Dict[str, Any], user) -> Dict[str, Any]:
        """Create event dictionary from conversation context."""
        date_str = user_data.get('date')
        time_str = user_data.get('time')
        
        start_time = f"{date_str}T{time_str}:00" if time_str else f"{date_str}T00:00:00"
        
        event_id = f"telegram_{user.id}_{int(datetime.now().timestamp())}"
        
        # Generate teaser from title and description
        title = user_data.get('title', '')
        description = user_data.get('description') or ''
        teaser = title[:200] if len(title) <= 200 else title[:197] + '...'
        if not teaser and description:
            teaser = description[:200] if len(description) <= 200 else description[:197] + '...'
        if not teaser:
            teaser = "Event submitted via Telegram"
        
        return {
            'id': event_id,
            'title': title,
            'description': description,
            'teaser': teaser,
            'location': {
                'name': user_data.get('location'),
                'lat': 50.3167,  # Default Hof coordinates
                'lon': 11.9167,
                'address_hidden': True  # Location needs verification
            },
            'start_time': start_time,
            'end_time': None,
            'url': f"https://t.me/{user.username}" if user.username else None,
            'source': f"https://t.me/{user.username}" if user.username else "https://t.me",
            'scraped_at': datetime.now().isoformat(),
            'status': 'pending',
            'category': 'community',
            'metadata': {
                'telegram_user_id': user.id,
                'telegram_username': user.username,
                'telegram_first_name': user.first_name,
                'submitted_via': 'manual_entry'
            }
        }
    
    def _parse_ocr_text(self, ocr_text: str, user, file_id: str) -> Dict[str, Any]:
        """
        Parse OCR text to extract event information.
        
        This is a simplified parser. For production, consider using
        the AI-powered event extractor from smart_scraper module.
        
        Args:
            ocr_text: Extracted text from OCR
            user: Telegram user object
            file_id: Telegram file ID of the image
            
        Returns:
            Event dictionary
        """
        # Simple extraction (could be enhanced with AI)
        lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
        
        event_id = f"telegram_ocr_{user.id}_{int(datetime.now().timestamp())}"
        
        # Try to extract title (usually first non-empty line)
        title = lines[0] if lines else "Event from Flyer"
        
        # Try to extract date patterns
        date_patterns = [
            r'\d{1,2}[./]\d{1,2}[./]\d{2,4}',
            r'\d{4}-\d{2}-\d{2}'
        ]
        found_date = None
        for pattern in date_patterns:
            matches = re.findall(pattern, ocr_text)
            if matches:
                found_date = self._parse_date(matches[0])
                break
        
        # Generate teaser from OCR text
        teaser_text = ocr_text[:200] if len(ocr_text) <= 200 else ocr_text[:197] + '...'
        if not teaser_text.strip():
            teaser_text = title[:200] if len(title) <= 200 else title[:197] + '...'
        
        return {
            'id': event_id,
            'title': title[:100],  # Limit length
            'description': ocr_text[:500],  # Include OCR text as description
            'teaser': teaser_text,
            'location': {
                'name': 'Hof',  # Default, needs verification
                'lat': 50.3167,
                'lon': 11.9167,
                'address_hidden': True
            },
            'start_time': f"{found_date}T00:00:00" if found_date else datetime.now().isoformat(),
            'end_time': None,
            'url': f"https://t.me/{user.username}" if user.username else None,
            'source': f"https://t.me/{user.username}" if user.username else "https://t.me",
            'scraped_at': datetime.now().isoformat(),
            'status': 'pending',
            'category': 'community',
            'metadata': {
                'telegram_user_id': user.id,
                'telegram_username': user.username,
                'telegram_file_id': file_id,
                'submitted_via': 'flyer_ocr',
                'ocr_text': ocr_text[:1000]  # Store OCR text for review
            }
        }
    
    def build_handlers(self):
        """Build and return conversation handlers for the bot."""
        handlers = []
        
        # Basic commands
        handlers.append(CommandHandler("start", self.start_command))
        handlers.append(CommandHandler("help", self.help_command))
        handlers.append(CommandHandler("status", self.status_command))
        
        # Event submission conversation (if enabled)
        if self.features.get('event_submission'):
            submit_handler = ConversationHandler(
                entry_points=[CommandHandler("submit", self.submit_start)],
                states={
                    TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.submit_title)],
                    DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.submit_date)],
                    TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.submit_time)],
                    LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.submit_location)],
                    DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.submit_description)],
                    CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.submit_confirmation)],
                },
                fallbacks=[CommandHandler("cancel", self.cancel_command)],
            )
            handlers.append(submit_handler)
        
        # Flyer upload handler (if enabled)
        if self.features.get('flyer_upload'):
            handlers.append(CommandHandler("upload", self.upload_command))
            handlers.append(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Contact form conversation (if enabled)
        if self.features.get('contact_form'):
            contact_handler = ConversationHandler(
                entry_points=[CommandHandler("contact", self.contact_start)],
                states={
                    CONTACT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.contact_message)],
                },
                fallbacks=[CommandHandler("cancel", self.cancel_command)],
            )
            handlers.append(contact_handler)
        
        return handlers
    
    async def run(self):
        """Run the bot (blocking)."""
        if not self.telegram_config.get('enabled'):
            logger.warning("Telegram bot is disabled in config")
            return
        
        logger.info("Starting Telegram bot...")
        
        # Build application
        self.application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        for handler in self.build_handlers():
            self.application.add_handler(handler)
        
        # Start bot
        logger.info("Telegram bot is running. Press Ctrl+C to stop.")
        await self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
def main():
    """Standalone entry point for testing."""
    import sys
    import asyncio
    from pathlib import Path
    from .utils import load_config
    
    base_path = Path(__file__).parent.parent.parent
    config = load_config(base_path)
    
    if not config.get('telegram', {}).get('enabled'):
        print("❌ Telegram bot is disabled in config.json")
        print("Enable it by setting 'telegram.enabled: true' and adding your bot token")
        sys.exit(1)
    
    try:
        bot = TelegramBot(config, base_path)
        print("🤖 Starting Telegram bot...")
        print("Press Ctrl+C to stop")
        
        # Use explicit event loop creation (GitHub Actions compatible)
        async def start_bot():
            await bot.run()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(start_bot())
        finally:
            loop.close()
            
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
