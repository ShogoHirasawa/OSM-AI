"""
Overpass API client for OSM AI Agent plugin.
Fetches OSM data and converts it to GeoJSON.
"""

import json
from typing import Any, Dict, List, Optional

import requests


OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
TIMEOUT = 60  # seconds


def fetch_osm_geojson(overpass_query: str) -> str:
    """
    Execute Overpass QL query and return result as GeoJSON string.
    
    Args:
        overpass_query: Overpass QL query text (should use [out:json])
        
    Returns:
        GeoJSON string (UTF-8)
        
    Raises:
        RuntimeError: If API call fails or conversion fails
    """
    try:
        # Call Overpass API
        response = requests.post(
            OVERPASS_API_URL,
            data={"data": overpass_query},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        # Parse response
        osm_data = response.json()
        
        if "elements" not in osm_data:
            raise RuntimeError("Invalid Overpass API response: missing 'elements'")
        
        # Convert to GeoJSON
        geojson = convert_overpass_to_geojson(osm_data)
        
        # Return as JSON string
        return json.dumps(geojson, ensure_ascii=False)
        
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Overpass API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse Overpass API response: {str(e)}")
    except Exception as e:
        if isinstance(e, RuntimeError):
            raise
        raise RuntimeError(f"Unexpected error fetching OSM data: {str(e)}")


def convert_overpass_to_geojson(osm_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Overpass JSON format to GeoJSON.
    
    This is a simplified conversion that handles basic geometries:
    - nodes as Points
    - ways with geometry as LineStrings or Polygons
    - relations are currently skipped (can be improved in the future)
    
    Args:
        osm_data: Overpass JSON response
        
    Returns:
        GeoJSON dictionary
    """
    features = []
    
    # Create lookup for nodes (needed for way geometry)
    nodes = {}
    for element in osm_data.get("elements", []):
        if element.get("type") == "node":
            nodes[element["id"]] = {
                "lat": element.get("lat"),
                "lon": element.get("lon")
            }
    
    # Process elements
    for element in osm_data.get("elements", []):
        element_type = element.get("type")
        
        if element_type == "node":
            # Convert node to Point
            feature = convert_node_to_feature(element)
            if feature:
                features.append(feature)
                
        elif element_type == "way":
            # Convert way to LineString or Polygon
            feature = convert_way_to_feature(element, nodes)
            if feature:
                features.append(feature)
                
        # Skip relations for now (can be added later)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


def convert_node_to_feature(node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convert OSM node to GeoJSON Point feature.
    
    Args:
        node: OSM node element
        
    Returns:
        GeoJSON feature or None if invalid
    """
    lat = node.get("lat")
    lon = node.get("lon")
    
    if lat is None or lon is None:
        return None
    
    return {
        "type": "Feature",
        "id": f"node/{node.get('id')}",
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        },
        "properties": node.get("tags", {})
    }


def convert_way_to_feature(way: Dict[str, Any], nodes: Dict[int, Dict[str, float]]) -> Optional[Dict[str, Any]]:
    """
    Convert OSM way to GeoJSON LineString or Polygon feature.
    
    Args:
        way: OSM way element
        nodes: Dictionary of node_id -> {lat, lon}
        
    Returns:
        GeoJSON feature or None if invalid
    """
    # Get coordinates from geometry or nodes
    coordinates = []
    
    # Check if geometry is already included in the response
    if "geometry" in way:
        coordinates = [[n["lon"], n["lat"]] for n in way["geometry"]]
    elif "nodes" in way:
        # Look up node coordinates
        for node_id in way["nodes"]:
            if node_id in nodes:
                node_data = nodes[node_id]
                coordinates.append([node_data["lon"], node_data["lat"]])
    
    if len(coordinates) < 2:
        return None
    
    # Determine if it's a closed way (polygon) or open way (linestring)
    is_closed = (
        len(coordinates) >= 4 and 
        coordinates[0] == coordinates[-1]
    )
    
    # Check tags to determine if it should be a polygon
    tags = way.get("tags", {})
    is_area = (
        is_closed and (
            tags.get("area") == "yes" or
            "building" in tags or
            "landuse" in tags or
            "natural" in tags or
            "leisure" in tags or
            "amenity" in tags
        )
    )
    
    if is_area:
        geometry_type = "Polygon"
        # Polygon coordinates are nested: [[[lon, lat], ...]]
        geometry_coords = [coordinates]
    else:
        geometry_type = "LineString"
        geometry_coords = coordinates
    
    return {
        "type": "Feature",
        "id": f"way/{way.get('id')}",
        "geometry": {
            "type": geometry_type,
            "coordinates": geometry_coords
        },
        "properties": tags
    }

