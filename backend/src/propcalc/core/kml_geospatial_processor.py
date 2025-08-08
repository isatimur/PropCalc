"""
KML Geospatial Data Processor for PropCalc
Processes KML files to extract community, sector, and entrance data
"""

import json
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

class KMLDataType(Enum):
    """KML data types"""
    COMMUNITY = "community"
    SECTOR = "sector"
    ENTRANCE = "entrance"

@dataclass
class CommunityData:
    """Community data from KML"""
    object_id: int
    community_name_en: str
    community_name_ar: str
    label_en: str
    label_ar: str
    coordinates: list[tuple[float, float]]
    area_km2: float | None = None
    perimeter_km: float | None = None

@dataclass
class SectorData:
    """Sector data from KML"""
    object_id: int
    sector_number: int
    perimeter: float
    created_user: str
    created_date: str
    coordinates: list[tuple[float, float]]
    area_km2: float | None = None

@dataclass
class EntranceData:
    """Entrance data from KML"""
    entrance_id: int
    community_name: str
    coordinates: tuple[float, float]
    gzd: str
    entrance_type: str | None = None

class KMLGeospatialProcessor:
    """Process KML files to extract geospatial data"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url
        if database_url:
            self.engine = create_engine(database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.kml_dir = Path("..")  # KML files are in parent directory

    async def process_all_kml_files(self) -> dict[str, Any]:
        """Process all available KML files"""
        results = {}

        try:
            # Process Community KML
            community_file = self.kml_dir / "Community.kml"
            if community_file.exists():
                logger.info("Processing Community KML file...")
                communities = await self.process_community_kml(community_file)
                results['communities'] = {
                    'count': len(communities),
                    'data': communities
                }
                logger.info(f"Extracted {len(communities)} communities")
            else:
                logger.warning("Community.kml file not found")

            # Process Sectors KML
            sectors_file = self.kml_dir / "Sectors.kml"
            if sectors_file.exists():
                logger.info("Processing Sectors KML file...")
                sectors = await self.process_sectors_kml(sectors_file)
                results['sectors'] = {
                    'count': len(sectors),
                    'data': sectors
                }
                logger.info(f"Extracted {len(sectors)} sectors")
            else:
                logger.warning("Sectors.kml file not found")

            # Process Entrances KML
            entrances_file = self.kml_dir / "Dmgisnet_Enterances.kml"
            if entrances_file.exists():
                logger.info("Processing Entrances KML file...")
                entrances = await self.process_entrances_kml(entrances_file)
                results['entrances'] = {
                    'count': len(entrances),
                    'data': entrances
                }
                logger.info(f"Extracted {len(entrances)} entrances")
            else:
                logger.warning("Dmgisnet_Enterances.kml file not found")

            # Create geospatial mapping
            mapping = await self.create_geospatial_mapping(results)
            results['mapping'] = mapping

            return results

        except Exception as e:
            logger.error(f"Error processing KML files: {e}")
            return {'error': str(e)}

    async def process_community_kml(self, file_path: Path) -> list[CommunityData]:
        """Process Community KML file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Define namespace
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}

            communities = []

            # Find all Placemark elements
            placemarks = root.findall('.//kml:Placemark', ns)

            for placemark in placemarks:
                try:
                    # Extract ExtendedData
                    extended_data = placemark.find('.//kml:ExtendedData', ns)
                    if extended_data is None:
                        continue

                    # Extract data fields
                    data = {}
                    for simple_data in extended_data.findall('.//kml:SimpleData', ns):
                        name = simple_data.get('name')
                        value = simple_data.text
                        if name and value:
                            data[name] = value

                    # Extract coordinates
                    coordinates = self._extract_coordinates(placemark, ns)

                    if coordinates and 'OBJECTID' in data and 'CNAME_E' in data:
                        community = CommunityData(
                            object_id=int(data['OBJECTID']),
                            community_name_en=data.get('CNAME_E', ''),
                            community_name_ar=data.get('CNAME_A', ''),
                            label_en=data.get('LABEL_E', ''),
                            label_ar=data.get('LABEL_A', ''),
                            coordinates=coordinates
                        )

                        # Calculate area and perimeter
                        if coordinates:
                            area, perimeter = self._calculate_polygon_metrics(coordinates)
                            community.area_km2 = area
                            community.perimeter_km = perimeter

                        communities.append(community)

                except Exception as e:
                    logger.warning(f"Error processing community placemark: {e}")
                    continue

            return communities

        except Exception as e:
            logger.error(f"Error processing Community KML: {e}")
            return []

    async def process_sectors_kml(self, file_path: Path) -> list[SectorData]:
        """Process Sectors KML file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Define namespace
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}

            sectors = []

            # Find all Placemark elements
            placemarks = root.findall('.//kml:Placemark', ns)

            for placemark in placemarks:
                try:
                    # Extract ExtendedData
                    extended_data = placemark.find('.//kml:ExtendedData', ns)
                    if extended_data is None:
                        continue

                    # Extract data fields
                    data = {}
                    for simple_data in extended_data.findall('.//kml:SimpleData', ns):
                        name = simple_data.get('name')
                        value = simple_data.text
                        if name and value:
                            data[name] = value

                    # Extract coordinates
                    coordinates = self._extract_coordinates(placemark, ns)

                    if coordinates and 'OBJECTID' in data and 'SEC_NUM' in data:
                        sector = SectorData(
                            object_id=int(data['OBJECTID']),
                            sector_number=int(data['SEC_NUM']),
                            perimeter=float(data.get('PERIMETER', 0)),
                            created_user=data.get('CREATED_USER', ''),
                            created_date=data.get('CREATED_DATE', ''),
                            coordinates=coordinates
                        )

                        # Calculate area
                        if coordinates:
                            area, _ = self._calculate_polygon_metrics(coordinates)
                            sector.area_km2 = area

                        sectors.append(sector)

                except Exception as e:
                    logger.warning(f"Error processing sector placemark: {e}")
                    continue

            return sectors

        except Exception as e:
            logger.error(f"Error processing Sectors KML: {e}")
            return []

    async def process_entrances_kml(self, file_path: Path) -> list[EntranceData]:
        """Process Entrances KML file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Define namespace
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}

            entrances = []

            # Find all Placemark elements
            placemarks = root.findall('.//kml:Placemark', ns)

            for placemark in placemarks:
                try:
                    # Extract ExtendedData
                    extended_data = placemark.find('.//kml:ExtendedData', ns)
                    if extended_data is None:
                        continue

                    # Extract data fields
                    data = {}
                    for simple_data in extended_data.findall('.//kml:SimpleData', ns):
                        name = simple_data.get('name')
                        value = simple_data.text
                        if name and value:
                            data[name] = value

                    # Extract coordinates
                    coordinates = self._extract_coordinates(placemark, ns)

                    if coordinates and 'ENTERANCEID' in data:
                        # For entrances, we expect a single point
                        if len(coordinates) == 1:
                            entrance = EntranceData(
                                entrance_id=int(data['ENTERANCEID']),
                                community_name=data.get('COMM_NAM_1', ''),
                                coordinates=coordinates[0],
                                gzd=data.get('GZD', ''),
                                entrance_type=data.get('ENTRANCE_TYPE', None)
                            )
                            entrances.append(entrance)

                except Exception as e:
                    logger.warning(f"Error processing entrance placemark: {e}")
                    continue

            return entrances

        except Exception as e:
            logger.error(f"Error processing Entrances KML: {e}")
            return []

    def _extract_coordinates(self, placemark, ns) -> list[tuple[float, float]]:
        """Extract coordinates from placemark"""
        try:
            # Look for coordinates in different possible locations
            coord_elements = [
                placemark.find('.//kml:coordinates', ns),
                placemark.find('.//kml:LinearRing/kml:coordinates', ns),
                placemark.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
            ]

            for coord_elem in coord_elements:
                if coord_elem is not None and coord_elem.text:
                    # Parse coordinates string
                    coords_text = coord_elem.text.strip()
                    coordinates = []

                    # Split by spaces and process each coordinate pair
                    for coord_pair in coords_text.split():
                        parts = coord_pair.split(',')
                        if len(parts) >= 2:
                            try:
                                lon = float(parts[0])
                                lat = float(parts[1])
                                coordinates.append((lat, lon))  # Store as (lat, lon)
                            except ValueError:
                                continue

                    return coordinates

            return []

        except Exception as e:
            logger.warning(f"Error extracting coordinates: {e}")
            return []

    def _calculate_polygon_metrics(self, coordinates: list[tuple[float, float]]) -> tuple[float, float]:
        """Calculate area and perimeter of polygon"""
        try:
            if len(coordinates) < 3:
                return 0.0, 0.0

            # Calculate perimeter
            perimeter = 0.0
            for i in range(len(coordinates)):
                j = (i + 1) % len(coordinates)
                lat1, lon1 = coordinates[i]
                lat2, lon2 = coordinates[j]

                # Haversine formula for distance
                distance = self._haversine_distance(lat1, lon1, lat2, lon2)
                perimeter += distance

            # Calculate area using shoelace formula
            area = 0.0
            for i in range(len(coordinates)):
                j = (i + 1) % len(coordinates)
                lat1, lon1 = coordinates[i]
                lat2, lon2 = coordinates[j]
                area += (lon1 * lat2 - lon2 * lat1)

            area = abs(area) / 2.0

            # Convert to km² (approximate)
            area_km2 = area * 111.32 * 111.32  # Rough conversion
            perimeter_km = perimeter

            return area_km2, perimeter_km

        except Exception as e:
            logger.warning(f"Error calculating polygon metrics: {e}")
            return 0.0, 0.0

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        try:
            import math

            # Convert to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))

            # Earth radius in kilometers
            r = 6371

            return c * r

        except Exception as e:
            logger.warning(f"Error calculating haversine distance: {e}")
            return 0.0

    async def create_geospatial_mapping(self, kml_results: dict[str, Any]) -> dict[str, Any]:
        """Create comprehensive geospatial mapping"""
        try:
            mapping = {
                'communities': {},
                'sectors': {},
                'entrances': {},
                'relationships': {}
            }

            # Process communities
            if 'communities' in kml_results:
                communities = kml_results['communities']['data']
                for community in communities:
                    mapping['communities'][community.object_id] = {
                        'name_en': community.community_name_en,
                        'name_ar': community.community_name_ar,
                        'label_en': community.label_en,
                        'label_ar': community.label_ar,
                        'area_km2': community.area_km2,
                        'perimeter_km': community.perimeter_km,
                        'coordinates': community.coordinates
                    }

            # Process sectors
            if 'sectors' in kml_results:
                sectors = kml_results['sectors']['data']
                for sector in sectors:
                    mapping['sectors'][sector.object_id] = {
                        'sector_number': sector.sector_number,
                        'perimeter': sector.perimeter,
                        'area_km2': sector.area_km2,
                        'created_user': sector.created_user,
                        'created_date': sector.created_date,
                        'coordinates': sector.coordinates
                    }

            # Process entrances
            if 'entrances' in kml_results:
                entrances = kml_results['entrances']['data']
                for entrance in entrances:
                    mapping['entrances'][entrance.entrance_id] = {
                        'community_name': entrance.community_name,
                        'coordinates': entrance.coordinates,
                        'gzd': entrance.gzd,
                        'entrance_type': entrance.entrance_type
                    }

            # Create relationships
            mapping['relationships'] = await self._create_relationships(mapping)

            return mapping

        except Exception as e:
            logger.error(f"Error creating geospatial mapping: {e}")
            return {}

    async def _create_relationships(self, mapping: dict[str, Any]) -> dict[str, Any]:
        """Create relationships between different geospatial entities"""
        try:
            relationships = {
                'community_sectors': {},
                'community_entrances': {},
                'sector_entrances': {}
            }

            # Match communities with sectors based on spatial overlap
            communities = mapping.get('communities', {})
            sectors = mapping.get('sectors', {})

            logger.info("🔗 Creating community-sector relationships...")
            for comm_id, comm_data in communities.items():
                comm_coords = comm_data['coordinates']
                if not comm_coords:
                    continue

                # Find sectors that overlap with this community
                overlapping_sectors = []
                for sec_id, sec_data in sectors.items():
                    sec_coords = sec_data['coordinates']
                    if sec_coords and self._polygons_overlap(comm_coords, sec_coords):
                        overlapping_sectors.append(sec_id)

                if overlapping_sectors:
                    relationships['community_sectors'][comm_id] = overlapping_sectors

            # Match communities with entrances (optimized for large datasets)
            entrances = mapping.get('entrances', {})

            logger.info("🚪 Creating community-entrance relationships...")
            logger.info(f"   Processing {len(entrances)} entrances across {len(communities)} communities...")

            # Process in batches to avoid memory issues
            batch_size = 1000
            entrance_items = list(entrances.items())

            for comm_id, comm_data in communities.items():
                comm_coords = comm_data['coordinates']
                if not comm_coords:
                    continue

                # Find entrances within this community
                community_entrances = []

                # Process entrances in batches
                for i in range(0, len(entrance_items), batch_size):
                    batch = entrance_items[i:i + batch_size]

                    for ent_id, ent_data in batch:
                        ent_coords = ent_data['coordinates']
                        if ent_coords and self._point_in_polygon(ent_coords, comm_coords):
                            community_entrances.append(ent_id)

                    # Log progress for large datasets
                    if len(entrances) > 10000 and i % 10000 == 0:
                        logger.info(f"   Processed {i}/{len(entrances)} entrances...")

                if community_entrances:
                    relationships['community_entrances'][comm_id] = community_entrances
                    logger.info(f"   Community {comm_id}: {len(community_entrances)} entrances")

            return relationships

        except Exception as e:
            logger.error(f"Error creating relationships: {e}")
            return {}

    def _polygons_overlap(self, coords1: list[tuple[float, float]], coords2: list[tuple[float, float]]) -> bool:
        """Check if two polygons overlap"""
        try:
            # Simple bounding box check first
            min_lat1, max_lat1 = min(c[0] for c in coords1), max(c[0] for c in coords1)
            min_lon1, max_lon1 = min(c[1] for c in coords1), max(c[1] for c in coords1)

            min_lat2, max_lat2 = min(c[0] for c in coords2), max(c[0] for c in coords2)
            min_lon2, max_lon2 = min(c[1] for c in coords2), max(c[1] for c in coords2)

            # Check if bounding boxes overlap
            if (max_lat1 < min_lat2 or min_lat1 > max_lat2 or
                max_lon1 < min_lon2 or min_lon1 > max_lon2):
                return False

            # For now, return True if bounding boxes overlap
            # In a full implementation, you'd do proper polygon intersection
            return True

        except Exception as e:
            logger.warning(f"Error checking polygon overlap: {e}")
            return False

    def _point_in_polygon(self, point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
        """Check if a point is inside a polygon using ray casting algorithm"""
        try:
            lat, lon = point
            n = len(polygon)
            inside = False

            p1x, p1y = polygon[0]
            for i in range(n + 1):
                p2x, p2y = polygon[i % n]
                if lon > min(p1x, p2x):
                    if lon <= max(p1x, p2x):
                        if lat <= max(p1y, p2y):
                            if p1x != p2x:
                                xinters = (lon - p1x) * (p2y - p1y) / (p2x - p1x) + p1y
                            if p1y == p2y or lat <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y

            return inside

        except Exception as e:
            logger.warning(f"Error checking point in polygon: {e}")
            return False

    async def save_to_database(self, kml_results: dict[str, Any]) -> bool:
        """Save KML data to database"""
        try:
            if not self.database_url:
                logger.warning("No database URL provided, skipping database save")
                return False

            engine = create_engine(self.database_url)

            # Create tables if they don't exist
            await self._create_geospatial_tables(engine)

            # Save communities
            if 'communities' in kml_results:
                await self._save_communities(engine, kml_results['communities']['data'])

            # Save sectors
            if 'sectors' in kml_results:
                await self._save_sectors(engine, kml_results['sectors']['data'])

            # Save entrances
            if 'entrances' in kml_results:
                await self._save_entrances(engine, kml_results['entrances']['data'])

            logger.info("KML data saved to database successfully")
            return True

        except Exception as e:
            logger.error(f"Error saving KML data to database: {e}")
            return False

    async def _create_geospatial_tables(self, engine):
        """Create geospatial tables"""
        try:
            with engine.connect() as conn:
                # Communities table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS communities (
                        id SERIAL PRIMARY KEY,
                        object_id INTEGER UNIQUE,
                        community_name_en VARCHAR(255),
                        community_name_ar VARCHAR(255),
                        label_en VARCHAR(255),
                        label_ar VARCHAR(255),
                        area_km2 DECIMAL(10,2),
                        perimeter_km DECIMAL(10,2),
                        coordinates JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                # Sectors table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sectors (
                        id SERIAL PRIMARY KEY,
                        object_id INTEGER UNIQUE,
                        sector_number INTEGER,
                        perimeter DECIMAL(10,2),
                        area_km2 DECIMAL(10,2),
                        created_user VARCHAR(100),
                        created_date VARCHAR(50),
                        coordinates JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                # Entrances table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS entrances (
                        id SERIAL PRIMARY KEY,
                        entrance_id INTEGER UNIQUE,
                        community_name VARCHAR(255),
                        latitude DECIMAL(10,6),
                        longitude DECIMAL(10,6),
                        gzd VARCHAR(50),
                        entrance_type VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                conn.commit()

        except Exception as e:
            logger.error(f"Error creating geospatial tables: {e}")

    async def _save_communities(self, engine, communities: list[CommunityData]):
        """Save communities to database"""
        try:
            with engine.connect() as conn:
                for community in communities:
                    conn.execute(text("""
                        INSERT INTO communities (object_id, community_name_en, community_name_ar,
                                              label_en, label_ar, area_km2, perimeter_km, coordinates)
                        VALUES (:object_id, :name_en, :name_ar, :label_en, :label_ar,
                                :area_km2, :perimeter_km, :coordinates)
                        ON CONFLICT (object_id) DO UPDATE SET
                            community_name_en = EXCLUDED.community_name_en,
                            community_name_ar = EXCLUDED.community_name_ar,
                            label_en = EXCLUDED.label_en,
                            label_ar = EXCLUDED.label_ar,
                            area_km2 = EXCLUDED.area_km2,
                            perimeter_km = EXCLUDED.perimeter_km,
                            coordinates = EXCLUDED.coordinates
                    """), {
                        'object_id': community.object_id,
                        'name_en': community.community_name_en,
                        'name_ar': community.community_name_ar,
                        'label_en': community.label_en,
                        'label_ar': community.label_ar,
                        'area_km2': community.area_km2,
                        'perimeter_km': community.perimeter_km,
                        'coordinates': json.dumps(community.coordinates)
                    })

                conn.commit()

        except Exception as e:
            logger.error(f"Error saving communities: {e}")

    async def _save_sectors(self, engine, sectors: list[SectorData]):
        """Save sectors to database"""
        try:
            with engine.connect() as conn:
                for sector in sectors:
                    conn.execute(text("""
                        INSERT INTO sectors (object_id, sector_number, perimeter, area_km2,
                                          created_user, created_date, coordinates)
                        VALUES (:object_id, :sector_number, :perimeter, :area_km2,
                                :created_user, :created_date, :coordinates)
                        ON CONFLICT (object_id) DO UPDATE SET
                            sector_number = EXCLUDED.sector_number,
                            perimeter = EXCLUDED.perimeter,
                            area_km2 = EXCLUDED.area_km2,
                            created_user = EXCLUDED.created_user,
                            created_date = EXCLUDED.created_date,
                            coordinates = EXCLUDED.coordinates
                    """), {
                        'object_id': sector.object_id,
                        'sector_number': sector.sector_number,
                        'perimeter': sector.perimeter,
                        'area_km2': sector.area_km2,
                        'created_user': sector.created_user,
                        'created_date': sector.created_date,
                        'coordinates': json.dumps(sector.coordinates)
                    })

                conn.commit()

        except Exception as e:
            logger.error(f"Error saving sectors: {e}")

    async def _save_entrances(self, engine, entrances: list[EntranceData]):
        """Save entrances to database"""
        try:
            with engine.connect() as conn:
                for entrance in entrances:
                    conn.execute(text("""
                        INSERT INTO entrances (entrance_id, community_name, latitude, longitude,
                                            gzd, entrance_type)
                        VALUES (:entrance_id, :community_name, :latitude, :longitude,
                                :gzd, :entrance_type)
                        ON CONFLICT (entrance_id) DO UPDATE SET
                            community_name = EXCLUDED.community_name,
                            latitude = EXCLUDED.latitude,
                            longitude = EXCLUDED.longitude,
                            gzd = EXCLUDED.gzd,
                            entrance_type = EXCLUDED.entrance_type
                    """), {
                        'entrance_id': entrance.entrance_id,
                        'community_name': entrance.community_name,
                        'latitude': entrance.coordinates[0],
                        'longitude': entrance.coordinates[1],
                        'gzd': entrance.gzd,
                        'entrance_type': entrance.entrance_type
                    })

                conn.commit()

        except Exception as e:
            logger.error(f"Error saving entrances: {e}")

    async def generate_geospatial_report(self, kml_results: dict[str, Any]) -> dict[str, Any]:
        """Generate comprehensive geospatial report"""
        try:
            report = {
                'summary': {
                    'total_communities': kml_results.get('communities', {}).get('count', 0),
                    'total_sectors': kml_results.get('sectors', {}).get('count', 0),
                    'total_entrances': kml_results.get('entrances', {}).get('count', 0),
                    'processing_timestamp': datetime.now().isoformat()
                },
                'communities': {},
                'sectors': {},
                'entrances': {},
                'spatial_analysis': {}
            }

            # Analyze communities
            if 'communities' in kml_results:
                communities = kml_results['communities']['data']
                if communities:
                    areas = [c.area_km2 for c in communities if c.area_km2]
                    perimeters = [c.perimeter_km for c in communities if c.perimeter_km]

                    report['communities'] = {
                        'total_count': len(communities),
                        'avg_area_km2': np.mean(areas) if areas else 0,
                        'max_area_km2': max(areas) if areas else 0,
                        'min_area_km2': min(areas) if areas else 0,
                        'avg_perimeter_km': np.mean(perimeters) if perimeters else 0
                    }

            # Analyze sectors
            if 'sectors' in kml_results:
                sectors = kml_results['sectors']['data']
                if sectors:
                    areas = [s.area_km2 for s in sectors if s.area_km2]
                    perimeters = [s.perimeter for s in sectors if s.perimeter]

                    report['sectors'] = {
                        'total_count': len(sectors),
                        'avg_area_km2': np.mean(areas) if areas else 0,
                        'max_area_km2': max(areas) if areas else 0,
                        'min_area_km2': min(areas) if areas else 0,
                        'avg_perimeter': np.mean(perimeters) if perimeters else 0
                    }

            # Analyze entrances
            if 'entrances' in kml_results:
                entrances = kml_results['entrances']['data']
                if entrances:
                    report['entrances'] = {
                        'total_count': len(entrances),
                        'unique_communities': len({e.community_name for e in entrances if e.community_name})
                    }

            # Spatial analysis
            if 'mapping' in kml_results:
                mapping = kml_results['mapping']
                relationships = mapping.get('relationships', {})

                report['spatial_analysis'] = {
                    'communities_with_sectors': len(relationships.get('community_sectors', {})),
                    'communities_with_entrances': len(relationships.get('community_entrances', {})),
                    'total_relationships': sum(len(rel) for rel in relationships.values())
                }

            return report

        except Exception as e:
            logger.error(f"Error generating geospatial report: {e}")
            return {'error': str(e)}

# Global instance
_kml_processor = None

async def get_kml_processor(database_url: str = None) -> KMLGeospatialProcessor:
    """Get global KML processor instance"""
    global _kml_processor
    if _kml_processor is None:
        if database_url is None:
            import os
            database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/propcalc')
        _kml_processor = KMLGeospatialProcessor(database_url)
    return _kml_processor
