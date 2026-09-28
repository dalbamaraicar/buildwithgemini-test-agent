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

"""Firestore database tools for Smart Pantry Chef."""

import logging
from typing import Any
from google.api_core import exceptions
from google.cloud import firestore

# IMPORTANT: Hardcoded Project ID string as required by Agent Platform
PROJECT_ID = "qwiklabs-gcp-02-76b9ced258ff"
COLLECTION_NAME = "pantry"

logger = logging.getLogger(__name__)

# Fallback in-memory storage for local dev when Firestore database is pending creation
_IN_MEMORY_PANTRY: dict[str, dict[str, Any]] = {
    "olive_oil": {
        "id": "olive_oil",
        "name": "Extra Virgin Olive Oil",
        "category": "pantry_staple",
        "quantity": 500.0,
        "unit": "ml",
        "notes": "Cold pressed, organic",
    },
    "tomatoes": {
        "id": "tomatoes",
        "name": "Roma Tomatoes",
        "category": "produce",
        "quantity": 6.0,
        "unit": "pcs",
        "notes": "Fresh, ripe",
    },
    "garlic": {
        "id": "garlic",
        "name": "Fresh Garlic Cloves",
        "category": "produce",
        "quantity": 8.0,
        "unit": "cloves",
        "notes": "Peeled",
    },
    "pasta_spaghetti": {
        "id": "pasta_spaghetti",
        "name": "Spaghetti Pasta",
        "category": "grains",
        "quantity": 400.0,
        "unit": "g",
        "notes": "Semolina wheat",
    },
    "parmesan_cheese": {
        "id": "parmesan_cheese",
        "name": "Aged Parmesan Cheese",
        "category": "dairy",
        "quantity": 150.0,
        "unit": "g",
        "notes": "Grated",
    },
    "basil": {
        "id": "basil",
        "name": "Fresh Basil Leaves",
        "category": "produce",
        "quantity": 1.0,
        "unit": "bunch",
        "notes": "Hydroponic fresh",
    },
}


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with hardcoded project ID string."""
    return firestore.Client(project=PROJECT_ID)


def get_pantry_inventory(category: str | None = None) -> list[dict[str, Any]]:
    """Retrieves all pantry items from Firestore, optionally filtered by category.

    Args:
        category: Optional category filter (e.g. 'produce', 'dairy', 'grains', 'spices', 'pantry_staple').

    Returns:
        A list of dictionaries representing pantry items.
    """
    try:
        db = get_firestore_client()
        query = db.collection(COLLECTION_NAME)
        if category:
            query = query.where("category", "==", category.lower().strip())
        docs = query.stream()
        items = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            items.append(data)
        return items
    except exceptions.NotFound:
        logger.warning(
            "Firestore database not found. Using local in-memory pantry store. "
            f"To enable Cloud Firestore, visit: https://console.cloud.google.com/datastore/setup?project={PROJECT_ID}"
        )
        items = list(_IN_MEMORY_PANTRY.values())
        if category:
            cat_clean = category.lower().strip()
            items = [item for item in items if item.get("category") == cat_clean]
        return items
    except Exception as e:
        logger.error(f"Error fetching pantry inventory: {e}")
        return [{"error": str(e)}]


def add_or_update_pantry_item(
    item_id: str,
    name: str,
    category: str,
    quantity: float,
    unit: str,
    notes: str = "",
) -> dict[str, Any]:
    """Adds or updates an item in the pantry Firestore collection.

    Args:
        item_id: Unique document ID or code (e.g. 'olive_oil', 'tomatoes').
        name: Name of the ingredient/item.
        category: Category (e.g. 'produce', 'dairy', 'pantry_staple', 'spice').
        quantity: Current quantity available.
        unit: Unit of measurement (e.g. 'g', 'ml', 'pcs', 'cups', 'bottles').
        notes: Additional notes or expiration hints.

    Returns:
        Status and saved item data.
    """
    clean_id = item_id.lower().strip().replace(" ", "_")
    data = {
        "id": clean_id,
        "name": name,
        "category": category.lower().strip(),
        "quantity": float(quantity),
        "unit": unit,
        "notes": notes,
    }
    try:
        db = get_firestore_client()
        doc_ref = db.collection(COLLECTION_NAME).document(clean_id)
        doc_ref.set(
            {
                "name": data["name"],
                "category": data["category"],
                "quantity": data["quantity"],
                "unit": data["unit"],
                "notes": data["notes"],
            },
            merge=True,
        )
        _IN_MEMORY_PANTRY[clean_id] = data
        return {"status": "success", "storage": "firestore", "item": data}
    except exceptions.NotFound:
        logger.warning("Firestore database not found. Updating local in-memory pantry store.")
        _IN_MEMORY_PANTRY[clean_id] = data
        return {"status": "success", "storage": "in_memory_fallback", "item": data}
    except Exception as e:
        logger.error(f"Error saving pantry item {item_id}: {e}")
        return {"status": "error", "message": str(e)}
