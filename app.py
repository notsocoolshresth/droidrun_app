"""
Job Application Automation Agent
Main orchestrator for automated job searching and applications.

DISCLAIMER: This is for educational and hackathon purposes only.
Not intended for commercial use. Always comply with platform terms of service.
"""
import asyncio
import os
import json
from datetime import datetime
from droidrun import AdbTools, DroidAgent, DroidrunConfig
from llama_index.llms.google_genai import GoogleGenAI

# Import utility modules
from job_tracker import JobTracker
from profile_matcher import ProfileMatcher
from email_checker import EmailChecker

# Import platform agents
from agents.linkedin_agent import LinkedInAgent
from agents.naukri_agent import NaukriAgent
from agents.indeed_agent import IndeedAgent
from agents.unstop_agent import UnstopAgent
from agents.whatsapp_agent import WhatsAppAgent


def load_config(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ Loaded configuration from {config_path}")
        return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        raise


def print_banner():
    """Print application banner."""
    print("\n" + "="*70)
    print("🤖 JOB APPLICATION AUTOMATION AGENT")
    print("="*70)
    print("⚠️  EDUCATIONAL USE ONLY - Hackathon Project")
    print("="*70 + "\n")


def print_summary(all_results: dict):
    """Print summary of all results."""
    print("\n" + "="*70)
    print("📊 APPLICATION SESSION SUMMARY")
    print("="*70)
    
    total_jobs = 0
    total_applications = 0
    
    for platform, results in all_results.items():
        if platform == 'email':
            continue
        
        print(f"\n{platform}:")
        print(f"  Jobs Found: {results.get('jobs_found', 0)}")
        print(f"  Jobs Matched: {results.get('jobs_matched', 0)}")
        print(f"  Applications Submitted: {results.get('applications_submitted', 0)}")
        
        if results.get('errors'):
            print(f"  Errors: {len(results['errors'])}")
        
        total_jobs += results.get('jobs_found', 0)
        total_applications += results.get('applications_submitted', 0)
    
    # Email results
    if 'email' in all_results:
        email_results = all_results['email']
        print(f"\nEmail Updates:")
        print(f"  Emails Checked: {email_results.get('emails_checked', 0)}")
        print(f"  Interview Invites: {email_results.get('interviews', 0)}")
        print(f"  Rejections: {email_results.get('rejections', 0)}")
    
    print(f"\n{'='*70}")
    print(f"TOTAL JOBS FOUND: {total_jobs}")
    print(f"TOTAL APPLICATIONS SUBMITTED: {total_applications}")
    print(f"{'='*70}\n")


async def main():
    """Main function to run the job application agent."""
    # Print banner
    print_banner()
    
    # Load configuration
    config_data = load_config()
    
    # Set up Google API key
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "HARDCODED_API_KEY")
    
    # Initialize tools and config
    print("🔧 Initializing tools...")
    tools = AdbTools()
    config = DroidrunConfig()
    config.agent.max_steps = 30  # Increase max steps from default 15 to 30
    llm = GoogleGenAI(model="gemini-2.5-flash", temperature=0.2)
    
    # Initialize job tracker
    print("📋 Initializing job tracker...")
    excel_path = config_data.get('tracking', {}).get('excel_file_path', 'job_applications.xlsx')
    job_tracker = JobTracker(excel_path)
    
    # Initialize profile matcher
    print("🎯 Initializing profile matcher...")
    profile_matcher = ProfileMatcher(config_data)
    
    # Get application stats
    stats = job_tracker.get_application_stats()
    print(f"\n📈 Current Application Stats:")
    print(f"  Total Applications: {stats['total']}")
    print(f"  Applied: {stats['applied']}")
    print(f"  Interview Stage: {stats['interview']}")
    print(f"  Rejected: {stats['rejected']}\n")
    
    # Track all results
    all_results = {}
    
    # Get enabled platforms
    platforms_config = config_data.get('platforms', {})
    
    try:
        # LinkedIn
        if platforms_config.get('linkedin', {}).get('enabled', True):
            print("\n🚀 Running LinkedIn Agent...")
            linkedin_agent = LinkedInAgent(tools, config, llm, job_tracker, profile_matcher, config_data)
            all_results['LinkedIn'] = await linkedin_agent.search_and_apply()
            await asyncio.sleep(30)  # Delay between platforms
        
        # Naukri
        # if platforms_config.get('naukri', {}).get('enabled', True):
        #     print("\n🚀 Running Naukri Agent...")
        #     naukri_agent = NaukriAgent(tools, config, llm, job_tracker, profile_matcher, config_data)
        #     all_results['Naukri'] = await naukri_agent.search_and_apply()
        #     await asyncio.sleep(30)
        
        # # Indeed
        # if platforms_config.get('indeed', {}).get('enabled', True):
        #     print("\n🚀 Running Indeed Agent...")
        #     indeed_agent = IndeedAgent(tools, config, llm, job_tracker, profile_matcher, config_data)
        #     all_results['Indeed'] = await indeed_agent.search_and_apply()
        #     await asyncio.sleep(30)
        
        # # Unstop
        # if platforms_config.get('unstop', {}).get('enabled', True):
        #     print("\n🚀 Running Unstop Agent...")
        #     unstop_agent = UnstopAgent(tools, config, llm, job_tracker, profile_matcher, config_data)
        #     all_results['Unstop'] = await unstop_agent.search_and_apply()
        #     await asyncio.sleep(30)
        
        # # WhatsApp
        # if platforms_config.get('whatsapp', {}).get('enabled', True):
        #     print("\n🚀 Running WhatsApp Scanner...")
        #     whatsapp_agent = WhatsAppAgent(tools, config, llm, job_tracker, profile_matcher, config_data)
        #     all_results['WhatsApp'] = await whatsapp_agent.scan_groups()
        #     await asyncio.sleep(30)
        
        # Email Checker
        print("\n🚀 Checking Email...")
        email_checker = EmailChecker(tools, config, llm, job_tracker)
        all_results['email'] = await email_checker.check_emails()
        
    except KeyboardInterrupt:
        print("\n⚠️ Agent interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close job tracker
        job_tracker.close()
        
        # Print summary
        print_summary(all_results)
        
        print("✅ Job Application Agent Session Complete")
        print(f"📅 Session ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    asyncio.run(main())