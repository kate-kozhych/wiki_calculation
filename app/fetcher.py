import requests
import re
from typing import Dict, Optional
import logging
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Fetcher:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.timeout = 10
        self.headers = {
            "User-Agent": "PiCalculatorBot/1.0 (Educational project; contact@example.com)"
        }

    def fetch_cosmic_object(self, name: str) -> Optional[Dict[str, float]]: #gets data about our space object
        logger.info(f"Fetching data from the space for {name}")
        content = self._fetch_page_data_wiki(name)
        if not content:
            logger.error(f"Failed to fetch page content for {name}")
            return None
        data = self._parse_space_data(content, name)
        if not data:
            logger.error(f"Failed to parse data for {name}")
            return None
        logger.info(f"Successfully fetched data for {name}")
        return data

    def _fetch_page_data_wiki(self, title: str) -> Optional[str]: #makes http request to wiki api and gets wikitext
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main",
            "titles": title,
            "format": "json",
            "formatversion": "2"
        }
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status() #status code 200
            data = response.json()
            pages = data.get("query", {}).get("pages", [])
            if not pages:
                logger.warning(f"No pages found for title {title}")
                return None
            page = pages[0]
            if "missing" in page:
                logger.warning(f"Page not found {title}")
                return None
            
            revisions = page.get("revisions", [])
            if not revisions:
                return None
            content = page["revisions"][0].get("slots", {}).get("main", {}).get("content", "")
            return content
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching {title}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {title}: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing response for {title}: {e}")
            return None

    def _parse_space_data(self, content: str, name: str)  -> Optional[Dict[str, float]]: #parse wikitext to get the readius and other data for calculations
        radius = self._get_radius(content)
        circumference = self._get_circumference(content)
        if radius is None:
            logger.warning(f"No radius found for {name}")
            return None
        if circumference is None:
            logger.info(f"ℹCircumference not found for {name}")
            return None

        return {
            "name": name,
            "radius_km": radius,
            "circumference_km": circumference
            # "source": "wikipedia"
        }

    def _get_radius(self, content: str) -> Optional[float]:
        patterns = [
            r'\|\s*[a-z_]*radius\s*=\s*(?:\n\s*)?{{val\s*\|\s*([0-9.,]+)',
            r'\|\s*[a-z_]*radius\s*=\s*(?:\n\s*)?{{convert\s*\|\s*([0-9.,]+)',
            r'\|\s*[a-z_]*radius\s*=\s*(?:\n\s*)?([0-9.,]+)\s*(?:&nbsp;)?\s*km'
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        return None


    def _get_circumference(self, content: str) -> Optional[float]:
        patterns = [
            r'\|\s*[a-z_]*circumference\s*=\s*(?:\n\s*)?{{val\s*\|\s*([0-9.,]+)',
            r'\|\s*[a-z_]*circumference\s*=\s*(?:\n\s*)?{{convert\s*\|\s*([0-9.,]+)',
            r'\|\s*[a-z_]*circumference\s*=\s*(?:\n\s*)?([0-9.,]+)\s*(?:&nbsp;)?\s*km',
            r'\|\s*circumference\s*=\s*{{unbulleted list[^}]*\n\s*\|\s*{{val\s*\|\s*([0-9.,]+)',
        ]  
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        return None




