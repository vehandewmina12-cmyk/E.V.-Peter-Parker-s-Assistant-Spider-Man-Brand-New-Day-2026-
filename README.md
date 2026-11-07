# 🤖 E.V. — Personal AI Voice Assistant

**E.V.** is an AI-powered personal voice assistant built for macOS. It helps users control their Mac, search the web, find files, manage daily tasks, and interact with AI using voice commands.

Note:- This is a Fork Of https://github.com/Ouru77/ev-assistant

Note:- This Ai Assistant Was Made On A Mac,So It Functions On Macs... If You Are a Windows User You can Also Try It( But Experimental And Not tested)!

---

## ✨ Features

### 🧠 AI & Voice
- AI-powered conversations
- Voice input and spoken responses
- Speech recognition using Whisper
- Optional wake-word activation
- Conversation history
- Long-term memory
- Supports Ollama, DeepSeek, Gemini, and Claude

### 🌐 Web & Internet
- Search the web (Beta)
- Find current information (Beta)
- Search for news (Beta)
- Read and summarize web pages (Beta)
- Open websites in the browser
- Search and open YouTube videos

### 📂 File & Folder Management
- Search files by name (Beta)
- Search indexed document contents (Beta)
- Choose folders for E.V. to access (Beta)
- Open files and folders
- Reveal files in Finder
- Read and summarize supported documents (Beta)

**Supported formats:**
- PDF (Beta)
- TXT (Beta)
- MD (Beta)
- CSV (Beta)
- TSV (Beta)
- JSON (Beta)
- LOG (Beta)
- DOC / DOCX (Beta)
- RTF (Beta)
- ODT (Beta)
- HTML (Beta)
- 
### 🖥️ Mac Control
- Open and close applications
- Control media playback
- Adjust volume (Beta)
- Adjust brightness (Beta)
- Enable dark or light mode (Beta)
- Turn Wi-Fi on or off (Beta)
- Lock the Mac
- Mouse clicking and scrolling (Beta)
- Supported power operations

### 🎵 Music & Entertainment
- Control Apple Music
- Play songs from your library
- Play playlists
- Shuffle music (Beta)
- Pause and resume playback (Beta)
- Skip tracks (Beta)
- Search for YouTube videos

### 👁️ AI Screen Vision (Beta)
- Capture the Mac screen
- Analyze screenshots using AI
- Describe visible screen content
- Ask questions about the screen

### ⏰ Reminders & Time Management
- Create reminders
- Set timers
- Set alarms
- Cancel active timers

### 📅 Calendar & Daily Briefing
- Create calendar events (Beta)
- Check upcoming events (Beta)
- View today's schedule
- Get a daily briefing
- Include weather and battery information

### 🎥 Zoom Assistant (Beta)
- Join Zoom meetings
- Find upcoming Zoom meetings
- Use meeting IDs and passwords
- Cancel pending meeting actions

### 💬 WhatsApp
- Find contacts
- Prepare messages
- Send WhatsApp messages
- Confirm before sending

### ⚙️ System Monitoring
- Monitor CPU usage
- Check RAM usage
- Check disk usage
- Check battery percentage
- Check charging status

### 🔗 Apple Shortcuts (Beta)
- Find installed shortcuts
- Run Apple Shortcuts using voice commands

### 🌦️ Weather & Tasks (Beta)
- Retrieve weather information
- Read tasks from an Obsidian `Tasks.md` file
- Include useful information in daily briefings

---

## 🛠️ Technologies Used

- Python
- FastAPI
- WebSockets
- JavaScript
- Node.js
- Ollama
- Whisper
- ElevenLabs
- DuckDuckGo Search
- Playwright
- AppleScript
- macOS Automation

---

## 💻 Requirements

- macOS
- Python 3
- Node.js and npm
- Microphone and speakers
- Internet connection for online features
- API keys for selected cloud AI services
- Ollama for local AI (optional)
- Required macOS permissions

---

## 🚀 Installation

1. Download Zip File
  
2. Enter the project folder:

```bash
cd YOUR_PROJECT_FOLDER
```
3.Run These Commands

```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```

```bash
python server.py
```

4. Install the required dependencies.

5. Configure `config.json` with your preferred settings and AI provider.

6. Grant the necessary macOS permissions.

7. Start E.V.

Run These Commands

```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```

```bash
python server.py
```

8. Done!

   
---

## 🔐 Privacy & Security

- Supports local AI processing through Ollama.
- File access is designed to be read-only.
- Sensitive files and directories are excluded from file search.
- WhatsApp messages require confirmation before sending.
- Some features require macOS Automation, Accessibility, or Screen Recording permissions.

**Note:** Cloud AI providers may receive information sent to them. Privacy depends on your selected provider and configuration.

---

## ⚠️ Limitations

- Some features require API keys.
- File search depends on Spotlight indexing and permissions.
- Some websites may block automated access.
- Screen vision requires a compatible vision model.
- Some integrations require additional applications and macOS permissions.
- Availability of features depends on configuration and installed dependencies.

---

## 📌 Project Status

E.V. is an evolving personal AI assistant project. New features, improvements, and integrations may be added over time.

---

## 👨‍💻 Author

**PAVD**

Special Thanks To @Ouru77 For Making First Version...

Built with Python, JavaScript, AI, and macOS automation.

---

⭐ If you find this project interesting, consider giving the repository a star!
