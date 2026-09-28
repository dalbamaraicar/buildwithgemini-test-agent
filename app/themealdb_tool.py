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

"""TheMealDB public API integration for Smart Pantry Chef."""

import json
import logging
import os
import urllib.parse
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

# Free default test API key provided by TheMealDB
DEFAULT_API_KEY = "1"


def search_online_recipes(query: str) -> list[dict[str, Any]]:
    """Searches real online recipes from TheMealDB public API by meal or ingredient name.

    Args:
        query: Recipe name or main ingredient to search for (e.g., 'pasta', 'chicken', 'curry', 'salmon').

    Returns:
        List of dictionaries with meal name, category, cuisine, ingredients, instructions, and image URL.
    """
    api_key = os.getenv("THEMEALDB_API_KEY", DEFAULT_API_KEY)
    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={encoded_query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SmartPantryChef/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        meals = data.get("meals")
        if not meals:
            return []

        results = []
        for meal in meals[:5]:  # Limit to top 5 results
            ingredients = []
            for i in range(1, 21):
                ing = meal.get(f"strIngredient{i}")
                measure = meal.get(f"strMeasure{i}")
                if ing and ing.strip():
                    ingredients.append(f"{measure.strip()} {ing.strip()}".strip())

            results.append(
                {
                    "id": meal.get("idMeal"),
                    "name": meal.get("strMeal"),
                    "category": meal.get("strCategory"),
                    "cuisine": meal.get("strArea"),
                    "image_url": meal.get("strMealThumb"),
                    "ingredients": ingredients,
                    "instructions": meal.get("strInstructions", "")[:300] + "...",
                    "youtube_url": meal.get("strYoutube"),
                }
            )
        return results
    except Exception as e:
        logger.error(f"Error fetching recipes from TheMealDB: {e}")
        return [{"error": str(e)}]
