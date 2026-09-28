# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Maps Geocoding and Places (New) API tools for Smart Pantry Chef."""

import json
import logging
import os
import urllib.parse
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)


def _get_maps_api_key() -> str:
    """Reads GOOGLE_MAPS_API_KEY from environment variables."""
    key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not key or key == "PASTE_KEY_HERE":
        raise ValueError(
            "GOOGLE_MAPS_API_KEY is not set or contains default placeholder in .env file."
        )
    return key


def geocode_address(address: str) -> dict[str, Any]:
    """Converts a street address or city name into geographic coordinates (latitude & longitude).

    Args:
        address: Street address or city name (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'San Francisco, CA').

    Returns:
        Dictionary containing formatted address, latitude, and longitude.
    """
    try:
        api_key = _get_maps_api_key()
        encoded = urllib.parse.quote(address.strip())
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded}&key={api_key}"

        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("status") != "OK" or not data.get("results"):
            return {"error": f"Geocoding failed: {data.get('status', 'ZERO_RESULTS')}"}

        first = data["results"][0]
        location = first["geometry"]["location"]
        return {
            "address": first["formatted_address"],
            "location": {
                "latitude": location["lat"],
                "longitude": location["lng"],
            },
        }
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        return {"error": str(e)}


def search_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "grocery_store",
    radius_meters: float = 2000.0,
) -> list[dict[str, Any]]:
    """Finds nearby places of a given type around a geographic location using Places API (New).

    Args:
        latitude: Center point latitude.
        longitude: Center point longitude.
        place_type: Type of place to search for (e.g. 'grocery_store', 'supermarket', 'restaurant', 'bakery').
        radius_meters: Search radius in meters (default: 2000.0 meters).

    Returns:
        List of nearby places with name, formatted address, and location coordinates.
    """
    try:
        api_key = _get_maps_api_key()
        url = "https://places.googleapis.com/v1/places:searchNearby"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
        }

        payload = {
            "includedTypes": [place_type.lower().strip()],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                    },
                    "radius": float(radius_meters),
                }
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        places_raw = data.get("places", [])
        results = []

        for p in places_raw:
            display_name = p.get("displayName", {}).get("text", "Unknown")
            address = p.get("formattedAddress", "")
            loc = p.get("location", {})
            results.append(
                {
                    "name": display_name,
                    "address": address,
                    "location": {
                        "latitude": loc.get("latitude"),
                        "longitude": loc.get("longitude"),
                    },
                }
            )

        return results
    except Exception as e:
        logger.error(f"Places API (New) searchNearby error: {e}")
        return [{"error": str(e)}]
