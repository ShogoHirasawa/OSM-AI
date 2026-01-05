"""
LLM client for OSM AI Agent plugin.
Calls OpenAI API to generate Overpass QL queries from natural language.
"""

import json
import os
from typing import Dict, Tuple, Optional, List

import requests

from .settings import load_api_key


# OpenAI API configuration
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
MODEL_NAME = "gpt-4o-mini"
TIMEOUT = 60  # seconds


BBox = Tuple[float, float, float, float]


SYSTEM_PROMPT = """You are an assistant with expertise in OpenStreetMap (OSM) and Overpass API.

You will receive the following JSON input:
- user_message: User's instruction in natural language
- bbox: Geographic bounding box in "south,west,north,east" format (latitude, longitude)
- chat_history: Array of previous conversation history
- language: User's language code (e.g., ja, en, zh, es, etc.)

You can respond in two modes:

## Mode 1: Chat Mode (mode: "chat")
Use chat mode when the user's input is ambiguous, or if it's a question/greeting.

{
  "mode": "chat",
  "message": "Your response message to the user"
}

## Mode 2: Query Execution Mode (mode: "query")
Use this mode ONLY when the user's request is clear and OSM data can be retrieved.

{
  "mode": "query",
  "description": "Short name to be used as QGIS layer name. Keep it concise within 2-3 words (e.g., Hospitals, Cafes, Parks, Convenience Stores)",
  "overpass_query": "Executable Overpass QL query (string)",
  "expected_geometry": "point" or "line" or "polygon",
  "notes": "Additional information if any (empty string if none)"
}

## Geographic Area Specification:

You can use TWO methods to specify search area:

### Method 1: Bounding Box (when no specific location is mentioned)
Use the provided bbox coordinates when user doesn't specify a particular place:
```
[out:json][timeout:60];
(
  node["tag"="value"](south,west,north,east);
  way["tag"="value"](south,west,north,east);
);
out geom;
```

### Method 2: Area Search (when user mentions a specific location)
When the user specifies a place name (e.g., "横浜市", "渋谷区", "Tokyo", "Shibuya"), use area search:
```
[out:json][timeout:60];
area["name"="Place Name"]->.searchArea;
(
  node["tag"="value"](area.searchArea);
  way["tag"="value"](area.searchArea);
);
out geom;
```

**Important Decision Criteria:**
- If user mentions a **specific place name** → USE METHOD 2 (area search)
- If **no place name** is mentioned → USE METHOD 1 (bbox)
- For area search, use the exact place name in the user's language
- Common place name patterns: city names, ward names (区), prefecture names (県/府/道), district names
- Examples: "横浜市の病院" → use area["name"="横浜市"], "Get cafes in Shibuya" → use area["name"="Shibuya"]

## Important Decision Criteria:

**Use Chat Mode (mode: "chat") when:**
- User input is a greeting or question (e.g., "Hello", "What is this?")
- What to search for is not clear
- Additional information is needed
- User is asking how to use the tool

**Use Query Mode (mode: "query") when:**
- User is specifically requesting OSM data
- Examples: "Get convenience stores", "Show cafes", "Search for parks"

## Language Support:
- **ALWAYS respond in the language specified in the language field**
- Write all output (description, message, etc.) in the specified language
- If language="ja", respond in Japanese; if language="en", respond in English

## Additional Requirements:
- All queries must start with [out:json][timeout:60];
- Always include coordinate information using out geom;
- Use standard OSM tags (refer to https://wiki.openstreetmap.org/wiki/Map_features)
- Choose between bbox or area search based on user input
"""


def call_llm_for_overpass(user_message: str, bbox: BBox, chat_history: Optional[list] = None, user_language: str = "en") -> Dict[str, str]:
    """
    Call OpenAI API to generate Overpass QL query from natural language.
    
    Args:
        user_message: User's natural language instruction
        bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
        
    Returns:
        Dictionary with keys:
        - description: str
        - overpass_query: str
        - expected_geometry: str ("point" | "line" | "polygon")
        - notes: str
        
    Raises:
        RuntimeError: If API call fails or response is invalid
    """
    # Get API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = load_api_key()
    if not api_key:
        raise RuntimeError(
            "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
            "or configure it in plugin settings."
        )
    
    # Format bbox for Overpass API
    bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"  # lat_min,lon_min,lat_max,lon_max
    
    # Prepare chat history
    if chat_history is None:
        chat_history = []
    
    # Prepare request payload
    user_content = json.dumps({
        "user_message": user_message,
        "bbox": bbox_str,
        "chat_history": chat_history,
        "language": user_language
    }, ensure_ascii=False)
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.7,
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        # Call OpenAI API
        response = requests.post(
            OPENAI_API_URL,
            headers=headers,
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        if "choices" not in result or len(result["choices"]) == 0:
            raise RuntimeError("Invalid response from OpenAI API: no choices")
        
        content = result["choices"][0]["message"]["content"]
        
        # Parse JSON from content
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse LLM response as JSON: {content}")
        
        # Validate mode field
        if "mode" not in parsed:
            raise RuntimeError("Missing 'mode' field in LLM response")
        
        mode = parsed["mode"]
        
        # Validate based on mode
        if mode == "chat":
            # Chat mode: only requires message
            if "message" not in parsed:
                raise RuntimeError("Missing 'message' field in chat mode response")
        elif mode == "query":
            # Query mode: requires all query fields
            required_fields = ["description", "overpass_query", "expected_geometry", "notes"]
            for field in required_fields:
                if field not in parsed:
                    raise RuntimeError(f"Missing required field in LLM response: {field}")
            
            if not parsed["overpass_query"]:
                raise RuntimeError("Empty overpass_query in LLM response")
        else:
            raise RuntimeError(f"Invalid mode in LLM response: {mode}")
        
        return parsed
        
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"OpenAI API request failed: {str(e)}")
    except Exception as e:
        if isinstance(e, RuntimeError):
            raise
        raise RuntimeError(f"Unexpected error calling LLM: {str(e)}")

