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

"""Unit tests for A2UI integration and callback."""

from unittest.mock import MagicMock
from app.a2ui_utils import a2ui_callback
from app.agent import root_agent
from google.adk.models.llm_response import LlmResponse
from google.genai import types


def test_agent_has_a2ui_callback():
    assert root_agent.after_model_callback == a2ui_callback


def test_a2ui_callback_rewraps_json():
    mock_context = MagicMock()
    a2ui_json = '[{"beginRendering": {"surfaceId": "main", "root": "card1"}}, {"surfaceUpdate": {"surfaceId": "main", "components": [{"id": "card1", "component": {"Card": {"child": "text1"}}}, {"id": "text1", "component": {"Text": {"text": {"literalString": "Hello A2UI"}}}}]}}]'
    response = LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text=a2ui_json)])
    )

    result = a2ui_callback(mock_context, response)
    assert result is not None
    assert result.custom_metadata == {"a2a:response": "true"}
    assert len(result.content.parts) == 2
