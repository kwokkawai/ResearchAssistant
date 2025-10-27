#!/usr/bin/env python3
"""
Web Search Module for Deep Research
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import re

class WebSearchProvider:
    """Base class for web search providers"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Perform web search and return results"""
        raise NotImplementedError

class GoogleSearchProvider(WebSearchProvider):
    """Google Search provider using Custom Search API"""
    
    def __init__(self, api_key: str = None, search_engine_id: str = None):
        super().__init__(api_key)
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API with pagination support"""
        # Validate num_results parameter
        if num_results is None:
            num_results = 10
        elif not isinstance(num_results, int) or num_results <= 0:
            num_results = 10
            
        if not self.api_key or not self.search_engine_id:
            print("Google Search API key or search engine ID not provided, using fallback")
            return self._fallback_search(query, num_results)
        
        try:
            results = []
            # Google API allows max 10 results per request
            # To get more, we need to paginate
            max_per_request = 10
            remaining = num_results
            
            start_index = 1
            while remaining > 0:
                # Determine how many results to request in this iteration
                results_to_get = min(remaining, max_per_request)
                
                params = {
                    'key': self.api_key,
                    'cx': self.search_engine_id,
                    'q': query,
                    'num': results_to_get,
                    'start': start_index
                }
                
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                items = data.get('items', [])
                
                # If no more items available, break
                if not items:
                    break
                
                for item in items:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'Google'
                    })
                
                # Check if we got all requested results
                if len(items) < results_to_get:
                    # No more results available
                    break
                
                # Prepare for next page
                remaining -= len(items)
                start_index += results_to_get
                
                # Safety check: limit total pagination to avoid excessive API calls
                if len(results) >= num_results or start_index > 100:
                    break
            
            print(f"Google Search: Retrieved {len(results)} results (requested {num_results})")
            return results[:num_results]
            
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                print("Google Search API Error: 403 Forbidden")
                print("This usually means:")
                print("- API key is invalid or disabled")
                print("- Custom Search API is not enabled")
                print("- Daily/monthly quota exceeded")
                print("- API key has IP/domain restrictions")
                print("- Search engine ID is invalid")
                print("Falling back to DuckDuckGo search...")
            else:
                print(f"Google search error: {e}")
            return self._fallback_search(query, num_results)
    
    def _fallback_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Fallback search using DuckDuckGo when Google API is not available"""
        try:
            # Validate num_results parameter
            if num_results is None:
                num_results = 10
            elif not isinstance(num_results, int) or num_results <= 0:
                num_results = 10
                
            # Use DuckDuckGo as fallback when Google API is not available
            from search.web_search import DuckDuckGoSearchProvider
            duckduckgo_provider = DuckDuckGoSearchProvider()
            return duckduckgo_provider.search(query, num_results)
        except Exception as e:
            print(f"Google fallback search error: {e}")
            return [{
                'title': f'Search results for: {query}',
                'url': f'https://www.google.com/search?q={quote_plus(query)}',
                'snippet': f'Search results for "{query}" - please check the link for current information',
                'source': 'Google (Fallback)'
            }]

