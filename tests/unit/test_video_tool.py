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

"""Unit tests for generate_recipe_video tool."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.video_tool import generate_recipe_video


@pytest.mark.asyncio
@patch("google.cloud.storage.Client")
@patch("google.genai.Client")
async def test_generate_recipe_video(mock_genai_client, mock_storage_client):
    # Mock Gemini response
    mock_part = MagicMock()
    mock_part.inline_data.data = b"fake_mp4_video_bytes"
    mock_part.inline_data.mime_type = "video/mp4"
    mock_genai_response = MagicMock()
    mock_genai_response.parts = [mock_part]
    mock_genai_instance = MagicMock()
    mock_genai_instance.models.generate_content.return_value = mock_genai_response
    mock_genai_client.return_value = mock_genai_instance

    # Mock Storage Client
    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_storage_instance = MagicMock()
    mock_storage_instance.bucket.return_value = mock_bucket
    mock_storage_client.return_value = mock_storage_instance

    # Mock ToolContext
    mock_tool_context = MagicMock()
    mock_tool_context.save_artifact = AsyncMock()

    result = await generate_recipe_video("Sizzling Garlic Butter Shrimp", mock_tool_context)

    assert result["status"] == "success"
    assert result["item_name"] == "Sizzling Garlic Butter Shrimp"
    assert "public_url" in result
    assert result["public_url"].startswith("https://storage.googleapis.com/smart-pantry-chef-media-qwiklabs-gcp-02-76b9ced258ff/")

    # Verify save_artifact called
    mock_tool_context.save_artifact.assert_called_once()

    # Verify upload_from_string called without saving local file
    mock_blob.upload_from_string.assert_called_once_with(b"fake_mp4_video_bytes", content_type="video/mp4")
