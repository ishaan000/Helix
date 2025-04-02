from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
import logging
import requests
from bs4 import BeautifulSoup
import json

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_professionals(
    query: str,
    location: Optional[str] = None,
    years_experience: Optional[int] = None,
    skills: Optional[List[str]] = None,
    current_company: Optional[str] = None
) -> Dict:
    """
    Search for potential employers and networking contacts using LinkedIn.
    
    Args:
        query (str): The search query (e.g., "hiring manager", "engineering director")
        location (Optional[str]): Location to search in (e.g., "San Francisco")
        years_experience (Optional[int]): Minimum years of experience
        skills (Optional[List[str]]): List of relevant skills
        current_company (Optional[str]): Target company name
    
    Returns:
        Dict: Search results containing professional profiles
    """
    try:
        # Build a more targeted LinkedIn search query
        linkedin_query = f"{query} site:linkedin.com/in/"
        
        # Add location if specified
        if location:
            linkedin_query += f" in {location}"
            
        # Add current company if specified
        if current_company:
            linkedin_query += f" at {current_company}"
            
        # Add experience if specified
        if years_experience:
            linkedin_query += f" {years_experience}+ years experience"
            
        # Add skills if specified
        if skills:
            linkedin_query += f" {' OR '.join(skills)}"
            
        params = {
            "engine": "google",
            "q": linkedin_query,
            "api_key": os.getenv("SERPAPI_KEY"),
            "num": 10,
            "gl": "us",  # Set to US for better results
            "hl": "en"   # Set to English
        }
        
        logger.info(f"Making LinkedIn search request with query: {linkedin_query}")
        search = GoogleSearch(params)
        search_results = search.get_dict()
        
        professionals = []
        if "organic_results" in search_results:
            for result in search_results["organic_results"]:
                if "linkedin.com/in/" in result.get("link", ""):
                    # Extract name and clean it
                    title = result.get("title", "")
                    name = title.split(" | ")[0] if " | " in title else title
                    
                    # Extract current position if available
                    snippet = result.get("snippet", "")
                    current_position = extract_current_position(snippet)
                    
                    professional = {
                        "name": name,
                        "link": result.get("link", ""),
                        "snippet": snippet,
                        "source": "LinkedIn",
                        "type": "profile",
                        "current_position": current_position
                    }
                    
                    # Add experience if mentioned
                    if years_experience:
                        professional["years_experience"] = extract_years_experience(snippet)
                    
                    # Add skills if mentioned
                    if skills:
                        professional["matched_skills"] = [skill for skill in skills if skill.lower() in snippet.lower()]
                    
                    professionals.append(professional)
        
        # Filter out job listings and invalid profiles
        filtered_professionals = [
            prof for prof in professionals
            if not any(term in prof["snippet"].lower() for term in ["job", "career", "hiring", "apply now"])
            and prof["name"] != "LinkedIn"
        ]
        
        return {
            "query": query,
            "professionals": filtered_professionals,
            "total_found": len(filtered_professionals)
        }
        
    except Exception as e:
        logger.error(f"Error in search_professionals: {str(e)}", exc_info=True)
        return {
            "query": query,
            "professionals": [],
            "total_found": 0
        }

def extract_current_position(snippet: str) -> str:
    """Extract current position from LinkedIn snippet."""
    try:
        # Look for position at the start of the snippet
        lines = snippet.split("\n")
        for line in lines:
            if any(term in line.lower() for term in ["at ", "currently ", "presently "]):
                return line.strip()
        return ""
    except:
        return ""

def extract_years_experience(snippet: str) -> Optional[int]:
    """Extract years of experience from text snippet."""
    try:
        # Simple regex pattern for years of experience
        import re
        pattern = r"(\d+)\+?\s*(?:year|yr)s?\s*(?:of\s*)?experience"
        match = re.search(pattern, snippet.lower())
        if match:
            return int(match.group(1))
    except:
        pass
    return None

def get_professional_details(profile_url: str) -> Dict:
    """
    Get detailed information about a professional from their profile URL.
    
    Args:
        profile_url (str): URL of the professional's profile
    
    Returns:
        Dict: Detailed information about the professional
    """
    try:
        params = {
            "engine": "google",
            "q": f"site:{profile_url}",
            "api_key": os.getenv("SERPAPI_KEY")
        }
        
        logger.info(f"Making SerpAPI request for profile: {profile_url}")
        search = GoogleSearch(params)
        search_results = search.get_dict()
        
        # Extract relevant information with better error handling
        organic_results = search_results.get("organic_results", [])
        if not organic_results:
            logger.warning(f"No organic results found for profile: {profile_url}")
            return {
                "url": profile_url,
                "content": "",
                "title": ""
            }
            
        first_result = organic_results[0]
        details = {
            "url": profile_url,
            "content": first_result.get("snippet", ""),
            "title": first_result.get("title", "")
        }
        
        return details
        
    except Exception as e:
        logger.error(f"Error in get_professional_details: {str(e)}", exc_info=True)
        return {
            "url": profile_url,
            "content": "",
            "title": ""
        } 