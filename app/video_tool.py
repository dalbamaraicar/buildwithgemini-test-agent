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

"""Video generation tool using gemini-omni-flash-preview for Smart Pantry Chef."""

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


async def generate_recipe_video(
    item_name: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Generates a short video for a food item or recipe, saves it as an artifact, and uploads it to public Cloud Storage.

    Args:
        item_name: Name or description of the food item or recipe to generate a short video for (e.g., 'Sizzling Garlic Butter Shrimp').
        tool_context: ADK execution context for saving session artifacts.

    Returns:
        Dictionary containing the public Cloud Storage video URL, item name, and artifact filename.
    """
    try:
        # Initialize Gemini Client for global region as required for gemini-omni-flash-preview
        client = genai.Client(location="global")
        prompt = f"A short, appetizing culinary video showcasing {item_name} being freshly prepared and plated, vibrant colors, cinematic slow motion."

        response = client.models.generate_content(
            model="gemini-omni-flash-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["VIDEO"],
            ),
        )

        video_bytes = None
        mime_type = "video/mp4"

        for part in response.parts:
            if part.inline_data and part.inline_data.data:
                video_bytes = part.inline_data.data
                if part.inline_data.mime_type:
                    mime_type = part.inline_data.mime_type
                break

        if not video_bytes:
            return {"error": "Failed to generate video bytes from model response."}

        filename = f"recipe_video_{uuid.uuid4().hex[:8]}.mp4"

        # 1. Save with tool_context.save_artifact so it shows up in Playground Artifacts panel
        part_artifact = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        await tool_context.save_artifact(
            filename=filename,
            artifact=part_artifact,
        )

        # 2. Upload video bytes directly to public Cloud Storage bucket (without local file)
        storage_client = storage.Client(project="qwiklabs-gcp-02-76b9ced258ff")
        bucket = storage_client.bucket(HARDCODED_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{HARDCODED_BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "item_name": item_name,
            "artifact_filename": filename,
            "public_url": public_url,
        }
    except Exception as e:
        logger.error(f"Error generating or uploading recipe video: {e}")
        return {"error": str(e)}
