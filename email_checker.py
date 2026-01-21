"""
Email Checker Module
Checks email for job application responses and updates job tracker.
"""
from typing import Dict, List
from droidrun import DroidAgent, DroidrunConfig, AdbTools


class EmailChecker:
    """Checks email for job application updates."""
    
    def __init__(self, tools: AdbTools, config: DroidrunConfig, llm, job_tracker):
        """
        Initialize email checker.
        
        Args:
            tools: AdbTools instance
            config: DroidrunConfig instance
            llm: Language model instance
            job_tracker: JobTracker instance
        """
        self.tools = tools
        self.config = config
        self.llm = llm
        self.job_tracker = job_tracker
    
    async def check_emails(self) -> Dict:
        """
        Check emails for job application responses.
        
        Returns:
            Dictionary with results
        """
        print(f"\n{'='*60}")
        print(f"📧 Checking Email for Job Updates")
        print(f"{'='*60}\n")
        
        results = {
            'emails_checked': 0,
            'updates_found': 0,
            'interviews': 0,
            'rejections': 0,
            'errors': []
        }
        
        try:
            await self._open_gmail()
            emails = await self._search_job_emails()
            
            results['emails_checked'] = len(emails)
            
            for email in emails:
                update_type = self._classify_email(email)
                
                if update_type:
                    results['updates_found'] += 1
                    
                    if update_type == 'interview':
                        results['interviews'] += 1
                    elif update_type == 'rejection':
                        results['rejections'] += 1
                    
                    # Update job tracker
                    # Note: You'd need to match email to application ID
                    print(f"📨 Found {update_type}: {email.get('subject', 'Unknown')}")
        
        except Exception as e:
            print(f"❌ Email checker error: {e}")
            results['errors'].append(str(e))
        
        return results
    
    async def _open_gmail(self):
        """Open Gmail app."""
        agent = DroidAgent(
            goal="""
            1. Open the Gmail app
            2. Wait for the app to load
            3. Navigate to the Primary inbox
            """,
            config=self.config,
            tools=self.tools,
            llms=self.llm
        )
        await agent.run()
        print("✅ Opened Gmail")
    
    async def _search_job_emails(self) -> List[Dict]:
        """
        Search for job-related emails.
        
        Returns:
            List of email dictionaries
        """
        agent = DroidAgent(
            goal="""
            1. Tap on the search bar
            2. Search for emails containing keywords: "application", "interview", "job", "position"
            3. Filter to show emails from the last 7 days
            4. Scroll through search results
            5. Extract email subjects and senders
            """,
            config=self.config,
            tools=self.tools,
            llms=self.llm
        )
        await agent.run()
        
        # TODO: Implement actual email extraction
        emails = []
        print("✅ Searched for job-related emails")
        return emails
    
    def _classify_email(self, email: Dict) -> str:
        """
        Classify email type based on content.
        
        Args:
            email: Email dictionary with subject and body
            
        Returns:
            Email type: 'interview', 'rejection', 'offer', or None
        """
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()
        
        combined_text = f"{subject} {body}"
        
        # Interview keywords
        if any(keyword in combined_text for keyword in [
            'interview', 'schedule', 'meet', 'discuss', 'round', 'assessment'
        ]):
            return 'interview'
        
        # Rejection keywords
        if any(keyword in combined_text for keyword in [
            'regret', 'unfortunately', 'not selected', 'not moving forward', 'rejected'
        ]):
            return 'rejection'
        
        # Offer keywords
        if any(keyword in combined_text for keyword in [
            'offer', 'congratulations', 'selected', 'pleased to inform'
        ]):
            return 'offer'
        
        return None
