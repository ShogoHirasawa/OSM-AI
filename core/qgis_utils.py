"""
QGIS-specific utilities for OSM AI Agent plugin.
Handles bbox extraction and layer management.
"""

from typing import Tuple
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsVectorLayer,
)
from qgis.utils import iface


BBox = Tuple[float, float, float, float]


def get_current_bbox_wgs84() -> BBox:
    """
    Get the current map canvas extent as WGS84 bbox.
    
    Returns:
        Tuple of (min_lon, min_lat, max_lon, max_lat)
        
    Raises:
        RuntimeError: If unable to get map canvas or transform coordinates
    """
    try:
        canvas = iface.mapCanvas()
        extent = canvas.extent()
        
        # Get current CRS
        source_crs = canvas.mapSettings().destinationCrs()
        
        # Target CRS: WGS84 (EPSG:4326)
        target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        
        # Transform extent to WGS84
        transform = QgsCoordinateTransform(source_crs, target_crs, QgsProject.instance())
        transformed_extent = transform.transformBoundingBox(extent)
        
        # Return as (min_lon, min_lat, max_lon, max_lat)
        return (
            transformed_extent.xMinimum(),
            transformed_extent.yMinimum(),
            transformed_extent.xMaximum(),
            transformed_extent.yMaximum(),
        )
    except Exception as e:
        raise RuntimeError(f"Failed to get current bbox: {str(e)}")


def add_geojson_layer(geojson_str: str, layer_name: str) -> None:
    """
    Add a GeoJSON string as a vector layer to QGIS.
    
    Args:
        geojson_str: GeoJSON string (UTF-8)
        layer_name: Name for the layer
        
    Raises:
        RuntimeError: If unable to create or add the layer
    """
    try:
        # Create vector layer from GeoJSON string
        layer = QgsVectorLayer(geojson_str, layer_name, "ogr")
        
        if not layer.isValid():
            raise RuntimeError(f"Failed to create valid layer from GeoJSON")
        
        # Add layer to project
        QgsProject.instance().addMapLayer(layer)
        
    except Exception as e:
        raise RuntimeError(f"Failed to add GeoJSON layer: {str(e)}")

