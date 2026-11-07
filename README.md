# E.V.-Peter-Parker-s-Assistant-Spider-Man-Brand-New-Day-2026
This is a Fork Of https://github.com/Ouru77/ev-assistant With More Interesting Features 


# 🤖 E.V. — Personal AI Voice Assistant

**E.V.** is an AI-powered personal voice assistant built for macOS. It helps users control their Mac, search the web, find files, manage daily tasks, and interact with AI using voice commands.

Note:-Made On Mac,Don't Know About Windows Support,If You want,You Can Try It On Your Windows PC!
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
- Search the web
- Find current information
- Search for news
- Read and summarize web pages
- Open websites in the browser
- Search and open YouTube videos

### 📂 File & Folder Management
- Search files by name
- Search indexed document contents
- Choose folders for E.V. to access
- Open files and folders
- Reveal files in Finder
- Read and summarize supported documents

**Supported formats:**
- PDF
- TXT
- MD
- CSV
- TSV
- JSON
- LOG
- DOC / DOCX
- RTF
- ODT
- HTML

### 🖥️ Mac Control
- Open and close applications
- Control media playback
- Adjust volume
- Adjust brightness
- Enable dark or light mode
- Turn Wi-Fi on or off
- Lock the Mac
- Mouse clicking and scrolling
- Supported power operations

### 🎵 Music & Entertainment
- Control Apple Music
- Play songs from your library
- Play playlists
- Shuffle music
- Pause and resume playback
- Skip tracks
- Search for YouTube videos

### 👁️ AI Screen Vision
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
- Create calendar events
- Check upcoming events
- View today's schedule
- Get a daily briefing
- Include weather and battery information

### 🎥 Zoom Assistant
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

### 🔗 Apple Shortcuts
- Find installed shortcuts
- Run Apple Shortcuts using voice commands

### 🌦️ Weather & Tasks
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
- DeepSeek
- Google Gemini
- Anthropic Claude
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

1. Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
```

2. Enter the project folder:

```bash
cd YOUR_PROJECT_FOLDER
```

3. Install the required dependencies.

4. Configure `config.json` with your preferred settings and AI provider.

5. Grant the necessary macOS permissions.

6. Start E.V.:

```bash
npm start
```

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

Special Thanks For @Ouru77 For Building First Version...

Built with Python, JavaScript, and macOS automation.

---

⭐ If you find this project interesting, consider giving the repository a star!
