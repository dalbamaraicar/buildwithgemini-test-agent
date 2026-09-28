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

"""Image generation tool using gemini-3.1-flash-lite-image for Smart Pantry Chef."""

import io
import logging
import uuid
from typing import Any

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

logger = logging.getLogger(__name__)

HARDCODED_BUCKET_NAME = "smart-pantry-chef-media-qwiklabs-gcp-02-76b9ced258ff"


async def generate_recipe_image(
    item_name: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Generates an image for a recipe or food dish, saves it as an artifact, and uploads it to public Cloud Storage.

    Args:
        item_name: Name or description of the food dish or recipe to generate an image for (e.g., 'Fresh Tomato & Basil Pasta').
        tool_context: ADK execution context for saving session artifacts.

    Returns:
        Dictionary containing the public Cloud Storage image URL, item name, and artifact filename.
    """
    try:
        # Initialize Gemini Client for global region as required for gemini-3.1-flash-lite-image
        client = genai.Client(location="global")
        prompt = f"Professional studio food photography of {item_name}, highly detailed, vibrant, delicious presentation."

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        image_bytes = None
        for part in response.parts:
            if part.inline_data and part.inline_data.data:
                image_bytes = part.inline_data.data
                break
            elif hasattr(part, "as_image"):
                pil_img = part.as_image()
                if pil_img:
                    buf = io.BytesIO()
                    pil_img.save(buf, format="PNG")
                    image_bytes = buf.getvalue()
                    break

        if not image_bytes:
            return {"error": "Failed to generate image bytes from model response."}

        filename = f"recipe_{uuid.uuid4().hex[:8]}.png"

        # 1. Save with tool_context.save_artifact for Playground Artifacts panel
        part_artifact = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        await tool_context.save_artifact(
            filename=filename,
            artifact=part_artifact,
        )

        # 2. Upload image bytes directly to public Cloud Storage bucket (without writing local file)
        storage_client = storage.Client(project="qwiklabs-gcp-02-76b9ced258ff")
        bucket = storage_client.bucket(HARDCODED_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/png")

        public_url = f"https://storage.googleapis.com/{HARDCODED_BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "item_name": item_name,
            "artifact_filename": filename,
            "public_url": public_url,
        }
    except Exception as e:
        logger.error(f"Error generating or uploading recipe image: {e}")
        return {"error": str(e)}
