# Job Application Automation Agent

This is an educational project for automating job applications across multiple platforms using Android automation.

## ⚠️ Disclaimer

**This tool is for educational and hackathon purposes only.** It is not intended for commercial use. Always comply with the terms of service of the platforms you're using. Automated job applications may violate some platforms' policies.

## 🚀 Features

- **Multi-Platform Support**: LinkedIn, Naukri, Indeed, Unstop, and WhatsApp groups
- **Smart Job Matching**: Filters jobs based on your profile and preferences
- **Excel Tracking**: Automatically tracks all applications in an Excel spreadsheet
- **Email Monitoring**: Checks emails for application updates
- **Configurable**: Easy JSON configuration for all settings

## 📋 Prerequisites

1. **Android Device or Emulator** with:
   - ADB enabled
   - Job search apps installed and logged in (LinkedIn, Naukri, Indeed, Unstop)
   - WhatsApp with job groups already joined
   - Resume PDF stored on device

2. **Python 3.8+** installed on your computer

3. **Google Gemini API Key**

## 🛠️ Installation

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Connect your Android device:
```bash
adb devices
```

4. Configure your settings in `config.json`:
   - Update user profile information
   - Set job preferences (titles, keywords, locations)
   - Configure platform settings
   - Set resume path on device

## ⚙️ Configuration

Edit `config.json` to customize:

- **User Profile**: Name, email, phone, resume path
- **Job Preferences**: Desired job titles, keywords, locations, experience level
- **Platforms**: Enable/disable platforms, set application limits
- **WhatsApp**: Groups to monitor, keywords to scan for
- **Tracking**: Excel file paths, logging settings

## 🎯 Usage

1. Make sure your Android device is connected and apps are logged in

2. Ensure your resume is at the path specified in `config.json`

3. Run the agent:
```bash
python app.py
```

4. Monitor the console output for progress

5. Check `job_applications.xlsx` for tracking results

## 📊 Job Tracker

The agent creates an Excel file (`job_applications.xlsx`) with the following information:
- Application ID
- Date Applied
- Platform
- Company
- Job Title
- Location
- Job URL
- Status
- Experience Required
- Job Type
- Skills Matched
- Notes

## 🔧 How It Works

1. **Initialization**: Loads config, connects to Android device
2. **Platform Agents**: Each platform has a dedicated agent that:
   - Opens the app
   - Searches for jobs using your keywords
   - Filters jobs based on your profile
   - Applies to matching positions
   - Tracks applications in Excel
3. **WhatsApp Scanner**: Scans groups for job postings
4. **Email Checker**: Monitors for application responses
5. **Summary**: Generates a report of all actions taken

## 🎨 Customization

### Adding New Job Titles
Edit `config.json` → `job_preferences` → `job_titles`

### Changing Application Limits
Edit `config.json` → `platforms` → `[platform]` → `max_applications_per_session`

### Modifying Search Keywords
Edit `config.json` → `platforms` → `[platform]` → `search_keywords`

## 🐛 Troubleshooting

**ADB Connection Issues:**
- Ensure USB debugging is enabled
- Try `adb kill-server` then `adb start-server`

**Apps Not Opening:**
- Make sure apps are installed
- Check if apps need updates
- Verify you're logged in

**Applications Not Working:**
- Check resume path is correct
- Ensure device has internet connection
- Verify API key is valid

## 📝 Notes

- The agent needs apps to be pre-logged in
- WhatsApp groups must be pre-joined
- Some platforms may have captchas or additional verification
- Adjust delays between applications to avoid rate limiting
- Always review and customize applications when possible

## 🤝 Contributing

This is an educational project. Feel free to:
- Report issues
- Suggest improvements
- Share your modifications

## 📄 License

Educational use only. Not for commercial purposes.

## 🙏 Acknowledgments

Built using:
- [droidrun](https://github.com/droidrun/droidrun) - Android automation framework
- [llama-index](https://github.com/run-llama/llama_index) - LLM framework
- [Google Gemini](https://ai.google.dev/) - AI capabilities
