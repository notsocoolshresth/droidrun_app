"""
Simple test script for droidrun setup
Tests basic Android automation before running the full job application agent
"""
import asyncio
import os
from droidrun import AdbTools, DroidAgent, DroidrunConfig
from llama_index.llms.google_genai import GoogleGenAI


async def test_basic_connection():
    """Test if droidrun can connect to the device."""
    print("🔧 Testing ADB connection...")
    try:
        tools = AdbTools()
        print("✅ AdbTools initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize AdbTools: {e}")
        return False


async def test_simple_action():
    """Test a simple action on the device."""
    print("\n🔧 Testing simple automation...")
    try:
        os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "HARDCODED_API_KEY")
        
        tools = AdbTools()
        config = DroidrunConfig()
        llm = GoogleGenAI(model="gemini-2.5-flash", temperature=0.2)
        
        agent = DroidAgent(
            goal="Open the Settings app and wait for it to load",
            config=config,
            tools=tools,
            llms=llm
        )
        
        print("🚀 Running test agent...")
        await agent.run()
        print("✅ Test agent completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"\nError type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("="*60)
    print("🧪 DROIDRUN SETUP TEST")
    print("="*60)
    print("\nThis script tests if droidrun is properly configured.\n")
    
    # Test 1: Basic connection
    test1 = await test_basic_connection()
    
    if not test1:
        print("\n⚠️ Basic connection failed. Please check:")
        print("1. Is your Android device/emulator connected? (run: adb devices)")
        print("2. Is ADB working properly?")
        print("3. Are the necessary permissions granted?")
        return
    
    # Test 2: Simple automation
    test2 = await test_simple_action()
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    print(f"Basic Connection: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Simple Automation: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 All tests passed! You can now run the full agent:")
        print("   python app.py")
    else:
        print("\n⚠️ Some tests failed. Check TROUBLESHOOTING.md for help")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())