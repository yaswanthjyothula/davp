"""
Jolpica / Ergast F1 API client with local JSON caching and fallback.
Base URL: https://api.jolpi.ca/ergast/f1/
"""

import os
import json
import time
import hashlib
import urllib.request
import urllib.error
from utils.helpers import remove_hyphens, format_f1_date

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_TTL = 86400  # 24 hours cache

class JolpicaApiClient:
    def __init__(self, base_url="https://api.jolpi.ca/ergast/f1"):
        self.base_url = base_url.rstrip('/')

    def _get_cache_path(self, endpoint):
        key = hashlib.md5(endpoint.encode('utf-8')).hexdigest()
        return os.path.join(CACHE_DIR, f"{key}.json")

    def fetch(self, endpoint, force_refresh=False):
        """Fetch JSON data with local file caching and error recovery."""
        cache_file = self._get_cache_path(endpoint)
        
        # Check cache if not forcing refresh
        if not force_refresh and os.path.exists(cache_file):
            mtime = os.path.getmtime(cache_file)
            if time.time() - mtime < CACHE_TTL:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    pass

        # Make HTTP Request
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if not url.endswith('.json'):
            url += '.json'
            
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'F1HistoricalAnalytics/1.0'})
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode('utf-8'))
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
                return data
        except Exception as e:
            # If request fails, fall back to existing cache even if expired
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    pass
            return None

    def get_current_driver_standings(self):
        """Retrieve current season driver championship standings."""
        data = self.fetch('current/driverStandings')
        if not data:
            return []
        try:
            lists = data['MRData']['StandingsTable']['StandingsLists']
            if not lists:
                return []
            standings = lists[0]['DriverStandings']
            results = []
            for s in standings:
                d = s['Driver']
                c = s['Constructors'][0] if s.get('Constructors') else {'name': 'N/A'}
                results.append({
                    'position': int(s['position']),
                    'driver': remove_hyphens(f"{d.get('givenName', '')} {d.get('familyName', '')}"),
                    'driverId': d.get('driverId', ''),
                    'code': d.get('code', 'N/A'),
                    'nationality': remove_hyphens(d.get('nationality', 'N/A')),
                    'constructor': remove_hyphens(c.get('name', 'N/A')),
                    'points': float(s.get('points', 0)),
                    'wins': int(s.get('wins', 0)),
                })
            return results
        except Exception:
            return []

    def get_current_constructor_standings(self):
        """Retrieve current season constructor championship standings."""
        data = self.fetch('current/constructorStandings')
        if not data:
            return []
        try:
            lists = data['MRData']['StandingsTable']['StandingsLists']
            if not lists:
                return []
            standings = lists[0]['ConstructorStandings']
            results = []
            for s in standings:
                c = s['Constructor']
                results.append({
                    'position': int(s['position']),
                    'constructor': remove_hyphens(c.get('name', 'N/A')),
                    'constructorId': c.get('constructorId', ''),
                    'nationality': remove_hyphens(c.get('nationality', 'N/A')),
                    'points': float(s.get('points', 0)),
                    'wins': int(s.get('wins', 0)),
                })
            return results
        except Exception:
            return []
