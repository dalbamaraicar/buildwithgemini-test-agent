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

"""Unit tests for TheMealDB API tool."""

from app.themealdb_tool import search_online_recipes


def test_search_online_recipes():
    results = search_online_recipes("pasta")
    assert isinstance(results, list)
    assert len(results) > 0
    top_meal = results[0]
    assert "name" in top_meal
    assert "ingredients" in top_meal
    assert "image_url" in top_meal
    assert top_meal["image_url"].startswith("http")