class DuckDuckGoSearchProvider(WebSearchProvider):
    """DuckDuckGo search provider"""
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo"""
        try:
            # Validate num_results parameter
            if num_results is None:
                num_results = 10
            elif not isinstance(num_results, int) or num_results <= 0:
                num_results = 10
            
            # Use DuckDuckGo Instant Answer API
            url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
            
            response = requests.get(url, timeout=10)
            # DuckDuckGo API returns 202 for successful requests
            if response.status_code in [200, 202]:
                data = response.json()
                results = []
                
                # Add abstract if available
                if data.get('Abstract'):
                    results.append({
                        'title': data.get('Heading', query),
                        'url': data.get('AbstractURL', ''),
                        'snippet': data.get('Abstract', ''),
                        'source': 'DuckDuckGo'
                    })
                
                # Add related topics
                for topic in data.get('RelatedTopics', [])[:num_results-1]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append({
                            'title': topic.get('FirstURL', '').split('/')[-1] if topic.get('FirstURL') else 'Related Topic',
                            'url': topic.get('FirstURL', ''),
                            'snippet': topic.get('Text', ''),
                            'source': 'DuckDuckGo'
                        })
                
                # If no results from API, try web scraping fallback
                if not results:
                    results = self._web_scraping_fallback(query, num_results)
                
                return results[:num_results]
            else:
                print(f"DuckDuckGo API error: HTTP {response.status_code}")
                return self._web_scraping_fallback(query, num_results)
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            # Try web scraping fallback
            return self._web_scraping_fallback(query, num_results)
    
    def _web_scraping_fallback(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Fallback web scraping method"""
        try:
            # Validate num_results parameter
            if num_results is None:
                num_results = 10
            elif not isinstance(num_results, int) or num_results <= 0:
                num_results = 10
            import requests
            from bs4 import BeautifulSoup
            
            # Use DuckDuckGo HTML search as fallback
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
                'DNT': '1',
                'Sec-GPC': '1'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            # Initialize variables outside the if block
            result_links = []
            results = []
            
            # DuckDuckGo HTML search returns 200 or 202 for successful requests
            if response.status_code in [200, 202]:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check if we got a simplified page (no search results)
                page_title = soup.title.string if soup.title else ""
                if "DuckDuckGo" in page_title and len(response.text) < 20000:
                    print("DuckDuckGo returned simplified page (likely bot detection)")
                    return self._generate_fallback_results(query, num_results)
                
                # Try multiple selectors to find search results
                # Updated selectors for current DuckDuckGo HTML structure
                selectors = [
                    # Modern DuckDuckGo selectors
                    'a[data-testid="result-title-a"]',
                    'a[data-testid="result-title"]',
                    '.result__title a',
                    '.result__a',
                    'a.result__a',
                    'h2.result__title a',
                    
                    # Alternative selectors
                    'a[href*="http"]:not([href*="duckduckgo.com"])',
                    'a[href*="www"]:not([href*="duckduckgo.com"])',
                    'a[class*="result"]',
                    '.result .result__a',
                    'a[class*="web"]',
                    
                    # Generic link selectors (last resort)
                    'a[href^="http"]',
                    'a[href^="https"]',
                    'a[href*="://"]'
                ]
                
                for selector in selectors:
                    links = soup.select(selector)
                    if links:
                        # Filter out DuckDuckGo internal links and invalid URLs
                        filtered_links = []
                        for link in links:
                            href = link.get('href', '')
                            # Skip DuckDuckGo internal links and invalid URLs
                            if (href and 
                                not href.startswith('#') and 
                                not href.startswith('javascript:') and
                                not 'duckduckgo.com' in href and
                                not href.startswith('/') and
                                ('http' in href or 'www.' in href)):
                                filtered_links.append(link)
                        
                        if filtered_links:
                            result_links = filtered_links[:num_results]
                            print(f"Found {len(result_links)} results using selector: {selector}")
                            break
                
                if not result_links:
                    print("No search results found with any selector")
                    print(f"Page content preview: {response.text[:500]}...")
                    print("This usually means DuckDuckGo detected automated access")
                    # Return informative fallback results based on query
                    return self._generate_fallback_results(query, num_results)
                
                for link in result_links:
                    title = link.get_text().strip()
                    url = link.get('href', '')
                    
                    # Clean up URL if it's a relative DuckDuckGo redirect
                    if url.startswith('/l/?uddg='):
                        # Extract the actual URL from DuckDuckGo redirect
                        try:
                            from urllib.parse import unquote, parse_qs
                            url_part = url.split('uddg=')[1]
                            url = unquote(url_part)
                        except:
                            pass
                    
                    # Find snippet - try multiple approaches
                    snippet = ''
                    snippet_elem = link.find_next('a', class_='result__snippet')
                    if not snippet_elem:
                        snippet_elem = link.find_next(class_='result__snippet')
                    if not snippet_elem:
                        snippet_elem = link.find_next(class_='result__body')
                    if snippet_elem:
                        snippet = snippet_elem.get_text().strip()
                    
                    # Only add if we have both title and URL
                    if title and url and len(title) > 3:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': 'DuckDuckGo (Scraped)'
                        })
                
                return results[:num_results]
            else:
                print(f"DuckDuckGo HTML search error: HTTP {response.status_code}")
                return self._generate_fallback_results(query, num_results)
            
        except Exception as e:
            print(f"Web scraping fallback error: {e}")
            # Return informative fallback results
            return self._generate_fallback_results(query, num_results)
    
    def _generate_fallback_results(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Generate informative fallback results when scraping fails"""
        # Validate num_results parameter
        if num_results is None:
            num_results = 10
        elif not isinstance(num_results, int) or num_results <= 0:
            num_results = 10
            
        # Create contextually relevant fallback results based on query
        fallback_results = []
        
        # Common search patterns and their fallback URLs
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['nba', 'basketball', 'score', 'game']):
            fallback_results = [
                {
                    'title': 'NBA Scores and Schedule - ESPN',
                    'url': 'https://www.espn.com/nba/scoreboard',
                    'snippet': 'Live NBA scores, schedules, standings, and news from ESPN',
                    'source': 'DuckDuckGo (Fallback)'
                },
                {
                    'title': 'NBA Scores - CBS Sports',
                    'url': 'https://www.cbssports.com/nba/scoreboard/',
                    'snippet': 'NBA scores, standings, and game information',
                    'source': 'DuckDuckGo (Fallback)'
                },
                {
                    'title': 'NBA Games and Scores - Yahoo Sports',
                    'url': 'https://sports.yahoo.com/nba/scoreboard/',
                    'snippet': 'NBA game scores, schedules, and team statistics',
                    'source': 'DuckDuckGo (Fallback)'
                }
            ]
        elif any(keyword in query_lower for keyword in ['news', 'latest', 'today']):
            fallback_results = [
                {
                    'title': 'Latest News - Google News',
                    'url': 'https://news.google.com/',
                    'snippet': 'Latest news from around the world',
                    'source': 'DuckDuckGo (Fallback)'
                },
                {
                    'title': 'Breaking News - BBC',
                    'url': 'https://www.bbc.com/news',
                    'snippet': 'Breaking news and current events',
                    'source': 'DuckDuckGo (Fallback)'
                },
                {
                    'title': 'CNN Breaking News',
                    'url': 'https://www.cnn.com/',
                    'snippet': 'Latest breaking news and top stories',
                    'source': 'DuckDuckGo (Fallback)'
                }
            ]
        elif any(keyword in query_lower for keyword in ['weather', 'forecast']):
            fallback_results = [
                {
                    'title': 'Weather Forecast - Weather.com',
                    'url': 'https://weather.com/',
                    'snippet': 'Current weather conditions and forecasts',
                    'source': 'DuckDuckGo (Fallback)'
                },
                {
                    'title': 'Weather - AccuWeather',
                    'url': 'https://www.accuweather.com/',
                    'snippet': 'Weather forecasts and conditions',
                    'source': 'DuckDuckGo (Fallback)'
                }
            ]
        elif any(keyword in query_lower for keyword in ['python', 'programming', 'code']):
            fallback_results = [
                {
                    'title': 'Python.org - Official Python Website',
                    'url': 'https://www.python.org/',
                    'snippet': 'Official Python programming language website',
                    'source': 'DuckDuckGo (Fallback)'
                },
                {
                    'title': 'Python Documentation',
                    'url': 'https://docs.python.org/',
                    'snippet': 'Official Python documentation and tutorials',
                    'source': 'DuckDuckGo (Fallback)'
                },
                {
                    'title': 'Stack Overflow - Python',
                    'url': 'https://stackoverflow.com/questions/tagged/python',
                    'snippet': 'Python programming questions and answers',
                    'source': 'DuckDuckGo (Fallback)'
                }
            ]
        else:
            # Generic fallback with search engines
            fallback_results = [
                {
                    'title': f'Search results for: {query}',
                    'url': f'https://duckduckgo.com/?q={quote_plus(query)}',
                    'snippet': f'Search results for "{query}" - please check the link for current information',
                    'source': 'DuckDuckGo (Fallback)'
                },
                {
                    'title': f'Google Search: {query}',
                    'url': f'https://www.google.com/search?q={quote_plus(query)}',
                    'snippet': f'Google search results for "{query}"',
                    'source': 'DuckDuckGo (Fallback)'
                },
                {
                    'title': f'Bing Search: {query}',
                    'url': f'https://www.bing.com/search?q={quote_plus(query)}',
                    'snippet': f'Bing search results for "{query}"',
                    'source': 'DuckDuckGo (Fallback)'
                }
            ]
        
        return fallback_results[:num_results]

class WebSearchManager:
    """Manages web search functionality"""
    
    def __init__(self):
        self.providers = {
            'google': GoogleSearchProvider,
            'duckduckgo': DuckDuckGoSearchProvider
        }
        self.current_provider = None
    
    def set_provider(self, provider_name: str, **kwargs):
        """Set the search provider"""
        if provider_name in self.providers:
            try:
                # For Google provider, check if API credentials are available
                if provider_name == 'google':
                    api_key = kwargs.get('api_key')
                    search_engine_id = kwargs.get('search_engine_id')
                    if not api_key or not search_engine_id:
                        print(f"Google Search API credentials not provided, falling back to DuckDuckGo")
                        self.current_provider = DuckDuckGoSearchProvider()
                        return
                
                self.current_provider = self.providers[provider_name](**kwargs)
            except TypeError as e:
                print(f"Failed to initialize {provider_name} provider: {e}")
                print("Falling back to DuckDuckGo")
                self.current_provider = DuckDuckGoSearchProvider()
            except Exception as e:
                print(f"Error initializing {provider_name} provider: {e}")
                print("Falling back to DuckDuckGo")
                self.current_provider = DuckDuckGoSearchProvider()
        else:
            # Default to DuckDuckGo if provider not found
            print(f"Unknown provider '{provider_name}', using DuckDuckGo")
            self.current_provider = DuckDuckGoSearchProvider()
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Perform web search"""
        # Validate num_results parameter
        if num_results is None:
            num_results = 10
        elif not isinstance(num_results, int) or num_results <= 0:
            num_results = 10
            
        if not self.current_provider:
            self.current_provider = DuckDuckGoSearchProvider()
        
        return self.current_provider.search(query, num_results)
    
    def search_with_context(self, query: str, context: str = "", num_results: int = 10) -> List[Dict[str, Any]]:
        """Search with additional context"""
        # Validate num_results parameter
        if num_results is None:
            num_results = 10
        elif not isinstance(num_results, int) or num_results <= 0:
            num_results = 10
            
        if context:
            enhanced_query = f"{query} {context}"
        else:
            enhanced_query = query
        
        return self.search(enhanced_query, num_results)

# Global web search manager instance
web_search_manager = WebSearchManager()
