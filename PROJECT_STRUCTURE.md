# Job Application Automation Agent

## 📁 Project Structure

```
droid/
├── app.py                    # Main orchestrator
├── config.json              # Configuration (customize this)
├── config.example.json      # Configuration template
├── test_setup.py            # Setup verification script
│
├── agents/                  # Platform-specific agents
│   ├── linkedin_agent.py
│   ├── naukri_agent.py
│   ├── indeed_agent.py
│   ├── unstop_agent.py
│   └── whatsapp_agent.py
│
├── job_tracker.py           # Excel tracking
├── profile_matcher.py       # Job filtering
├── email_checker.py         # Email monitoring
│
├── requirements.txt         # Dependencies
├── README.md               # Full documentation
├── TROUBLESHOOTING.md      # Troubleshooting guide
└── .gitignore              # Git ignore rules
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test setup:**
   ```bash
   python test_setup.py
   ```

3. **Configure:**
   - Edit `config.json` with your details
   - Ensure apps are logged in on device
   - Place resume at configured path

4. **Run:**
   ```bash
   python app.py
   ```

## ⚙️ Key Files

- **app.py** - Main entry point
- **config.json** - All your settings
- **test_setup.py** - Verify droidrun works
- **agents/** - Platform-specific automation

## 📝 Notes

- For **educational purposes only**
- Requires Android device with ADB
- Apps must be pre-authenticated
- See README.md for full documentation
