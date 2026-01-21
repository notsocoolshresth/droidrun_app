"""
Profile Matcher Module
Matches job descriptions against user preferences and calculates relevance scores.
"""
import re
from typing import Dict, List, Tuple


class ProfileMatcher:
    """Matches jobs against user profile and preferences."""
    
    def __init__(self, config: Dict):
        """
        Initialize the profile matcher.
        
        Args:
            config: Configuration dictionary with job preferences
        """
        self.job_preferences = config.get('job_preferences', {})
        self.user_profile = config.get('user_profile', {})
        
        # Normalize keywords for matching
        self.job_titles = [title.lower() for title in self.job_preferences.get('job_titles', [])]
        self.keywords = [kw.lower() for kw in self.job_preferences.get('keywords', [])]
        self.locations = [loc.lower() for loc in self.job_preferences.get('locations', [])]
        self.excluded_keywords = [kw.lower() for kw in self.job_preferences.get('excluded_keywords', [])]
        
        self.min_experience = self.job_preferences.get('experience_range', {}).get('min_years', 0)
        self.max_experience = self.job_preferences.get('experience_range', {}).get('max_years', 1)
    
    def match_job(self, job_data: Dict) -> Tuple[bool, float, str]:
        """
        Check if a job matches user preferences and calculate relevance score.
        
        Args:
            job_data: Dictionary containing job information
                - job_title: str
                - company: str
                - location: str
                - description: str
                - experience: str (e.g., "0-1 years", "Fresher")
                
        Returns:
            Tuple of (is_match: bool, score: float, reason: str)
        """
        job_title = job_data.get('job_title', '').lower()
        job_description = job_data.get('description', '').lower()
        location = job_data.get('location', '').lower()
        experience = job_data.get('experience', '').lower()
        
        score = 0.0
        reasons = []
        
        # Check excluded keywords first (immediate rejection)
        for excluded in self.excluded_keywords:
            if excluded in job_title or excluded in job_description:
                return False, 0.0, f"Contains excluded keyword: '{excluded}'"
        
        # Check experience requirements
        if not self._match_experience(experience):
            return False, 0.0, f"Experience requirement doesn't match: {experience}"
        
        # Score job title match
        title_score = 0
        for preferred_title in self.job_titles:
            if preferred_title in job_title:
                title_score = 30.0
                reasons.append(f"Title matches: {preferred_title}")
                break
        
        if title_score == 0:
            # Partial title match
            for preferred_title in self.job_titles:
                title_words = preferred_title.split()
                if any(word in job_title for word in title_words if len(word) > 3):
                    title_score = 15.0
                    reasons.append(f"Partial title match")
                    break
        
        score += title_score
        
        # Score keyword matches in description
        keyword_matches = 0
        matched_keywords = []
        for keyword in self.keywords:
            if keyword in job_description or keyword in job_title:
                keyword_matches += 1
                matched_keywords.append(keyword)
        
        keyword_score = min(keyword_matches * 5, 40.0)  # Max 40 points for keywords
        score += keyword_score
        if matched_keywords:
            reasons.append(f"Keywords found: {', '.join(matched_keywords[:5])}")
        
        # Score location match
        location_score = 0
        for preferred_loc in self.locations:
            if preferred_loc in location:
                location_score = 20.0
                reasons.append(f"Location matches: {preferred_loc}")
                break
        
        score += location_score
        
        # Bonus for internship/entry-level keywords
        entry_keywords = ['intern', 'internship', 'fresher', 'entry level', 'graduate']
        for entry_kw in entry_keywords:
            if entry_kw in job_title or entry_kw in job_description:
                score += 10.0
                reasons.append("Entry-level position")
                break
        
        # Determine if it's a match (minimum 40 points)
        threshold = 40.0
        is_match = score >= threshold
        
        if is_match:
            reason_str = " | ".join(reasons) if reasons else "General match"
        else:
            reason_str = f"Score too low ({score:.1f} < {threshold})"
        
        return is_match, score, reason_str
    
    def _match_experience(self, experience_text: str) -> bool:
        """
        Check if experience requirement matches user's experience range.
        
        Args:
            experience_text: Experience requirement text
            
        Returns:
            True if matches, False otherwise
        """
        experience_text = experience_text.lower()
        
        # Check for fresher/entry-level keywords
        if any(keyword in experience_text for keyword in ['fresher', 'no experience', 'entry level', '0 year']):
            return True
        
        # Check for internship
        if 'intern' in experience_text:
            return True
        
        # Extract years using regex
        year_pattern = r'(\d+)\s*[-to]*\s*(\d*)\s*year'
        matches = re.findall(year_pattern, experience_text)
        
        if matches:
            for match in matches:
                min_years = int(match[0])
                max_years = int(match[1]) if match[1] else min_years
                
                # Check if our experience range overlaps with requirement
                if (min_years <= self.max_experience and 
                    max_years >= self.min_experience):
                    return True
            return False
        
        # If no years found but contains "experience", consider it uncertain (allow it)
        if 'experience' in experience_text:
            return True
        
        # Default to True if we can't determine
        return True
    
    def rank_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Rank a list of jobs by relevance score.
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Sorted list of jobs with scores
        """
        scored_jobs = []
        
        for job in jobs:
            is_match, score, reason = self.match_job(job)
            if is_match:
                job['match_score'] = score
                job['match_reason'] = reason
                scored_jobs.append(job)
        
        # Sort by score descending
        scored_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return scored_jobs
    
    def filter_and_rank(self, jobs: List[Dict], limit: int = None) -> List[Dict]:
        """
        Filter matching jobs and return top N ranked results.
        
        Args:
            jobs: List of job dictionaries
            limit: Maximum number of results to return
            
        Returns:
            Filtered and ranked job list
        """
        ranked_jobs = self.rank_jobs(jobs)
        
        if limit:
            return ranked_jobs[:limit]
        
        return ranked_jobs
