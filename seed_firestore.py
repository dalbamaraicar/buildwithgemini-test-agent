#!/usr/bin/env python3
"""Seed script to populate Firestore with initial pantry items."""

import logging
from google.api_core import exceptions
from google.cloud import firestore

# IMPORTANT: Hardcoded Project ID string as required by Agent Platform
PROJECT_ID = "qwiklabs-gcp-02-76b9ced258ff"
COLLECTION_NAME = "pantry"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INITIAL_PANTRY_ITEMS = [
    {
        "id": "olive_oil",
        "name": "Extra Virgin Olive Oil",
        "category": "pantry_staple",
        "quantity": 500,
        "unit": "ml",
        "notes": "Cold pressed, organic",
    },
    {
        "id": "tomatoes",
        "name": "Roma Tomatoes",
        "category": "produce",
        "quantity": 6,
        "unit": "pcs",
        "notes": "Fresh, ripe",
    },
    {
        "id": "garlic",
        "name": "Fresh Garlic Cloves",
        "category": "produce",
        "quantity": 8,
        "unit": "cloves",
        "notes": "Peeled",
    },
    {
        "id": "pasta_spaghetti",
        "name": "Spaghetti Pasta",
        "category": "grains",
        "quantity": 400,
        "unit": "g",
        "notes": "Semolina wheat",
    },
    {
        "id": "parmesan_cheese",
        "name": "Aged Parmesan Cheese",
        "category": "dairy",
        "quantity": 150,
        "unit": "g",
        "notes": "Grated",
    },
    {
        "id": "basil",
        "name": "Fresh Basil Leaves",
        "category": "produce",
        "quantity": 1,
        "unit": "bunch",
        "notes": "Hydroponic fresh",
    },
]


def seed_database():
    """Seeds initial items into the Firestore collection."""
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    logger.info(f"Seeding '{COLLECTION_NAME}' collection in Firestore project: '{PROJECT_ID}'...")

    try:
        for item in INITIAL_PANTRY_ITEMS:
            item_id = item["id"]
            data = {k: v for k, v in item.items() if k != "id"}
            collection_ref.document(item_id).set(data, merge=True)
            logger.info(f"  ✓ Seeded Firestore item: {item_id} ({item['name']})")
        logger.info("Successfully seeded Firestore database! 🎉")
    except exceptions.NotFound:
        logger.warning(
            "Firestore database (default) does not exist yet for this project.\n"
            f"Please visit https://console.cloud.google.com/datastore/setup?project={PROJECT_ID} "
            "to create a Cloud Firestore database in Native mode."
        )


if __name__ == "__main__":
    seed_database()
