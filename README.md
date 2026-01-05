# OSM AI - QGIS Plugin
![demo](https://github.com/user-attachments/assets/d87e510e-8ad2-4099-bdaf-26d723e7efbf)

## Overview

**OSM AI** is a QGIS plugin that lets you search and fetch OpenStreetMap data using a chat interface. It uses LLM (OpenAI API) to automatically generate Overpass QL queries and add OSM data as QGIS layers.

* **Note**: You need to obtain an OpenAI API key. API usage fees are your responsibility.

## Installation

### Install from ZIP file

1. **Download the plugin ZIP file**

   Download from here:
   
   👉 **[Download osm_ai.zip]([osm_ai.zip](https://github.com/user-attachments/files/24428320/osm_ai.zip))**

2. **Open QGIS** and go to **"Plugins" → "Manage and Install Plugins"**

3. Select the **"Install from ZIP"** tab

4. Select the downloaded **`osm_ai.zip`** and install

5. Enable "OSM AI" in the **"Installed"** tab

## Setup

### Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/) and create an account

2. Create a new API key on the [API Keys](https://platform.openai.com/api-keys) page

3. Copy the API key

4. Open an API setting page in QGIS
**"Plugins" → "OSM AI Agent" → "Settings"**
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/c979195e-aa90-4910-af2b-85be30a88575" />

5. Set your API key
<img width="500" height="500" alt="API setting page" src="https://github.com/user-attachments/assets/0526c26c-c3fa-4914-87d5-fcb26e8b0e12" />

## Key Features

### Chat-Based Data Search
- **Multi-language support**: UI language automatically adapts to your QGIS language settings (Japanese, English, Chinese, Spanish, etc.)
- **Conversational interface**: Enter requests naturally like chatting

### Chat Functions
- **Multiple tabs**: Run different search tasks in parallel across multiple tabs
- **History retention**: Each tab keeps its own chat history for context-aware searches

### Flexible Geographic Search
1. **Current view search**: Automatically detects the map view's bounding box
2. **Location-based search**: Search by place name (e.g., "city halls in Yokohama", "cafes in Shibuya")

### Keyboard Shortcuts
- Send messages with **Enter** or **Command+Enter** (configurable)
- Efficient operation

## Requirements

- **QGIS**: 3.x or higher
- **Python**: 3.9 or higher (included in QGIS)
- **Internet connection**: Required for OpenAI API and Overpass API
- **OpenAI API key**: Obtain from [OpenAI Platform](https://platform.openai.com/)


### Configure API Key in Plugin

1. After enabling the plugin in QGIS, click the **OSM AI icon** in the toolbar

2. When the dock widget appears, click the **⚙️ settings icon** in the top right

3. Paste your API key in the **"OpenAI API Key"** field

4. Select your preferred **"Send Shortcut"**:
   - **Enter**: Send with Enter key (new line with Shift+Enter)
   - **Command+Enter**: Send with Command+Enter (Ctrl+Enter on Windows/Linux)

5. Click **"OK"** to save

> **💡 Tip**: If you set the `OPENAI_API_KEY` environment variable, you don't need to enter it in the plugin settings.

## Usage

### Basic Usage

1. **Open a QGIS project**  
   Display the area you want to explore in the map view

2. **Launch the plugin**  
   Click the **OSM AI icon** in the toolbar, or select **"Plugins" → "OSM AI"** from the menu

3. **Search in natural language**  
   Enter your request in natural language

   **Examples**:
   - "Show convenience stores in Tokyo"
   - "Display parks in the current view"
   - "Show museums in New York"

4. **Send**  
   - Click the **Send button**
   - Or press **Enter** (or **Command+Enter**)

5. **Data automatically added**  
   - Plugin generates Overpass QL query
   - Fetches OSM data from Overpass API
   - Adds new layer to QGIS layer panel

### Multiple Tabs

You can run multiple search tasks in parallel:

1. **Create new tab**: Click the **➕ icon** above the input field

2. **Switch tabs**: Click on tabs to switch between them

3. **Close tab**: Click the **✕ icon** on the tab

Each tab has its own chat history for context-aware conversations.

### Chat Features

OSM AI is not just a data search tool—you can use it conversationally:

- **Greetings**: Say "Hello" and it will respond
- **Questions**: Ask "How do I use this plugin?"
- **Context understanding**: It remembers previous messages, so you can say "Show me more"

## Settings

### Keyboard Shortcuts

You can select the send shortcut in the **settings screen** (⚙️ icon):

- **Enter**: 
  - Send message: **Enter**
  - New line: **Shift+Enter**
  
- **Command+Enter** (recommended):
  - Send message: **Command+Enter** (Mac) or **Ctrl+Enter** (Windows/Linux)
  - New line: **Enter**

## Troubleshooting

### "API key not found" Error

**Cause**: OpenAI API key is not configured

**Solution**:
1. Open the plugin settings screen
2. Enter your OpenAI API Key
3. Verify the key is valid at [OpenAI Platform](https://platform.openai.com/api-keys)

### "Overpass API request failed: 400" Error

**Cause**: Generated query is invalid or search area is inappropriate

**Solution**:
1. Try entering more specific instructions
2. Try searches with place names (e.g., "cafes in Tokyo")
3. Zoom in on the map and try again

### Cannot Fetch Data

**Cause**: Overpass API rate limit or too much data requested

**Solution**:
1. Check your internet connection
2. Wait a few minutes before retrying (consecutive requests may be blocked)
3. Zoom in to narrow the search area
4. Specify more specific categories (e.g., "stores" → "convenience stores")

### Added Layer Not Visible

**Cause**: Data extent may be outside the current view

**Solution**:
1. Check for error messages in the QGIS message bar
2. Right-click the fetched layer in the layer panel
3. Select **"Zoom to Layer"**

### Plugin Won't Start

**Cause**: Incomplete installation or Python environment issue

**Solution**:
1. Restart QGIS
2. Disable and re-enable the plugin
3. Reinstall the plugin
4. Check error messages in the QGIS Python console

## Technical Information

### APIs Used

- OpenAI API
- Overpass API

### Directory Structure

```
osm_ai/
├── __init__.py              # Plugin entry point
├── metadata.txt             # Plugin metadata
├── osm_ai_plugin.py         # Main plugin code
├── icon.png                 # Plugin icon
├── resources.qrc            # Qt resource definition
├── resources.py             # Qt resources (generated)
├── core/                    # Core logic
│   ├── __init__.py
│   ├── settings.py          # Settings management (API key, shortcuts)
│   ├── llm_client.py        # OpenAI API calls
│   ├── overpass_client.py   # Overpass API calls
│   └── qgis_utils.py        # QGIS integration (layer addition, etc.)
└── ui/                      # User interface
    ├── __init__.py
    ├── osm_ai.ui            # Qt Designer UI file
    ├── osm_ai_form.py       # Generated UI code
    └── icon/                # SVG icons
        ├── agent.svg
        ├── user.svg
        ├── plus.svg
        ├── xmark.svg
        └── sent.svg
```

All dependencies are included in the standard QGIS environment—no additional installation required.

## FAQ

**Q: Can I use other LLMs (Claude, Gemini, etc.) besides OpenAI API?**  
A: Currently, only OpenAI API is supported. Support for other providers is planned for the future.

**Q: Are there API usage fees?**  
A: Yes. OpenAI API uses pay-as-you-go pricing. Users are responsible for their own API costs. In the future, we plan to develop a version that doesn't require users to provide their own OpenAI API key.

**Q: Can I use it offline?**  
A: No. Internet connection is required.

**Q: What types of data can I fetch?**  
A: Any data available in OpenStreetMap (POIs, roads, buildings, land use, etc.).

**Q: Can I use languages other than English?**  
A: Yes. Multiple languages are supported including Japanese, English, Chinese, and Spanish. The UI automatically adapts to your QGIS language settings.

## Support

For bug reports, feature requests, or questions, please contact us.

Contact: origami.no.1@gmail.com
