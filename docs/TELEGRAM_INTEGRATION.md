# Telegram Integration - Simplified Approach

## Overview

This document describes the **simplified Telegram integration** that replaces the overcomplicated conversation-based bot. The new approach follows proven patterns and integrates seamlessly with GitHub Actions workflows.

## Architecture

```
┌─────────────────┐
│  Telegram Bot   │  scripts/telegram_bot.py
│  (Simple Script)│  - Handles uploads & messages
└────────┬────────┘  - Caches files locally
         │           - Dispatches to GitHub
         │
         ▼
┌─────────────────┐
│  GitHub Actions │  .github/workflows/website-maintenance.yml
│  (Processing)   │  - Processes flyers with OCR
└─────────────────┘  - Creates issues
                     - Validates PINs
                     - Publishes events
```

## Components

### 1. Simple Bot Script (`scripts/telegram_bot.py`)

A straightforward Python script that:
- **Handles photo/document uploads**: Saves to `.cache/telegram/`, dispatches `telegram_flyer_submission`
- **Handles PIN publishing**: Format `PIN:1234\n{...json...}`, validates and dispatches `telegram_pin_submission`
- **Handles contact messages**: Regular text, dispatches `telegram_contact_submission`
- **Uses environment variables**: `TELEGRAM_BOT_TOKEN`, `GITHUB_TOKEN`, `GITHUB_REPOSITORY`

**Key Features:**
- No conversation state management (stateless)
- No complex conversation flows
- Simple dispatch-and-process model
- Security by obscurity for PIN validation (silent confirmations)

### 2. GitHub Actions Integration (`.github/workflows/website-maintenance.yml`)

Three new jobs integrated into the unified meta workflow:

#### Job: `process-telegram-flyer`
Triggered by: `repository_dispatch: telegram_flyer_submission` or manual dispatch

**Steps:**
1. Download file from cache (already uploaded by bot)
2. Run Tesseract OCR (German + English)
3. Create draft JSON in `assets/json/pending_events_telegram_*.json`
4. Commit draft
5. Create GitHub issue with labels: `telegram-submission`, `needs-review`, `flyer`

#### Job: `process-telegram-contact`
Triggered by: `repository_dispatch: telegram_contact_submission` or manual dispatch

**Steps:**
1. Extract message data from payload
2. Create GitHub issue with labels: `telegram-submission`, `contact-form`
3. Include Telegram profile link for admin response

#### Job: `process-telegram-pin`
Triggered by: `repository_dispatch: telegram_pin_submission` or manual dispatch

**Steps:**
1. Extract PIN and event JSON from payload
2. Compute SHA256 hash of PIN (stripped of whitespace)
3. Compare against `ORGANIZER_PIN_HASH_1`, `ORGANIZER_PIN_HASH_2`, `ORGANIZER_PIN_HASH_3` secrets
4. On match:
   - Validate JSON with `jq`
   - Add metadata: `_comment`, `_published_via`, `_published_at`, `_telegram_user_id`, `_telegram_username`
   - Add event directly to `assets/json/events.json`
   - Commit and push
5. On failure: Log but don't notify user (security by obscurity)

## Setup Instructions

### Prerequisites

