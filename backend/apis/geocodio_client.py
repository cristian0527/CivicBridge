"""
Geocodio API integration for CivicBridge.

This module handles ZIP code to congressional district mapping
and provides representative lookup functionality.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from geocodio import GeocodioClient

load_dotenv()

class GeocodioError(Exception):
    """Custom exception for Geocodio API errors."""

class CivicBridgeGeocodioClient:
    """Client for interacting with the Geocodio API using pygeocodio library."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Geocodio client with an API key."""
        self.api_key = os.getenv('GEOCODIO_API_KEY')
        if not self.api_key:
            raise GeocodioError("GEOCODIO_API_KEY is required. Setup your .env file with GEOCODIO_API_KEY.")
        
        try:
            self.client = GeocodioClient(self.api_key)
        except ValueError as e:
            raise GeocodioError(f"Invalid API key: {e}")
        except Exception as e:
            raise GeocodioError(f"Failed to initialize Geocodio client: {e}")
        
        self.logger = logging.getLogger(__name__)
    
    def lookup_zip_code(self, zip_code: str) -> Dict[str, Any]:
        """Lookup congressional district and representatives by ZIP code."""
        """Returns: Dict containing district and location information"""
        
        if not zip_code or not zip_code.isdigit() or len(zip_code) != 5:
            raise GeocodioError("Invalid ZIP code format. Must be a 5-digit number.")
        
        try:
            # Request congressional district information
            result = self.client.geocode(zip_code, fields=['cd'])
            if not result or not result.get('results'):
                raise GeocodioError(f"No results found for ZIP code {zip_code}.")
            
            # Check if the congressional district information exists
            location_data = None
            for item in result.get('results', []):
                if item.get('fields', {}).get('congressional_districts'):
                    location_data = item
                    break

            if not location_data:
                raise GeocodioError(f"No congressional district information found for ZIP code {zip_code}.")
            
            location = location_data.get("location", {})
            fields = location_data.get("fields", {})
            cd_info = fields.get("congressional_districts", {})[0] # Primary district

            district_info = {
                'zip_code': zip_code,
                'city': location.get('city'),
                'state': location.get('state'),
                'county': location.get('county'),
                'congressional_district': {
                    'number': cd_info.get('district_number'),
                    'name': cd_info.get('name'),
                    'current_legislators': cd_info.get('current_legislators', [])
                }
            }

            #self.logger.info(f"Successfully looked up ZIP code {zip_code}: {district_info}")
            self.logger.info(f"Successfully looked up ZIP code {zip_code}")
            return district_info
        
        except ValueError as e:
            error_msg = f"Invalid response from Geocodio API: {e}"
            self.logger.error(error_msg)
            raise GeocodioError(error_msg) from e
        except Exception as e:
            if isinstance(e, GeocodioError):
                raise
            error_msg = f"Geocodio API error for ZIP code {zip_code}: {e}"
            self.logger.error(error_msg)
            raise GeocodioError(error_msg) from e
    
    def get_representatives(self, zip_code: str) -> List[Dict[str, Any]]:
        """Get representatives for a given ZIP code."""
        """Returns: List of representatives with their details"""

        try:
            district_info = self.lookup_zip_code(zip_code)
            representatives = []
            cd_legislators = district_info['congressional_district'].get('current_legislators', [])
            print(f"DEBUG: Processing {len(cd_legislators)} legislators")
            for legislator in cd_legislators:
                # Extract name from nested bio object
                bio = legislator.get('bio', {})
                name = f"{bio.get('first_name', '')} {bio.get('last_name', '')}".strip()
                party = bio.get('party', '')
    
                # Extract contact info
                contact = legislator.get('contact', {})
                references = legislator.get('references', {})
                title =  legislator.get('type', '').lower()
                # Determine if the legislator is a representative or senator
                if 'senator' in title:
                    role = 'Senator'
                    district_num = None  # Senators do not have a district number
                elif 'representative' in title:
                    role = 'Representative'
                    district_num = district_info['congressional_district']['number']
                else:
                    role = 'Legislator'
                    district_num = district_info['congressional_district']['number']

                rep_info = {
                    'name': name,
                    'party': party,
                    'title': legislator.get('type'),
                    'chamber': role,
                    'district': district_num,
                    'state': district_info['state'],
                    'bioguide_id': references.get('bioguide_id'),
                    'phone': contact.get('phone'),
                    'address': contact.get('address'),
                    'website': contact.get('url'),
                    'contact_form': contact.get('contact_form'),
                    'twitter': legislator.get('social', {}).get('twitter'),
                    'photo_url': bio.get('photo_url')
                }

                #representatives.append(rep_info)    
                    #'name': legislator.get('name'),
                    #'party': legislator.get('party'),
                    #'title': legislator.get('type'),
                    #'chamber': role,
                    #'district': district_num,
                    #'state': district_info['state'],
                    #'contact': legislator.get('bio_guide_id')
                #}

                representatives.append(rep_info)

            self.logger.info(f"Found {len(representatives)} representatives for ZIP code {zip_code}")
            return representatives
            
        except GeocodioError:
            raise
        except Exception as e:
            error_msg = f"Error getting representatives for ZIP code {zip_code}: {e}"
            self.logger.error(error_msg)
            raise GeocodioError(error_msg) from e

def create_geocodio_client(api_key: Optional[str] = None) -> CivicBridgeGeocodioClient:
    """Factory method to create a Geocodio client instance."""
    return CivicBridgeGeocodioClient(api_key)

if __name__ == "__main__":
    import json
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        client = create_geocodio_client()
        
        print("Testing Geocodio API Client...")
        print("=" * 50)
        
        # Test ZIP code lookup
        test_zip = "12601"
        print(f"\nTesting ZIP code lookup for {test_zip}...")
        
        district_info = client.lookup_zip_code(test_zip)
        print("District Information:")
        print(json.dumps(district_info, indent=2))
        
        # Test representative lookup
        print(f"\nTesting representative lookup for {test_zip}...")
        representatives = client.get_representatives(test_zip)  # Fixed method name
        
        if representatives:
            print(f"Found {len(representatives)} representatives:")
            for rep in representatives:
                print(f"- {rep['name']} ({rep['party']}) - {rep['title']} ({rep['chamber']})")
                print(f"  Phone: {rep['phone']}")
                print(f"  Bioguide ID: {rep['bioguide_id']}")
                if rep['twitter']:
                    print(f"  Twitter: @{rep['twitter']}")
        else:
            print("No representatives found")
            
    except GeocodioError as e:
        print(f"Geocodio API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

