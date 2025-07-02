from tavily import TavilyClient
import os
from dotenv import load_dotenv
from typing import Annotated
import re
import json

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


class direct_web_search():
    def __init__(self,player_name):
        self.player_name = player_name

    def search_stats_tool(self) -> Annotated[str, "A list of results from the search"]:
        query = f"{self.player_name} cricket career statistics Test ODI T20I matches runs average centuries in a json format"
        return tavily.get_search_context(query=query, search_depth="advanced", max_results=1)
        # content = tavily.get_search_context(query=query, search_depth="advanced", max_results=3)
        # return self._extract_key_stats(content)


    def search_stats_compact(self) -> Annotated[dict, "Compact cricket statistics results"]:
        """Optimized search for smaller context windows (like DeepSeek 6.7B)"""
        # Use the same successful approach as search_stats_tool
        full_results = self.search_stats_tool()
        
        # Automatically compact the results
        return self.compact_search_results(full_results)
    
    def _extract_key_stats(self, content: str) -> str:
        """Extract only cricket statistics from content"""
        # Look for key statistical patterns
        key_phrases = [
            'Test:', 'ODI:', 'T20I:', 'matches', 'runs', 'average', 'centuries',
            'Career statistics', 'batting average', 'runs scored'
        ]
        
        sentences = content.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            if any(phrase.lower() in sentence.lower() for phrase in key_phrases):
                # Clean up the sentence
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 10 and len(clean_sentence) < 200:
                    relevant_sentences.append(clean_sentence)
        
        # Join key sentences, limit to prevent context overflow
        result = '. '.join(relevant_sentences[:5])  # Max 5 sentences
        return result[:500] if len(result) > 500 else result  # Max 500 chars
    
    def compact_search_results(self, full_results) -> dict:
        """Convert full search results to compact format for smaller models like DeepSeek 6.7B"""
        
        # If it's already a simple dict, return it
        if isinstance(full_results, dict) and 'results' in full_results:
            return full_results
            
        # Handle string results from get_search_context
        if isinstance(full_results, str):
            # First try to parse as JSON string
            try:
                parsed_results = json.loads(full_results)
                if isinstance(parsed_results, list) and len(parsed_results) > 0:
                    # Extract from first result (usually the best one)
                    best_result = parsed_results[0]
                    content = best_result.get('content', '')
                    url = best_result.get('url', 'https://search_context')
                    
                    # Format the cricket statistics
                    formatted_stats = self._format_cricket_stats(content)
                    
                    return {
                        "message": f"Cricket stats for {self.player_name}",
                        "player_name": self.player_name,
                        "results": [
                            {
                                "url": url,
                                "content": formatted_stats
                            }
                        ]
                    }
            except (json.JSONDecodeError, KeyError, IndexError):
                # If JSON parsing fails, fall back to text extraction
                pass
            
            # Fallback: Try to extract cricket statistics from raw text
            stats_content = self._extract_key_stats(full_results)
            return {
                "message": f"Cricket stats for {self.player_name}",
                "player_name": self.player_name,
                "results": [
                    {
                        "url": "https://search_context",
                        "content": stats_content
                    }
                ]
            }
        
        # Handle complex nested results
        try:
            # Look for the most relevant cricket statistics
            best_content = ""
            best_url = ""
            
            # Try to find Wikipedia or other reliable sources
            if hasattr(full_results, 'get') and 'results' in full_results:
                for result in full_results['results']:
                    content = result.get('content', '')
                    url = result.get('url', '')
                    
                    # Prefer Wikipedia or comprehensive sources
                    if 'wikipedia' in url.lower() or 'Career statistics' in content:
                        best_content = content
                        best_url = url
                        break
                    elif not best_content:  # Use first result as fallback
                        best_content = content
                        best_url = url
            
            # Extract and format the statistics
            if best_content:
                formatted_stats = self._format_cricket_stats(best_content)
                return {
                    "message": f"Cricket stats for {self.player_name}",
                    "player_name": self.player_name,
                    "results": [
                        {
                            "url": best_url,
                            "content": formatted_stats
                        }
                    ]
                }
        except Exception as e:
            print(f"Error processing results: {e}")
        
        # Fallback: return minimal structure
        return {
            "message": f"Cricket stats for {self.player_name}",
            "player_name": self.player_name,
            "results": [
                {
                    "url": "https://fallback",
                    "content": f"Cricket statistics for {self.player_name} - data parsing in progress"
                }
            ]
        }
    
    def _format_cricket_stats(self, content: str) -> str:
        """Format cricket statistics using robust table parsing - handles malformed tables"""
        # Remove commas from numbers for easier parsing
        clean_content = content.replace(',', '')
        
        # Split into lines and identify table structure
        lines = clean_content.split('\n')
        stats_dict = {'Test': {}, 'ODI': {}, 'T20I': {}}
        
        # Find data rows for each format
        for line in lines:
            line = line.strip()
            if '|' in line and any(fmt in line for fmt in ['Test', 'ODI', 'T20I']):
                parts = [p.strip() for p in line.split('|')]
                
                # Identify format
                format_name = None
                for fmt in ['Test', 'ODI', 'T20I']:
                    if fmt in parts[0]:
                        format_name = fmt
                        break
                
                if not format_name or len(parts) < 4:
                    continue
                
                try:
                    # Parse based on available columns
                    format_stats = {}
                    
                    # Matches (usually column 1)
                    if len(parts) > 1 and parts[1].isdigit():
                        format_stats['matches'] = parts[1]
                    
                    # Runs (usually column 3 or 4)
                    for i in [3, 4]:
                        if len(parts) > i and parts[i].replace('.', '').isdigit():
                            runs_val = int(float(parts[i]))
                            if 100 <= runs_val <= 25000:  # Reasonable range
                                format_stats['runs'] = str(runs_val)
                                break
                    
                    # Average - look in multiple positions
                    avg_found = False
                    for i in [5, 6, 7]:
                        if len(parts) > i and not avg_found:
                            avg_str = parts[i].replace(' ', '')
                            if re.match(r'^\d+\.\d+$', avg_str):
                                avg_val = float(avg_str)
                                if 10.0 <= avg_val <= 70.0:  # Reasonable batting average
                                    format_stats['avg'] = avg_str
                                    avg_found = True
                    
                    # Centuries - look for patterns like "33/6" or "73/10"
                    for i in range(len(parts)):
                        if '/' in parts[i]:
                            cent_parts = parts[i].split('/')
                            if len(cent_parts) >= 2 and cent_parts[1].isdigit():
                                cent_val = int(cent_parts[1])
                                if 0 <= cent_val <= 80:  # Reasonable centuries count
                                    format_stats['centuries'] = cent_parts[1]
                                    break
                    
                    # Store if we have meaningful data
                    if len(format_stats) >= 2:
                        stats_dict[format_name] = format_stats
                        
                except (ValueError, IndexError):
                    continue
        
        # Build formatted output
        if any(stats_dict.values()):
            result_parts = []
            for fmt in ['Test', 'ODI', 'T20I']:
                if stats_dict[fmt]:
                    stats = stats_dict[fmt]
                    matches = stats.get('matches', '0')
                    runs = stats.get('runs', '0')
                    avg = stats.get('avg', '0.0')
                    centuries = stats.get('centuries', '0')
                    
                    result_parts.append(f"{fmt}: {matches} matches, {runs} runs, avg {avg}, {centuries} centuries")
            
            if result_parts:
                return f"Career statistics: {'. '.join(result_parts)}."
        
        # Ultimate fallback: try basic regex patterns
        test_match = re.search(r'Test.*?(\d+).*?(\d{3,5}).*?([\d\.]+).*?(\d+)', clean_content)
        odi_match = re.search(r'ODI.*?(\d+).*?(\d{3,5}).*?([\d\.]+).*?(\d+)', clean_content)
        t20_match = re.search(r'T20I.*?(\d+).*?(\d{3,5}).*?([\d\.]+).*?(\d+)', clean_content)
        
        if test_match or odi_match or t20_match:
            result_parts = []
            if test_match:
                result_parts.append(f"Test: {test_match.group(1)} matches, {test_match.group(2)} runs, avg {test_match.group(3)}, {test_match.group(4)} centuries")
            if odi_match:
                result_parts.append(f"ODI: {odi_match.group(1)} matches, {odi_match.group(2)} runs, avg {odi_match.group(3)}, {odi_match.group(4)} centuries")
            if t20_match:
                result_parts.append(f"T20I: {t20_match.group(1)} matches, {t20_match.group(2)} runs, avg {t20_match.group(3)}, {t20_match.group(4)} centuries")
            
            return f"Career statistics: {'. '.join(result_parts)}."
        
        # If no patterns match, return empty string
        return ""



