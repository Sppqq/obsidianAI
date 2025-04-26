# Obsidian Telegram Bot

[🇷🇺 Русская версия](README_RU.md)

A powerful Telegram bot for managing notes and media files with automatic processing using Google's Gemini AI. The bot helps organize and format your notes in Markdown, making them perfect for Obsidian.

## 🆕 Latest Updates

- ✨ Updated Gemini model to gemini-2.0-flash-exp
- 🛠️ Improved text processing and formatting
- 📊 Optimized performance
- 🔄 Enhanced proxy stability
- 🌐 Added support for embedding various links

## 🌟 Features

- 🤖 AI-powered note processing using Google Gemini
- 📝 Automatic Markdown formatting
- 🏷️ Custom tag management system
- 📸 Support for various media files (photos, audio, video, documents)
- ☁️ Dropbox integration
- 🔄 Proxy support for stable connection
- 👥 Multi-user support
- 📱 Mobile-friendly experience

## 🛠️ Prerequisites

- Python 3.8+
- Telegram Bot Token
- Google Gemini API Key
- Dropbox API credentials (optional)
- Proxy (optional)

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/Sppqq/obsidianAI.git
cd obsidianAI
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## 📋 Configuration

1. The bot will automatically create a `config.json` file on first run. Configure it with your credentials:

```json
{
    "user1": {
        "chat_id": YOUR_CHAT_ID,
        "bot_token": "YOUR_BOT_TOKEN",
        "gemini_api": "YOUR_GEMINI_API",
        "gemini_model": "gemini-2.0-flash-exp",
        "tags": ["#code", "#study", "#files", "#ai", "#other"],
        "db_app_key": "your-dropbox-key",
        "db_app_secret": "your-dropbox-secret",
        "db_redirect_uri": "http://localhost:8080",
        "proxy": {
            "http": "http://your-proxy-server",
            "https": "http://your-proxy-server"
        }
    }
}
```

### 🔑 Getting API Keys

1. **Telegram Bot Token**:
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Create new bot with `/newbot`
   - Copy the provided token

2. **Google Gemini API**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Copy the API key

3. **Dropbox API** (optional):
   - Go to [Dropbox Developer Console](https://www.dropbox.com/developers/apps)
   - Create a new app
   - Set the redirect URI to `http://localhost:8080`
   - Copy App key and App secret

### 🔒 Proxy Configuration

For stable connection in some regions, you may need to use a proxy:

```json
"proxy": {
    "http": "http://username:password@proxy-server:port",
    "https": "http://username:password@proxy-server:port"
}
```

## 🚀 Usage

1. Start the bot:
```bash
python main.py
```

2. Send `/start` to your bot on Telegram

3. Use the following commands:
   - `/start` - Initialize the bot
   - `/tags` - Manage your tags

4. Send any text or media to the bot:
   - The bot will process it using Gemini AI
   - Format it in Markdown
   - Add appropriate tags
   - Save it as a `.md` file

## 📝 Note Format

The bot automatically formats notes with:
- Clear, concise titles
- Markdown formatting
- Embedded media
- Custom tags
- Proper text formatting with bold emphasis
- Emoji enhancements
- Working links

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

If you have any questions or issues, please create an issue in the repository or contact the author via Telegram. 