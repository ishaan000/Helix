from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
import logging

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_professionals(query: str, location: Optional[str] = None) -> Dict:
    """
    Search for professionals using SerpAPI.
    
    Args:
        query (str): The search query (e.g., "top designers", "founding engineers")
        location (Optional[str]): Location to search in (e.g., "San Francisco")
    
    Returns:
        Dict: Search results containing professional profiles
    """
    try:
        search_query = f"{query}"
        if location:
            search_query += f" in {location}"
        
        params = {
            "engine": "google",
            "q": search_query,
            "api_key": os.getenv("SERPAPI_KEY"),
            "num": 10  # Limit to top 10 results
        }
        
        logger.info(f"Making SerpAPI request with query: {search_query}")
        search = GoogleSearch(params)
        search_results = search.get_dict()
        
        # Log the raw results for debugging
        logger.info(f"Raw SerpAPI response: {search_results}")
        
        # Extract relevant information from results
        professionals = []
        if "organic_results" in search_results and isinstance(search_results["organic_results"], list):
            for search_result in search_results["organic_results"]:
                if isinstance(search_result, dict):
                    professional = {
                        "name": search_result.get("title", ""),
                        "link": search_result.get("link", ""),
                        "snippet": search_result.get("snippet", ""),
                        "source": search_result.get("source", "")
                    }
                    professionals.append(professional)
        
        logger.info(f"Found {len(professionals)} professionals")
        return {
            "query": search_query,
            "professionals": professionals
        }
        
    except Exception as e:
        logger.error(f"Error in search_professionals: {str(e)}", exc_info=True)
        return {
            "query": search_query,
            "professionals": []
        }

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
        
        # Log the raw results for debugging
        logger.info(f"Raw SerpAPI response: {search_results}")
        
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