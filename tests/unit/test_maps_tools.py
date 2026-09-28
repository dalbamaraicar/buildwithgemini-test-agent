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

"""Unit tests for Google Maps tools."""

import os
from unittest.mock import MagicMock, patch
from app.maps_tools import geocode_address, search_nearby_places


@patch("urllib.request.urlopen")
def test_geocode_address(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"status": "OK", "results": [{"formatted_address": "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA", "geometry": {"location": {"lat": 37.422, "lng": -122.084}}}]}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_key"}):
        res = geocode_address("1600 Amphitheatre Pkwy")
        assert "address" in res
        assert res["location"]["latitude"] == 37.422
        assert res["location"]["longitude"] == -122.084


@patch("urllib.request.urlopen")
def test_search_nearby_places(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"places": [{"displayName": {"text": "Trader Joe\'s"}, "formattedAddress": "Mountain View, CA", "location": {"latitude": 37.42, "longitude": -122.08}}]}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_key"}):
        res = search_nearby_places(37.422, -122.084, place_type="grocery_store")
        assert isinstance(res, list)
        assert len(res) == 1
        assert res[0]["name"] == "Trader Joe's"
        assert res[0]["location"]["latitude"] == 37.42
