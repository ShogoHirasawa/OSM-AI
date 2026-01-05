"""
OSM AI Agent - QGIS Plugin
A QGIS plugin that uses LLM to generate Overpass queries from natural language.
"""


def classFactory(iface):
    """
    Load OsmAiPlugin class from file osm_ai_plugin.
    
    Args:
        iface: A QGIS interface instance.
        
    Returns:
        OsmAiPlugin instance
    """
    from .osm_ai_plugin import OsmAiPlugin
    return OsmAiPlugin(iface)

