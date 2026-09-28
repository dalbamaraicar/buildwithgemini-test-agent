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

"""Unit tests for recipe search tools."""

from app.recipe_tools import search_recipes_by_ingredients


def test_search_recipes_by_ingredients():
    results = search_recipes_by_ingredients(["garlic", "olive_oil", "spaghetti"])
    assert isinstance(results, list)
    assert len(results) > 0
    top_match = results[0]
    assert top_match["title"] == "Spaghetti Aglio e Olio"
    assert top_match["missing_ingredients"] == []


def test_search_recipes_with_missing_items():
    results = search_recipes_by_ingredients(["tomatoes", "garlic"])
    assert isinstance(results, list)
    assert any("basil" in r["missing_ingredients"] for r in results)