1. **Telegram Bot Token**
   - Get from [@BotFather](https://t.me/BotFather) on Telegram
   - Command: `/newbot`
   - Follow prompts to create bot
   - Save token securely

2. **GitHub Personal Access Token**
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate new token with `repo` scope
   - Save token securely

3. **Python Dependencies**
   ```bash
   pip install python-telegram-bot>=20.0 requests
   ```

### Configuration

#### GitHub Secrets (Required)

Add these secrets in: Settings > Secrets and variables > Actions

1. **`TELEGRAM_BOT_TOKEN`**: Your bot token from @BotFather
2. **`GITHUB_TOKEN`**: (Automatically provided by GitHub Actions)
3. **`ORGANIZER_PIN_HASH_1`**: SHA256 hash of first trusted organizer PIN
4. **`ORGANIZER_PIN_HASH_2`**: SHA256 hash of second trusted organizer PIN
5. **`ORGANIZER_PIN_HASH_3`**: SHA256 hash of third trusted organizer PIN

**Generating PIN Hashes:**

```bash
# Example: Generate hash for PIN "1234"
echo -n "1234" | sha256sum
# Output: 03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4

# Use the hash (without trailing dash) as the secret value
```

#### Environment Variables (for running bot locally)

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export GITHUB_TOKEN="your_github_token_here"
export GITHUB_REPOSITORY="owner/repo"
```

### Running the Bot

#### Option 1: Local (Development/Testing)

```bash
# Run directly
python3 scripts/telegram_bot.py

# Or with Docker
docker run -it --rm \
  -e TELEGRAM_BOT_TOKEN="..." \
  -e GITHUB_TOKEN="..." \
  -e GITHUB_REPOSITORY="owner/repo" \
  -v $(pwd)/.cache:/app/.cache \
  python:3.11 \
  python3 /app/scripts/telegram_bot.py
```

#### Option 2: GitHub Actions (Production)

Use the existing `telegram-bot.yml` workflow or integrate into a persistent runner.

**Note:** The bot needs to run continuously to receive messages. Options:
- Run on a persistent server/VPS
- Run in GitHub Actions with scheduled workflows (limited uptime)
- Run in Docker container with restart policy

## Usage Guide

### For End Users

#### Submitting a Flyer

1. Send photo or PDF to the bot
2. Bot responds: "✅ Flyer received! I've saved it and triggered OCR processing."
3. Draft event created, admins notified via GitHub issue
4. Admin reviews and publishes

#### Sending a Contact Message

1. Send regular text message to bot
2. Bot responds: "✅ Message received! Thank you for reaching out."
3. GitHub issue created for admins
4. Admin responds via Telegram

#### PIN Publishing (Trusted Organizers Only)

1. Format message as:
   ```
   PIN:1234
   {
     "title": "Community Meetup",
     "start_time": "2026-01-25T18:00:00",
     "location": {
       "name": "City Hall",
       "lat": 50.3167,
       "lon": 11.9167
     },
     ...
   }
   ```
2. Bot responds: "✅ Submission received." (always, even if PIN invalid)
3. If PIN valid: Event published directly to production
4. If PIN invalid: Logged but no action taken

**Security Note:** The bot never reveals whether a PIN is valid or invalid. This prevents brute-force attacks.

### For Admins

#### Managing Trusted Organizers

To add, update, or revoke trusted organizer PINs:

**Using CLI:**
```bash
# Generate new PIN with hash
python3 src/event_manager.py pin-generate

# Compute hash for existing PIN
python3 src/event_manager.py pin-hash 1234

# Validate PIN format
python3 src/event_manager.py pin-validate 5678

# Check configured slots
python3 src/event_manager.py pin-status
```

**Using TUI:**
```bash
python3 src/event_manager.py
# → Choose option 9: "🔐 Manage Organizer PINs"
# → Interactive menu with all PIN management options
```

**Steps to add new trusted organizer:**
1. Generate PIN: `python3 src/event_manager.py pin-generate`
2. Copy the hash from output
3. Add to GitHub Secrets: `ORGANIZER_PIN_HASH_1` (or _2, _3)
4. Share PIN with organizer securely (encrypted message)
5. Organizer can now publish directly via Telegram

**To revoke a PIN:**
1. Delete the corresponding GitHub Secret (`ORGANIZER_PIN_HASH_1`, etc.)
2. Generate new PIN if replacing
3. Notify organizer of revocation

#### Reviewing Flyer Submissions

1. Check GitHub issues with label `telegram-submission` + `flyer`
2. Review OCR-extracted text
3. Edit draft JSON file: `assets/json/pending_events_telegram_*.json`
4. Run workflow: `review-pending` to publish

#### Reviewing Contact Messages

1. Check GitHub issues with label `contact-form`
2. Respond via Telegram link in issue
3. Close issue when resolved

#### Managing Trusted Organizers

1. Generate PIN (4 digits)
2. Compute SHA256 hash: `echo -n "1234" | sha256sum`
3. Add hash to GitHub Secrets: `ORGANIZER_PIN_HASH_1`, `ORGANIZER_PIN_HASH_2`, `ORGANIZER_PIN_HASH_3`
4. Share PIN with trusted organizer (securely)
5. Organizer can now publish directly via Telegram

## Migration from Old Bot

The old conversation-based bot (`src/modules/telegram_bot.py`) is **deprecated** as of January 2025. The current implementation in `src/modules/telegram_bot_simple.py` is simpler, more maintainable, and follows proven patterns.

### Key Differences

| Feature | Old Bot | New Bot |
|---------|---------|---------|
| Conversation state | ✅ Complex | ❌ Stateless |
| Flyer OCR | ⚠️ Optional | ✅ Required workflow |
| PIN publishing | ❌ No | ✅ Yes |
| GitHub integration | ⚠️ Direct commit | ✅ Actions workflow |
| Contact form | ✅ Notify admins | ✅ GitHub issues |
| Spam protection | ⚠️ Rate limiting | ✅ Issue-based moderation |

### Migration Steps

1. **Stop old bot** if running
2. **Deploy new bot** (`scripts/telegram_bot.py`)
3. **Configure GitHub Secrets** (see Setup above)
4. **Test with manual workflow dispatch** before enabling repository_dispatch
5. **Update documentation** to point users to new bot

## Troubleshooting

### Bot Not Receiving Messages

- Check `TELEGRAM_BOT_TOKEN` is correct
- Verify bot is running (check logs)
- Test with `/start` command

### repository_dispatch Not Working

- Verify `GITHUB_TOKEN` has `repo` scope
- Check `GITHUB_REPOSITORY` format: `owner/repo`
- Check GitHub Actions logs for errors

### OCR Not Working

- Verify Tesseract is installed: `tesseract --version`
- Check language packs: `tesseract --list-langs`
- Ensure file is in cache: `.cache/telegram/`

### PIN Publishing Fails

- Verify PIN hash is correct (no whitespace)
- Check secrets are configured: `ORGANIZER_PIN_HASH_1`, etc.
- Review workflow logs for validation errors

## Security Considerations

### PIN Validation

- **Silent confirmations**: Bot always responds "✅ Submission received." regardless of PIN validity
- **No feedback**: Invalid PINs are logged but not revealed to user
- **Rate limiting**: Consider adding IP-based rate limiting at GitHub Actions level

### File Uploads

- **Size limits**: 10MB max (configurable in bot)
- **Type validation**: Only photos and documents accepted
- **Cache directory**: `.cache/telegram/` is gitignored (not committed)

### GitHub Integration

- **Minimal permissions**: Only `repo` scope for `GITHUB_TOKEN`
- **Issue-based moderation**: All submissions create issues for review
- **Audit trail**: All actions logged in GitHub Actions

## Future Enhancements

Potential improvements (not implemented yet):

- [ ] Webhook mode (instead of polling)
- [ ] Multi-language support for bot messages
- [ ] Advanced OCR with AI event extraction
- [ ] Rate limiting per user (store in GitHub repository)
- [ ] Automated spam detection
- [ ] Edit-in-place web forms for easier event editing
- [ ] Helper scripts for PIN management

## References

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [GitHub Actions repository_dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#repository_dispatch)
- [Tesseract OCR Documentation](https://github.com/tesseract-ocr/tesseract)
- [python-telegram-bot Library](https://python-telegram-bot.org/)

## Support

For issues or questions:
- **Repository Issues**: Create issue with label `telegram-integration`
- **Documentation**: See `.github/copilot-instructions.md`
- **Workflow**: `.github/workflows/website-maintenance.yml`
