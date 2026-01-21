"""
LinkedIn Job Application Agent
Automates job search and application on LinkedIn mobile app.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from droidrun import DroidAgent, DroidrunConfig, AdbTools


class JobListing(BaseModel):
    """Single job listing data model."""
    job_title: str = Field(description="The title of the job position")
    company: str = Field(description="The name of the company offering the job")
    location: str = Field(description="The location of the job (city, state, or 'Remote')")
    description: str = Field(description="Brief description or summary of the job", default="")


class JobSearchResults(BaseModel):
    """Job search results containing multiple job listings."""
    jobs: List[JobListing] = Field(description="List of job listings found in the search results")


class ApplicationConfirmation(BaseModel):
    """Application submission confirmation."""
    success: bool = Field(description="Whether the application was successfully submitted")
    message: str = Field(description="Confirmation message or description of what was observed")


class LinkedInAgent:
    """Agent for LinkedIn job applications."""
    
    def __init__(self, tools: AdbTools, config: DroidrunConfig, llm, job_tracker, profile_matcher, app_config: Dict):
        """
        Initialize LinkedIn agent.
        
        Args:
            tools: AdbTools instance
            config: DroidrunConfig instance
            llm: Language model instance
            job_tracker: JobTracker instance
            profile_matcher: ProfileMatcher instance
            app_config: Application configuration dictionary
        """
        self.tools = tools
        self.config = config
        self.llm = llm
        self.job_tracker = job_tracker
        self.profile_matcher = profile_matcher
        self.app_config = app_config
        self.platform_name = "LinkedIn"
        
        # Platform-specific settings
        self.platform_config = app_config.get('platforms', {}).get('linkedin', {})
        self.max_applications = self.platform_config.get('max_applications_per_session', 10)
        self.search_keywords = self.platform_config.get('search_keywords', 'Software Developer Intern')
        
        self.applications_count = 0
    
    async def search_and_apply(self) -> Dict:
        """
        Main method to search for jobs and apply.
        
        Returns:
            Dictionary with results summary
        """
        print(f"\n{'='*60}")
        print(f"🔵 Starting LinkedIn Job Search")
        print(f"{'='*60}\n")
        
        results = {
            'platform': self.platform_name,
            'jobs_found': 0,
            'jobs_matched': 0,
            'applications_submitted': 0,
            'errors': []
        }
        
        try:
            # Step 1: Open LinkedIn and navigate to Jobs
            await self._open_linkedin_jobs()
            
            # Step 2: Search for jobs
            jobs = await self._search_jobs()
            results['jobs_found'] = len(jobs)
            
            # Step 3: Filter jobs using profile matcher
            matched_jobs = self.profile_matcher.filter_and_rank(jobs, limit=self.max_applications)
            results['jobs_matched'] = len(matched_jobs)
            
            print(f"📊 Found {len(jobs)} jobs, {len(matched_jobs)} matched criteria")
            
            # Step 4: Apply to matched jobs
            for job in matched_jobs:
                if self.applications_count >= self.max_applications:
                    print(f"⚠️ Reached maximum applications limit ({self.max_applications})")
                    break
                
                # Check if already applied
                if self.job_tracker.check_already_applied(
                    job.get('company', ''),
                    job.get('job_title', ''),
                    self.platform_name
                ):
                    print(f"⏭️ Already applied: {job.get('job_title')} at {job.get('company')}")
                    continue
                
                # Apply to job
                success = await self._apply_to_job(job)
                
                if success:
                    results['applications_submitted'] += 1
                    self.applications_count += 1
                    
                    # Add to tracker
                    job['platform'] = self.platform_name
                    job['status'] = 'Applied'
                    self.job_tracker.add_job_application(job)
                    
                    print(f"✅ Applied {self.applications_count}/{self.max_applications}")
                else:
                    results['errors'].append(f"Failed to apply: {job.get('job_title')}")
        
        except Exception as e:
            print(f"❌ LinkedIn agent error: {e}")
            results['errors'].append(str(e))
        
        return results
    
    async def _open_linkedin_jobs(self):
        """Open LinkedIn app and navigate to Jobs section."""
        agent = DroidAgent(
            goal="""
            1. Open the LinkedIn app
            2. Wait for it to load completely
            3. Tap on the "Jobs" icon/tab at the bottom navigation
            4. Wait for Jobs page to load
            """,
            config=self.config,
            tools=self.tools,
            llms=self.llm
        )
        await agent.run()
        print("✅ Opened LinkedIn Jobs")
    
    async def _search_jobs(self) -> List[Dict]:
        """
        Search for jobs using configured keywords.
        
        Returns:
            List of job dictionaries
        """
        # Use DroidAgent with structured output to search and extract job listings
        agent = DroidAgent(
            goal=f"""
            Search for jobs on LinkedIn and collect job information:
            
            1. Tap on the search bar at the top of the LinkedIn Jobs page.
            2. Type "{self.search_keywords}" in the search field.
            3. Apply relevant filters (Entry level, Internship, Remote if available).
            4. Execute the search by tapping the search button.
            5. Wait for the search results to load completely.
            6. Carefully read and observe the job listings displayed on the screen.
            7. For EACH job listing you see (aim for 5 jobs), observe and note:
               - The job title
               - The company name
               - The job location
               - Any brief description or details visible
            8. Scroll down to see more job listings if needed to gather enough information.
            9. After collecting information about the jobs, describe all the jobs you found.
            
            Important: Do NOT try to manually extract data from ui_state or access specific indices.
            Just read the screen naturally and describe what job listings you see.
            """,
            config=self.config,
            tools=self.tools,
            llms=self.llm,
            output_model=JobSearchResults
        )
        
        result = await agent.run()
        
        # Extract jobs from structured output
        jobs = []
        if result.success and result.structured_output:
            job_search_results: JobSearchResults = result.structured_output
            # Convert Pydantic models to dictionaries and ensure no None values
            jobs = []
            for job in job_search_results.jobs:
                job_dict = job.model_dump()
                # Ensure description is never None
                if job_dict.get('description') is None:
                    job_dict['description'] = ''
                jobs.append(job_dict)
            print(f"✅ Extracted {len(jobs)} jobs from LinkedIn search using structured output.")
        else:
            print(f"⚠️ Failed to extract jobs. Reason: {result.reason}")
        
        return jobs
    
    async def _apply_to_job(self, job: Dict) -> bool:
        """
        Apply to a specific job.
        
        Args:
            job: Job dictionary with details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n📝 Applying to: {job.get('job_title')} at {job.get('company')}")
            
            # resume_path = self.app_config.get('user_profile', {}).get('resume_path', '/sdcard/Documents/resume.pdf')
            
            agent = DroidAgent(
                goal=f"""
                1. From the LinkedIn jobs page, search for the job titled "{job.get('job_title')}" at "{job.get('company')}".
                2. Tap on the correct job listing from the search results to view its details.
                3. Find and tap the "Apply" or "Simple Apply" button.
                4. Follow the application flow. The application may have multiple steps , it may or may not be a google form.
                5. Fill in all required fields using the user's profile information.
                   - if asked for name , use "Aditya Sharma"
                   - if asked for email , use "adishasharma14@gmail.com" or if already filled, verify it's correct.
                   - if asked for phone number , use "1234567890"                  
                   - if asked for job position or related info, use the job title from the listing.
                   - If asked for a resume, upload it from: 'open my files app > search for resume.pdf > select the file'.
                   - If asked for experience level, select "Entry level" or "Internship".
                   - if anything else is asked, use generic but relevant info.
                6. Review all details carefully before submitting.
                7. Tap the final "Submit application" or any similar button.
                8. After submitting, carefully look for a confirmation message like "Application submitted" or "Application sent".
                9. Report whether you successfully submitted the application and describe what confirmation you saw.
                10. If you see a job application submitted , go back to the main jobs page [on linkedin] to continue applying to more jobs.
                """,
                config=self.config,
                tools=self.tools,
                llms=self.llm,
                output_model=ApplicationConfirmation
            )
            
            result = await agent.run()
            
            # Check for confirmation from structured output
            if result.success and result.structured_output:
                confirmation: ApplicationConfirmation = result.structured_output
                if confirmation.success:
                    print(f"✅ Successfully applied to {job.get('job_title')}")
                    print(f"   Confirmation: {confirmation.message}")
                    return True
                else:
                    print(f"⚠️ Application not confirmed for {job.get('job_title')}")
                    print(f"   Message: {confirmation.message}")
                    return False
            else:
                print(f"❌ Failed to complete application for {job.get('job_title')}")
                print(f"   Reason: {result.reason}")
                return False
            
        except Exception as e:
            print(f"❌ Error applying to job: {e}")
            return False
