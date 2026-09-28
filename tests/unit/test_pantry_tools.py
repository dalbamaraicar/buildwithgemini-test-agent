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

"""Unit tests for Firestore pantry tools."""

from app.firestore_db import add_or_update_pantry_item, get_pantry_inventory


def test_get_pantry_inventory():
    items = get_pantry_inventory()
    assert isinstance(items, list)
    assert len(items) >= 6


def test_get_pantry_inventory_filtered():
    items = get_pantry_inventory(category="produce")
    assert isinstance(items, list)
    assert any(item["name"] == "Roma Tomatoes" for item in items)


def test_add_or_update_pantry_item():
    result = add_or_update_pantry_item(
        item_id="salt",
        name="Sea Salt",
        category="spices",
        quantity=200,
        unit="g",
        notes="Fine grain",
    )
    assert result["status"] == "success"
    assert result["item"]["name"] == "Sea Salt"
