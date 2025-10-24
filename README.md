# 💡 Motivational Discord Bot – Flask Web Control Panel

A self-hosted motivational quote bot for Discord with a web interface built using **Flask**.

✅ Configure and control your Discord bot from a simple dashboard  
✅ Post motivational quotes automatically to a chosen Discord channel  
✅ Supports multiple quote APIs  
✅ Optional AI-generated image quotes (InspiroBot)  
✅ Set custom posting interval (seconds)  
✅ Secure admin login  
✅ JSON-based config storage (persistent settings)  

---

## 🚀 Features

| Feature | Status |
|----------|--------|
| Flask web dashboard | ✅ |
| Admin login (default: admin/admin) | ✅ |
| Change bot token, channel ID, interval | ✅ |
| Choose from multiple quote APIs | ✅ |
| Toggle image quotes | ✅ |
| Force post quote button | ✅ |
| Clear messages in channel | ✅ |
| Live quote preview | ✅ |
| Auto-reconnection | ✅ |
| Run alongside other services like AMP | ✅ |

---

## 🛠️ Technologies Used

- Python
- Flask
- Discord
- Requests
- JSON for config persistence

---

## 📦 Installation

### 1. Clone This Repo
```bash
git clone https://github.com/northfi/quote-bot-py.git
cd quote-bot-py
```

### 2. Install Dependencies
```bash
pip install flask discord requests
```

### 3. Run the App
```bash
python app.py
```

⚙️ Configuration

The config is stored in config.json automatically.

Option	Description
Bot Token	Discord Bot token from https://discord.com/developers

Channel ID	Numeric channel ID where quotes will be posted
Interval	Quote send interval (seconds)
API Sources	Toggle ZenQuotes, etc.
Image Quotes	Enable AI quote images (InspiroBot)

📚 Supported Quote APIs
API	                             Type	        Status
https://zenquotes.io/api/random  Text quotes	✅
https://zenquotes.io/api/today   Text quotes	✅
https://inspirobot.me/api     AI image quotes	✅

🔧 Buttons & Controls
Button	            Action
✅ Activate Bot	    Starts Discord bot
🛑 Deactivate Bot	  Stops bot loop
⚡ Force Post Now	  Immediately sends a quote
🧹 Clear Messages	  Deletes all bot messages in channel
🔄 Save Settings	  Stores config.json and applies changes

🔒 Security
Simple session-based authentication
Admin-only dashboard
Safe threading & asyncio handling

🚀 Future Features
User roles & permissions
Custom embed colors/themes
Auto-log errors
Docker support
Multi-server bot control

🤝 Contributing
Pull requests are welcome! Please open an issue to discuss major changes.
  
