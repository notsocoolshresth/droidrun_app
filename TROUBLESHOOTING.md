# Troubleshooting Guide

## Common Issues and Solutions

### 1. "Failed to parse state data from ContentProvider"

This error occurs when droidrun cannot access the Android device state properly.

**Solutions:**

#### Option A: Check ADB Connection
```bash
adb devices
adb shell dumpsys window | findstr mCurrentFocus
```

#### Option B: Restart ADB Server
```bash
adb kill-server
adb start-server
adb devices
```

#### Option C: Install Required APK on Emulator
The droidrun framework needs a helper APK installed on the device:
```bash
# Download droidrun APK if needed
# Install it on your emulator
adb install /path/to/droidrun.apk
```

#### Option D: Grant Permissions
Make sure the emulator has all necessary permissions:
```bash
adb shell pm grant com.droidrun.portal android.permission.WRITE_SECURE_SETTINGS
adb shell settings put secure enabled_accessibility_services com.droidrun.portal/.AccessibilityService
```

#### Option E: Use Simpler Test First
Before running the full job application agent, test with a simple script:

**test_simple.py:**
```python
import asyncio
from droidrun import AdbTools, DroidAgent, DroidrunConfig
from llama_index.llms.google_genai import GoogleGenAI
import os

async def main():
    os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
    tools = AdbTools()
    config = DroidrunConfig()
    llm = GoogleGenAI(model="gemini-2.5-flash", temperature=0.2)
    
    # Simple test - just open settings
    agent = DroidAgent(
        goal="Open the Settings app",
        config=config,
        tools=tools,
        llms=llm
    )
    
    print("Testing basic functionality...")
    await agent.run()
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(main())
```

Run: `python test_simple.py`

### 2. ConfigurationError

**Issue:** DroidrunConfig may need additional setup.

**Solution:** Create a `.droidrunrc` file in your home directory or project:

```json
{
  "adb_path": "adb",
  "device_serial": "emulator-5554"
}
```

### 3. Timeout Errors

If the agent times out waiting for apps to load:
- Increase timeout in DroidrunConfig
- Make sure apps are already installed
- Ensure apps are logged in beforehand

### 4. API Key Issues

Make sure your Google API key is set:
```bash
# In PowerShell
$env:GOOGLE_API_KEY="your-api-key-here"
python app.py
```

Or add to `.env` file:
```
GOOGLE_API_KEY=your-api-key-here
```

## Quick Start Checklist

Before running the full agent:

- [x] Install dependencies (`pip install -r requirements.txt`)
- [x] Connect Android device/emulator (`adb devices`)
- [ ] Install droidrun helper APK on device
- [ ] Grant necessary permissions
- [ ] Configure `config.json` with your details
- [ ] Place resume PDF on device
- [ ] Log into all job apps on device
- [ ] Join WhatsApp groups
- [ ] Test with simple script first

## Still Having Issues?

1. **Check droidrun documentation**: The framework may have specific setup requirements
2. **Use an older Android version**: Some emulator versions work better (API 30-33)
3. **Try with a real device**: Physical devices sometimes work better than emulators
4. **Check logs**: Look for more detailed error messages in the console

## Simplified Version

If you're having persistent issues with droidrun, consider:
1. Starting with a simpler automation approach
2. Using manual intervention for complex steps
3. Testing each platform agent individually
4. Reducing the number of enabled platforms in `config.json`
