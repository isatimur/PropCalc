"""
KML Processor for transforming KML files into database-friendly formats
Handles sectors, communities, and entrance points for area searches and mapping
"""

import xml.etree.ElementTree as ET
import json
import logging
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)

@dataclass
class PolygonData:
    """Represents polygon data extracted from KML"""
    object_id: int
    name: str
    coordinates: List[Tuple[float, float, float]]  # lon, lat, altitude
    properties: Dict[str, Any]
    area: Optional[float] = None
    perimeter: Optional[float] = None

@dataclass
class PointData:
    """Represents point data extracted from KML"""
    object_id: int
    name: str
    coordinates: Tuple[float, float, float]  # lon, lat, altitude
    properties: Dict[str, Any]

class KMLProcessor:
    """Processes KML files and converts them to database-friendly formats"""
    
    def __init__(self):
        self.namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    def parse_kml_file(self, file_path: str) -> Dict[str, Any]:
        """Parse KML file and extract all data"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract schema information
            schema = self._extract_schema(root)
            
            # Extract placemarks
            placemarks = self._extract_placemarks(root)
            
            return {
                'schema': schema,
                'placemarks': placemarks,
                'file_path': file_path,
                'processed_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing KML file {file_path}: {e}")
            raise
    
    def _extract_schema(self, root: ET.Element) -> Dict[str, Any]:
        """Extract schema information from KML"""
        schema = {}
        schema_elem = root.find('.//kml:Schema', self.namespace)
        if schema_elem is not None:
            schema['name'] = schema_elem.get('name', '')
            schema['id'] = schema_elem.get('id', '')
            
            fields = []
            for field in schema_elem.findall('.//kml:SimpleField', self.namespace):
                field_info = {
                    'name': field.get('name', ''),
                    'type': field.get('type', ''),
                    'display_name': field.find('kml:displayName', self.namespace)
                }
                if field_info['display_name'] is not None:
                    field_info['display_name'] = field_info['display_name'].text
                fields.append(field_info)
            
            schema['fields'] = fields
        
        return schema
    
    def _extract_placemarks(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract all placemarks from KML"""
        placemarks = []
        
        for placemark in root.findall('.//kml:Placemark', self.namespace):
            pm_data = self._extract_placemark_data(placemark)
            if pm_data:
                placemarks.append(pm_data)
        
        return placemarks
    
    def _extract_placemark_data(self, placemark: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract data from a single placemark"""
        try:
            # Extract basic info
            name = placemark.find('kml:name', self.namespace)
            name = name.text if name is not None else ''
            
            # Extract description
            description = placemark.find('kml:description', self.namespace)
            description_text = ''
            if description is not None:
                description_text = ET.tostring(description, encoding='unicode')
            
            # Extract extended data
            extended_data = self._extract_extended_data(placemark)
            
            # Extract geometry
            geometry = self._extract_geometry(placemark)
            
            if geometry:
                return {
                    'name': name,
                    'description': description_text,
                    'properties': extended_data,
                    'geometry': geometry
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting placemark data: {e}")
            return None
    
    def _extract_extended_data(self, placemark: ET.Element) -> Dict[str, Any]:
        """Extract extended data from placemark"""
        data = {}
        
        extended_data = placemark.find('.//kml:ExtendedData', self.namespace)
        if extended_data is not None:
            schema_data = extended_data.find('.//kml:SchemaData', self.namespace)
            if schema_data is not None:
                for simple_data in schema_data.findall('.//kml:SimpleData', self.namespace):
                    name = simple_data.get('name', '')
                    value = simple_data.text or ''
                    data[name] = value
        
        return data
    
    def _extract_geometry(self, placemark: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract geometry from placemark"""
        # Check for Polygon
        polygon = placemark.find('.//kml:Polygon', self.namespace)
        if polygon is not None:
            return self._extract_polygon_geometry(polygon)
        
        # Check for Point
        point = placemark.find('.//kml:Point', self.namespace)
        if point is not None:
            return self._extract_point_geometry(point)
        
        # Check for LineString
        linestring = placemark.find('.//kml:LineString', self.namespace)
        if linestring is not None:
            return self._extract_linestring_geometry(linestring)
        
        return None
    
    def _extract_polygon_geometry(self, polygon: ET.Element) -> Dict[str, Any]:
        """Extract polygon geometry"""
        coordinates = []
        
        # Extract outer boundary
        outer_boundary = polygon.find('.//kml:outerBoundaryIs', self.namespace)
        if outer_boundary is not None:
            linear_ring = outer_boundary.find('.//kml:LinearRing', self.namespace)
            if linear_ring is not None:
                coords_elem = linear_ring.find('.//kml:coordinates', self.namespace)
                if coords_elem is not None and coords_elem.text:
                    coordinates = self._parse_coordinates(coords_elem.text)
        
        return {
            'type': 'Polygon',
            'coordinates': coordinates
        }
    
    def _extract_point_geometry(self, point: ET.Element) -> Dict[str, Any]:
        """Extract point geometry"""
        coords_elem = point.find('.//kml:coordinates', self.namespace)
        coordinates = None
        
        if coords_elem is not None and coords_elem.text:
            coords = self._parse_coordinates(coords_elem.text)
            if coords:
                coordinates = coords[0]  # Take first coordinate for point
        
        return {
            'type': 'Point',
            'coordinates': coordinates
        }
    
    def _extract_linestring_geometry(self, linestring: ET.Element) -> Dict[str, Any]:
        """Extract linestring geometry"""
        coords_elem = linestring.find('.//kml:coordinates', self.namespace)
        coordinates = []
        
        if coords_elem is not None and coords_elem.text:
            coordinates = self._parse_coordinates(coords_elem.text)
        
        return {
            'type': 'LineString',
            'coordinates': coordinates
        }
    
    def _parse_coordinates(self, coord_text: str) -> List[Tuple[float, float, float]]:
        """Parse coordinate string into list of tuples"""
        coordinates = []
        
        # Clean and split coordinate string
        coord_text = coord_text.strip()
        coord_pairs = re.split(r'\s+', coord_text)
        
        for pair in coord_pairs:
            if pair.strip():
                parts = pair.split(',')
                if len(parts) >= 2:
                    try:
                        lon = float(parts[0])
                        lat = float(parts[1])
                        alt = float(parts[2]) if len(parts) > 2 else 0.0
                        coordinates.append((lon, lat, alt))
                    except ValueError:
                        continue
        
        return coordinates
    
    def calculate_polygon_area(self, coordinates: List[Tuple[float, float, float]]) -> float:
        """Calculate polygon area using shoelace formula"""
        if len(coordinates) < 3:
            return 0.0
        
        # Convert to radians and use spherical approximation
        area = 0.0
        for i in range(len(coordinates)):
            j = (i + 1) % len(coordinates)
            lon1, lat1, _ = coordinates[i]
            lon2, lat2, _ = coordinates[j]
            
            # Convert to radians
            lon1_rad = math.radians(lon1)
            lat1_rad = math.radians(lat1)
            lon2_rad = math.radians(lon2)
            lat2_rad = math.radians(lat2)
            
            # Spherical approximation
            area += (lon2_rad - lon1_rad) * (2 + math.sin(lat1_rad) + math.sin(lat2_rad))
        
        # Convert to square meters (approximate)
        earth_radius = 6371000  # meters
        area = abs(area) * earth_radius * earth_radius / 2.0
        
        return area
    
    def calculate_polygon_perimeter(self, coordinates: List[Tuple[float, float, float]]) -> float:
        """Calculate polygon perimeter"""
        if len(coordinates) < 2:
            return 0.0
        
        perimeter = 0.0
        for i in range(len(coordinates)):
            j = (i + 1) % len(coordinates)
            lon1, lat1, _ = coordinates[i]
            lon2, lat2, _ = coordinates[j]
            
            # Haversine formula for distance
            perimeter += self._haversine_distance(lat1, lon1, lat2, lon2)
        
        return perimeter
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        import math
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in meters
        earth_radius = 6371000
        return earth_radius * c
    
    def transform_to_database_format(self, kml_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform KML data to database-friendly format"""
        transformed_data = {
            'metadata': {
                'source_file': kml_data.get('file_path', ''),
                'processed_at': kml_data.get('processed_at', ''),
                'schema': kml_data.get('schema', {}),
                'total_placemarks': len(kml_data.get('placemarks', []))
            },
            'areas': [],
            'points': [],
            'lines': []
        }
        
        for placemark in kml_data.get('placemarks', []):
            geometry = placemark.get('geometry', {})
            geometry_type = geometry.get('type', '')
            
            if geometry_type == 'Polygon':
                area_data = self._create_area_record(placemark, geometry)
                if area_data:
                    transformed_data['areas'].append(area_data)
            
            elif geometry_type == 'Point':
                point_data = self._create_point_record(placemark, geometry)
                if point_data:
                    transformed_data['points'].append(point_data)
            
            elif geometry_type == 'LineString':
                line_data = self._create_line_record(placemark, geometry)
                if line_data:
                    transformed_data['lines'].append(line_data)
        
        return transformed_data
    
    def _create_area_record(self, placemark: Dict[str, Any], geometry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create area record from polygon placemark"""
        try:
            coordinates = geometry.get('coordinates', [])
            if not coordinates:
                return None
            
            # Calculate area and perimeter
            area = self.calculate_polygon_area(coordinates)
            perimeter = self.calculate_polygon_perimeter(coordinates)
            
            # Create center point for address generation
            center_lon = sum(coord[0] for coord in coordinates) / len(coordinates)
            center_lat = sum(coord[1] for coord in coordinates) / len(coordinates)
            
            return {
                'id': placemark.get('properties', {}).get('OBJECTID', 0),
                'name': placemark.get('name', ''),
                'name_arabic': placemark.get('properties', {}).get('CNAME_A', ''),
                'name_english': placemark.get('properties', {}).get('CNAME_E', ''),
                'sector_number': placemark.get('properties', {}).get('SEC_NUM', ''),
                'community_number': placemark.get('properties', {}).get('COMM_NUM', ''),
                'dgis_id': placemark.get('properties', {}).get('DGIS_ID', ''),
                'ndgis_id': placemark.get('properties', {}).get('NDGIS_ID', ''),
                'center_latitude': center_lat,
                'center_longitude': center_lon,
                'area_sqm': area,
                'perimeter_m': perimeter,
                'polygon_coordinates': coordinates,
                'properties': placemark.get('properties', {}),
                'geometry_type': 'Polygon'
            }
        except Exception as e:
            logger.error(f"Error creating area record: {e}")
            return None
    
    def _create_point_record(self, placemark: Dict[str, Any], geometry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create point record from point placemark"""
        try:
            coordinates = geometry.get('coordinates')
            if not coordinates:
                return None
            
            lon, lat, alt = coordinates
            
            return {
                'id': placemark.get('properties', {}).get('OBJECTID', 0),
                'name': placemark.get('name', ''),
                'latitude': lat,
                'longitude': lon,
                'altitude': alt,
                'properties': placemark.get('properties', {}),
                'geometry_type': 'Point'
            }
        except Exception as e:
            logger.error(f"Error creating point record: {e}")
            return None
    
    def _create_line_record(self, placemark: Dict[str, Any], geometry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create line record from linestring placemark"""
        try:
            coordinates = geometry.get('coordinates', [])
            if not coordinates:
                return None
            
            return {
                'id': placemark.get('properties', {}).get('OBJECTID', 0),
                'name': placemark.get('name', ''),
                'coordinates': coordinates,
                'properties': placemark.get('properties', {}),
                'geometry_type': 'LineString'
            }
        except Exception as e:
            logger.error(f"Error creating line record: {e}")
            return None
    
    def generate_address_from_coordinates(self, lat: float, lon: float) -> str:
        """Generate address from coordinates (placeholder for geocoding service)"""
        # This would typically use a geocoding service like Google Maps API
        # For now, return a formatted coordinate string
        return f"Lat: {lat:.6f}, Lon: {lon:.6f}"
    
    def process_all_kml_files(self, data_directory: str) -> Dict[str, Any]:
        """Process all KML files in the data directory"""
        import os
        import glob
        
        results = {}
        
        # Find all KML files
        kml_files = glob.glob(os.path.join(data_directory, "*.kml"))
        
        for kml_file in kml_files:
            try:
                logger.info(f"Processing KML file: {kml_file}")
                
                # Parse KML file
                kml_data = self.parse_kml_file(kml_file)
                
                # Transform to database format
                transformed_data = self.transform_to_database_format(kml_data)
                
                # Store results
                file_name = os.path.basename(kml_file)
                results[file_name] = transformed_data
                
                logger.info(f"Successfully processed {file_name}: "
                          f"{len(transformed_data['areas'])} areas, "
                          f"{len(transformed_data['points'])} points, "
                          f"{len(transformed_data['lines'])} lines")
                
            except Exception as e:
                logger.error(f"Error processing {kml_file}: {e}")
                results[os.path.basename(kml_file)] = {'error': str(e)}
        
        return results
    
    def export_to_json(self, data: Dict[str, Any], output_file: str):
        """Export processed data to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Exported data to {output_file}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise
    
    def export_to_csv(self, data: Dict[str, Any], output_directory: str):
        """Export processed data to CSV files"""
        import csv
        import os
        
        try:
            os.makedirs(output_directory, exist_ok=True)
            
            for file_name, file_data in data.items():
                if isinstance(file_data, dict) and 'error' not in file_data:
                    # Export areas
                    if file_data.get('areas'):
                        areas_file = os.path.join(output_directory, f"{file_name}_areas.csv")
                        self._export_areas_to_csv(file_data['areas'], areas_file)
                    
                    # Export points
                    if file_data.get('points'):
                        points_file = os.path.join(output_directory, f"{file_name}_points.csv")
                        self._export_points_to_csv(file_data['points'], points_file)
                    
                    # Export lines
                    if file_data.get('lines'):
                        lines_file = os.path.join(output_directory, f"{file_name}_lines.csv")
                        self._export_lines_to_csv(file_data['lines'], lines_file)
            
            logger.info(f"Exported data to CSV files in {output_directory}")
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def _export_areas_to_csv(self, areas: List[Dict[str, Any]], output_file: str):
        """Export areas to CSV"""
        import csv
        
        if not areas:
            return
        
        fieldnames = [
            'id', 'name', 'name_arabic', 'name_english', 'sector_number',
            'community_number', 'dgis_id', 'ndgis_id', 'center_latitude',
            'center_longitude', 'area_sqm', 'perimeter_m', 'geometry_type'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for area in areas:
                row = {field: area.get(field, '') for field in fieldnames}
                writer.writerow(row)
    
    def _export_points_to_csv(self, points: List[Dict[str, Any]], output_file: str):
        """Export points to CSV"""
        import csv
        
        if not points:
            return
        
        fieldnames = ['id', 'name', 'latitude', 'longitude', 'altitude', 'geometry_type']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for point in points:
                row = {field: point.get(field, '') for field in fieldnames}
                writer.writerow(row)
    
    def _export_lines_to_csv(self, lines: List[Dict[str, Any]], output_file: str):
        """Export lines to CSV"""
        import csv
        
        if not lines:
            return
        
        fieldnames = ['id', 'name', 'geometry_type']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for line in lines:
                row = {field: line.get(field, '') for field in fieldnames}
                writer.writerow(row) 