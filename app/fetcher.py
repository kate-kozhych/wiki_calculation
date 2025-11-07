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

    def fetch_cosmic_objest(self, name: str) -> Optional[Dict[str, float]]: #gets data about our space object
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
            logger.info(f"ℹCircumference not found for {name}, calculating from radius")
            # C = 2πR
            circumference = 2 * math.pi * radius

        return {
            "name": name,
            "radius_km": radius,
            "circumference_km": circumference
        }

    def _get_radius(self, content:str) -> Optional[float]:
        # | equatorial_radius = {{val|6378.137|u=km}}
        pattern1 = r'\|\s*equatorial_radius\s*=\s*{{val\|([0-9.,]+)'
        match = re.search(pattern1, content, re.IGNORECASE)
        
        if match:
            value = match.group(1).replace(',', '')
            return float(value)

        # | mean_radius = {{val|1737.4|u=km}} for the moon
        pattern2 = r'\|\s*mean_radius\s*=\s*{{val\|([0-9.,]+)'
        match = re.search(pattern2, content, re.IGNORECASE)
        
        if match:
            value = match.group(1).replace(',', '')
            return float(value)

        # | equatorial_radius = 6378.137 km if it is in the simple format
        pattern3 = r'\|\s*(?:equatorial_)?radius\s*=\s*([0-9.,]+)\s*km'
        match = re.search(pattern3, content, re.IGNORECASE)
        
        if match:
            value = match.group(1).replace(',', '')
            return float(value)
        
        return None

    def _get_circumference(self, content:str) -> Optional[float]:
        # | circumference = {{val|40075.017|u=km}}
        pattern1 = r'\|\s*circumference\s*=\s*{{val\|([0-9.,]+)'
        match = re.search(pattern1, content, re.IGNORECASE)
        
        if match:
            value = match.group(1).replace(',', '')
            return float(value)
        
        # name | equatorial_circumference same pattern
        pattern2 = r'\|\s*(?:equatorial_)?circumference\s*=\s*{{val\|([0-9.,]+)'
        match = re.search(pattern2, content, re.IGNORECASE)
        
        if match:
            value = match.group(1).replace(',', '')
            return float(value)
        
        # | circumference = 40075.017 km (equatorial) simple format
        pattern3 = r'\|\s*circumference\s*=\s*([0-9.,]+)\s*km'
        match = re.search(pattern3, content, re.IGNORECASE)
        
        if match:
            value = match.group(1).replace(',', '')
            return float(value)
        
        return None

if __name__ == "__main__":
    fetcher = Fetcher()
    earth_data=fetcher.fetch_cosmic_objest("Earth")
    print(f"Earth data: {earth_data}")
    if earth_data:
        pi = earth_data["circumference_km"] / (2 * earth_data["radius_km"])
        print(f"Calculated π from Earth: {pi:.10f}")
        print(f"Difference from math.pi: {abs(pi - 3.141592653589793):.10f}")


