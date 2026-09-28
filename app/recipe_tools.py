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

"""Recipe search tools for Smart Pantry Chef."""

from typing import Any

RECIPE_DATABASE = [
    {
        "id": "pasta_aglio_olio",
        "title": "Spaghetti Aglio e Olio",
        "prep_time": "15 mins",
        "required_ingredients": ["spaghetti", "olive_oil", "garlic"],
        "optional_ingredients": ["parmesan_cheese", "fresh_basil"],
        "instructions": "Boil pasta. Sauté minced garlic in olive oil until golden. Toss pasta with garlic oil and top with parmesan.",
    },
    {
        "id": "fresh_tomato_pasta",
        "title": "Fresh Tomato & Basil Pasta",
        "prep_time": "20 mins",
        "required_ingredients": ["spaghetti", "tomatoes", "garlic", "olive_oil", "basil"],
        "optional_ingredients": ["parmesan_cheese"],
        "instructions": "Dice tomatoes and garlic. Sauté in olive oil until tomatoes break down. Toss with pasta and fresh basil leaves.",
    },
    {
        "id": "garlic_parmesan_bread",
        "title": "Garlic Parmesan Toast",
        "prep_time": "10 mins",
        "required_ingredients": ["garlic", "parmesan_cheese", "olive_oil"],
        "optional_ingredients": ["bread", "basil"],
        "instructions": "Mix minced garlic and parmesan into olive oil. Spread over sliced bread and toast until crispy.",
    },
    {
        "id": "caprese_salad",
        "title": "Fresh Caprese Salad",
        "prep_time": "10 mins",
        "required_ingredients": ["tomatoes", "basil", "olive_oil"],
        "optional_ingredients": ["mozzarella"],
        "instructions": "Slice fresh tomatoes. Arrange with basil leaves, drizzle generously with extra virgin olive oil.",
    },
]


def search_recipes_by_ingredients(
    ingredients: list[str], max_results: int = 3
) -> list[dict[str, Any]]:
    """Searches for recipes matching available pantry ingredients.

    Args:
        ingredients: List of ingredient names available in the pantry (e.g. ['tomatoes', 'garlic', 'pasta']).
        max_results: Maximum number of recipe recommendations to return.

    Returns:
        A list of matching recipes with title, prep time, required ingredients, missing items, and instructions.
    """
    clean_inputs = [i.lower().strip().replace(" ", "_") for i in ingredients]
    matches = []

    for recipe in RECIPE_DATABASE:
        required = recipe["required_ingredients"]
        matching_count = sum(
            1 for req in required if any(inp in req or req in inp for inp in clean_inputs)
        )
        missing = [
            req for req in required if not any(inp in req or req in inp for inp in clean_inputs)
        ]

        if matching_count > 0:
            matches.append(
                {
                    "title": recipe["title"],
                    "prep_time": recipe["prep_time"],
                    "matching_ingredients_count": matching_count,
                    "missing_ingredients": missing,
                    "instructions": recipe["instructions"],
                }
            )

    matches.sort(key=lambda x: (x["matching_ingredients_count"], -len(x["missing_ingredients"])), reverse=True)
    return matches[:max_results]
