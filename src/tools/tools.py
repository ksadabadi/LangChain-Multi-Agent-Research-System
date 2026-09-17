from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """
    Perform a web search using the Tavily API.

    Args:
        query (str): The search query.

    Returns:
        str: The search results.
    """
    try:
        response = tavily_client.search(query=query, max_results=5)
        out = []
        for result in response['results']:
            out.append(f"Title: {result['title']}\nURL: {result['url']}\nSnippet: {result['content'][:300]}\n")

        return "\n----\n".join(out)
    
    except Exception as e:
        return f"An error occurred while performing the web search: {str(e)}"

@tool
def scrape_url(url: str) -> str:
    """
    Scrape the content of a given URL.
    Scrape and extract clean readable content from the provided URL
    Uses requests to fetch the page, readability to extract the main content, and BeautifulSoup to clean up the HTML.

    Args:
        url (str): The URL to scrape.

    Returns:
        str: The scraped content.
    """
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/124.0 Safari/537.36"
                       ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referrer": "https://www.google.com/",

    }

    try:
        # ---- Fetch the page content using requests ----
        response = requests.get(url=url, 
                                headers=headers,
                                timeout=15)

        response.raise_for_status()  # Raise an error for bad responses

        html = response.text

        # ------------------------------------------------------------------------
        # Strategy 1: Use trafilatura for extraction (BEST for articles and blogs)
        # -----------------------------------------------------------------------

        extracted_content = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False
            )

        if extracted_content and len(extracted_content) > 200:
            cleaned_content = re.sub(r'\s+', ' ', extracted_content)
            return cleaned_content[:5000]  # Limit to first 5000 characters

        # ------------------------------------------------------------------------
        # Strategy 2: Use readability and BeautifulSoup for extraction
        # -----------------------------------------------------------------------
        
        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, 'html.parser')

        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
            tag.decompose()

        text = soup.get_text(separator=' ', strip=True)

        if text and len(text.strip()) > 200:
            cleaned_text = re.sub(r'\s+', ' ', text)
            return cleaned_text[:5000]  # Limit to first 5000 characters

        # ------------------------------------------------------------------------
        # Strategy 3: Fallback full page extraction
        # -----------------------------------------------------------------------

        soup = BeautifulSoup(html, 'html.parser')

        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
            tag.decompose()

        full_text = soup.get_text(separator=' ', strip=True)

        cleaned_full_text = re.sub(r'\s+', ' ', full_text)

        if cleaned_full_text:
            return cleaned_full_text[:5000]  # Limit to first 5000 characters

        return "No readable content could be extracted from the URL."
        
    except requests.exceptions.Timeout:
        return f"Request timed out while scraping the {url}. Please try again later."

    except requests.exceptions.HTTPError as e:
        return f"HTTP error occurred while scraping the {url}: {str(e)}"

    except Exception as e:
        return f"An unexpected error occurred while scraping the {url}: {str(e)}"