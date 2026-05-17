from typing import List, Dict, Any
from google.genai import types


def _convert_messages(messages: List[Dict[str, Any]]):
    """
    將 OpenAI 格式的 messages 轉換成 Gemini 格式。
    system message 單獨提取，其餘轉成 contents。
    回傳 (system_instruction, contents)
    """
    system_instruction = None
    contents = []

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")

        if role == "system":
            system_instruction = content
        elif role == "user":
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=content)]
            ))
        elif role == "assistant":
            contents.append(types.Content(
                role="model",
                parts=[types.Part.from_text(text=content)]
            ))

    return system_instruction, contents
