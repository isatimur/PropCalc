"""
PropCalc Address Normalization Lookup Tables
Comprehensive mapping from DLD raw data to user-friendly locations
"""

from dataclasses import dataclass
from enum import Enum


class NormalizationType(Enum):
    """Types of normalization"""
    AREA_MAPPING = "area_mapping"
    PROPERTY_TYPE_MAPPING = "property_type_mapping"
    DEVELOPER_MAPPING = "developer_mapping"
    PROJECT_MAPPING = "project_mapping"

@dataclass
class NormalizationEntry:
    """Single normalization entry"""
    dld_value: str
    normalized_value: str
    category: str
    confidence: float
    notes: str | None = None

class AddressNormalizationLookup:
    """
    Comprehensive address normalization lookup tables for PropCalc
    Maps DLD raw data to user-friendly, standardized locations
    """

    def __init__(self):
        self.area_mapping = self._initialize_area_mapping()
        self.property_type_mapping = self._initialize_property_type_mapping()
        self.developer_mapping = self._initialize_developer_mapping()
        self.project_mapping = self._initialize_project_mapping()

    def _initialize_area_mapping(self) -> dict[str, NormalizationEntry]:
        """
        Initialize area name mapping from DLD to user-friendly names
        Maps technical DLD area names to recognizable location names
        """
        return {
            # Dubai Marina Area
            "Marsa Dubai": NormalizationEntry(
                dld_value="Marsa Dubai",
                normalized_value="Dubai Marina",
                category="Premium Waterfront",
                confidence=0.95,
                notes="Main Dubai Marina area"
            ),

            # Downtown Dubai Area
            "Burj Khalifa": NormalizationEntry(
                dld_value="Burj Khalifa",
                normalized_value="Downtown Dubai",
                category="Premium Downtown",
                confidence=0.98,
                notes="Downtown Dubai including Burj Khalifa area"
            ),

            # Palm Jumeirah
            "Palm Jumeirah": NormalizationEntry(
                dld_value="Palm Jumeirah",
                normalized_value="Palm Jumeirah",
                category="Premium Waterfront",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            # Business Bay
            "Business Bay": NormalizationEntry(
                dld_value="Business Bay",
                normalized_value="Business Bay",
                category="Business District",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            # Dubai Hills Estate
            "Hadaeq Sheikh Mohammed Bin Rashid": NormalizationEntry(
                dld_value="Hadaeq Sheikh Mohammed Bin Rashid",
                normalized_value="Dubai Hills Estate",
                category="Residential Community",
                confidence=0.90,
                notes="Dubai Hills Estate area"
            ),

            # Al Barsha Areas
            "Al Barsha South Fourth": NormalizationEntry(
                dld_value="Al Barsha South Fourth",
                normalized_value="Al Barsha",
                category="Residential",
                confidence=0.85,
                notes="Al Barsha residential area"
            ),

            # Al Thanyah Areas
            "Al Thanyah Fifth": NormalizationEntry(
                dld_value="Al Thanyah Fifth",
                normalized_value="Al Thanyah",
                category="Residential",
                confidence=0.85,
                notes="Al Thanyah residential area"
            ),

            # Al Warsan
            "Al Warsan First": NormalizationEntry(
                dld_value="Al Warsan First",
                normalized_value="Al Warsan",
                category="Residential",
                confidence=0.85,
                notes="Al Warsan residential area"
            ),

            # Wadi Al Safa
            "Wadi Al Safa 5": NormalizationEntry(
                dld_value="Wadi Al Safa 5",
                normalized_value="Wadi Al Safa",
                category="Residential",
                confidence=0.85,
                notes="Wadi Al Safa residential area"
            ),

            # Al Hebiah
            "Al Hebiah Fourth": NormalizationEntry(
                dld_value="Al Hebiah Fourth",
                normalized_value="Al Hebiah",
                category="Residential",
                confidence=0.85,
                notes="Al Hebiah residential area"
            ),

            # Jabal Ali
            "Jabal Ali First": NormalizationEntry(
                dld_value="Jabal Ali First",
                normalized_value="Jabal Ali",
                category="Industrial/Residential",
                confidence=0.85,
                notes="Jabal Ali area"
            ),

            # Al Merkadh
            "Al Merkadh": NormalizationEntry(
                dld_value="Al Merkadh",
                normalized_value="Al Merkadh",
                category="Residential",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            # Me'Aisem
            "Me'Aisem First": NormalizationEntry(
                dld_value="Me'Aisem First",
                normalized_value="Me'Aisem",
                category="Residential",
                confidence=0.85,
                notes="Me'Aisem residential area"
            ),

            # Al Thanayah
            "Al Thanayah Fourth": NormalizationEntry(
                dld_value="Al Thanayah Fourth",
                normalized_value="Al Thanayah",
                category="Residential",
                confidence=0.85,
                notes="Al Thanayah residential area"
            ),

            # Al Thanyah Third
            "Al Thanyah Third": NormalizationEntry(
                dld_value="Al Thanyah Third",
                normalized_value="Al Thanyah",
                category="Residential",
                confidence=0.85,
                notes="Al Thanyah residential area"
            ),

            # Default fallback
            "Unknown": NormalizationEntry(
                dld_value="Unknown",
                normalized_value="Dubai",
                category="General",
                confidence=0.50,
                notes="Default fallback for unknown areas"
            )
        }

    def _initialize_property_type_mapping(self) -> dict[str, NormalizationEntry]:
        """
        Initialize property type mapping from DLD to standardized types
        Maps DLD property types to user-friendly categories
        """
        return {
            # Residential Types
            "Unit": NormalizationEntry(
                dld_value="Unit",
                normalized_value="Apartment",
                category="Residential",
                confidence=0.95,
                notes="Standard apartment unit"
            ),

            "Apartment": NormalizationEntry(
                dld_value="Apartment",
                normalized_value="Apartment",
                category="Residential",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            "Villa": NormalizationEntry(
                dld_value="Villa",
                normalized_value="Villa",
                category="Residential",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            "Townhouse": NormalizationEntry(
                dld_value="Townhouse",
                normalized_value="Townhouse",
                category="Residential",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            "Penthouse": NormalizationEntry(
                dld_value="Penthouse",
                normalized_value="Penthouse",
                category="Residential",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            # Land Types
            "Land": NormalizationEntry(
                dld_value="Land",
                normalized_value="Villa",
                category="Residential",
                confidence=0.80,
                notes="Land typically used for villa development"
            ),

            # Commercial Types
            "Building": NormalizationEntry(
                dld_value="Building",
                normalized_value="Office",
                category="Commercial",
                confidence=0.85,
                notes="Commercial building mapped to office"
            ),

            "Office": NormalizationEntry(
                dld_value="Office",
                normalized_value="Office",
                category="Commercial",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            "Retail": NormalizationEntry(
                dld_value="Retail",
                normalized_value="Retail",
                category="Commercial",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            "Warehouse": NormalizationEntry(
                dld_value="Warehouse",
                normalized_value="Warehouse",
                category="Industrial",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            # Default fallback
            "Unknown": NormalizationEntry(
                dld_value="Unknown",
                normalized_value="Apartment",
                category="Residential",
                confidence=0.50,
                notes="Default fallback for unknown property types"
            )
        }

    def _initialize_developer_mapping(self) -> dict[str, NormalizationEntry]:
        """
        Initialize developer name mapping for consistency
        Maps various developer name formats to standardized names
        """
        return {
            # Major Developers
            "Emaar Properties": NormalizationEntry(
                dld_value="Emaar Properties",
                normalized_value="Emaar Properties",
                category="Major Developer",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            "Emaar": NormalizationEntry(
                dld_value="Emaar",
                normalized_value="Emaar Properties",
                category="Major Developer",
                confidence=0.95,
                notes="Shortened name mapped to full name"
            ),

            "Nakheel": NormalizationEntry(
                dld_value="Nakheel",
                normalized_value="Nakheel",
                category="Major Developer",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            "Dubai Properties": NormalizationEntry(
                dld_value="Dubai Properties",
                normalized_value="Dubai Properties",
                category="Major Developer",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            "Meraas": NormalizationEntry(
                dld_value="Meraas",
                normalized_value="Meraas",
                category="Major Developer",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            "DAMAC": NormalizationEntry(
                dld_value="DAMAC",
                normalized_value="DAMAC Properties",
                category="Major Developer",
                confidence=0.95,
                notes="Shortened name mapped to full name"
            ),

            "DAMAC Properties": NormalizationEntry(
                dld_value="DAMAC Properties",
                normalized_value="DAMAC Properties",
                category="Major Developer",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            # Default fallback
            "Unknown": NormalizationEntry(
                dld_value="Unknown",
                normalized_value="Private Developer",
                category="Other",
                confidence=0.50,
                notes="Default fallback for unknown developers"
            )
        }

    def _initialize_project_mapping(self) -> dict[str, NormalizationEntry]:
        """
        Initialize project name mapping for consistency
        Maps various project name formats to standardized names
        """
        return {
            # Marina Projects
            "Marina Heights": NormalizationEntry(
                dld_value="Marina Heights",
                normalized_value="Marina Heights",
                category="Marina Project",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            "Marina Gate": NormalizationEntry(
                dld_value="Marina Gate",
                normalized_value="Marina Gate",
                category="Marina Project",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            # Palm Projects
            "Palm Vista Villa": NormalizationEntry(
                dld_value="Palm Vista Villa",
                normalized_value="Palm Vista Villa",
                category="Palm Project",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            # Downtown Projects
            "Downtown Tower": NormalizationEntry(
                dld_value="Downtown Tower",
                normalized_value="Downtown Tower",
                category="Downtown Project",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            # Business Bay Projects
            "Business Bay Office": NormalizationEntry(
                dld_value="Business Bay Office",
                normalized_value="Business Bay Office",
                category="Business Bay Project",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            # Hills Projects
            "Hills Estate Villa": NormalizationEntry(
                dld_value="Hills Estate Villa",
                normalized_value="Hills Estate Villa",
                category="Hills Project",
                confidence=1.0,
                notes="Direct mapping - no change needed"
            ),

            # Default fallback
            "Unknown": NormalizationEntry(
                dld_value="Unknown",
                normalized_value="Private Project",
                category="Other",
                confidence=0.50,
                notes="Default fallback for unknown projects"
            )
        }

    def normalize_area(self, dld_area_name: str) -> str:
        """
        Normalize DLD area name to user-friendly location name

        Args:
            dld_area_name: Raw area name from DLD data

        Returns:
            Normalized area name for UI display
        """
        if not dld_area_name:
            return "Dubai"

        # Clean the input
        cleaned_name = dld_area_name.strip()

        # Look up in mapping
        if cleaned_name in self.area_mapping:
            return self.area_mapping[cleaned_name].normalized_value

        # Try partial matching for similar names
        for dld_name, entry in self.area_mapping.items():
            if dld_name.lower() in cleaned_name.lower() or cleaned_name.lower() in dld_name.lower():
                return entry.normalized_value

        # Return original if no match found
        return cleaned_name

    def normalize_property_type(self, dld_property_type: str) -> str:
        """
        Normalize DLD property type to standardized type

        Args:
            dld_property_type: Raw property type from DLD data

        Returns:
            Normalized property type for UI display
        """
        if not dld_property_type:
            return "Apartment"

        # Clean the input
        cleaned_type = dld_property_type.strip()

        # Look up in mapping
        if cleaned_type in self.property_type_mapping:
            return self.property_type_mapping[cleaned_type].normalized_value

        # Try partial matching
        for dld_type, entry in self.property_type_mapping.items():
            if dld_type.lower() in cleaned_type.lower() or cleaned_type.lower() in dld_type.lower():
                return entry.normalized_value

        # Return default
        return "Apartment"

    def normalize_developer(self, dld_developer_name: str) -> str:
        """
        Normalize DLD developer name to standardized name

        Args:
            dld_developer_name: Raw developer name from DLD data

        Returns:
            Normalized developer name for UI display
        """
        if not dld_developer_name:
            return "Private Developer"

        # Clean the input
        cleaned_name = dld_developer_name.strip()

        # Look up in mapping
        if cleaned_name in self.developer_mapping:
            return self.developer_mapping[cleaned_name].normalized_value

        # Try partial matching
        for dld_name, entry in self.developer_mapping.items():
            if dld_name.lower() in cleaned_name.lower() or cleaned_name.lower() in dld_name.lower():
                return entry.normalized_value

        # Return original if no match found
        return cleaned_name

    def normalize_project(self, dld_project_name: str) -> str:
        """
        Normalize DLD project name to standardized name

        Args:
            dld_project_name: Raw project name from DLD data

        Returns:
            Normalized project name for UI display
        """
        if not dld_project_name:
            return "Private Project"

        # Clean the input
        cleaned_name = dld_project_name.strip()

        # Look up in mapping
        if cleaned_name in self.project_mapping:
            return self.project_mapping[cleaned_name].normalized_value

        # Try partial matching
        for dld_name, entry in self.project_mapping.items():
            if dld_name.lower() in cleaned_name.lower() or cleaned_name.lower() in dld_name.lower():
                return entry.normalized_value

        # Return original if no match found
        return cleaned_name

    def get_normalization_stats(self) -> dict[str, dict]:
        """
        Get statistics about normalization mappings

        Returns:
            Dictionary with normalization statistics
        """
        return {
            "area_mapping": {
                "total_entries": len(self.area_mapping),
                "categories": list({entry.category for entry in self.area_mapping.values()}),
                "average_confidence": sum(entry.confidence for entry in self.area_mapping.values()) / len(self.area_mapping)
            },
            "property_type_mapping": {
                "total_entries": len(self.property_type_mapping),
                "categories": list({entry.category for entry in self.property_type_mapping.values()}),
                "average_confidence": sum(entry.confidence for entry in self.property_type_mapping.values()) / len(self.property_type_mapping)
            },
            "developer_mapping": {
                "total_entries": len(self.developer_mapping),
                "categories": list({entry.category for entry in self.developer_mapping.values()}),
                "average_confidence": sum(entry.confidence for entry in self.developer_mapping.values()) / len(self.developer_mapping)
            },
            "project_mapping": {
                "total_entries": len(self.project_mapping),
                "categories": list({entry.category for entry in self.project_mapping.values()}),
                "average_confidence": sum(entry.confidence for entry in self.project_mapping.values()) / len(self.project_mapping)
            }
        }

    def export_mapping_to_json(self) -> dict[str, dict]:
        """
        Export all mappings to JSON format for documentation

        Returns:
            Dictionary with all mappings in JSON format
        """
        return {
            "area_mapping": {
                dld_name: {
                    "normalized_value": entry.normalized_value,
                    "category": entry.category,
                    "confidence": entry.confidence,
                    "notes": entry.notes
                }
                for dld_name, entry in self.area_mapping.items()
            },
            "property_type_mapping": {
                dld_type: {
                    "normalized_value": entry.normalized_value,
                    "category": entry.category,
                    "confidence": entry.confidence,
                    "notes": entry.notes
                }
                for dld_type, entry in self.property_type_mapping.items()
            },
            "developer_mapping": {
                dld_name: {
                    "normalized_value": entry.normalized_value,
                    "category": entry.category,
                    "confidence": entry.confidence,
                    "notes": entry.notes
                }
                for dld_name, entry in self.developer_mapping.items()
            },
            "project_mapping": {
                dld_name: {
                    "normalized_value": entry.normalized_value,
                    "category": entry.category,
                    "confidence": entry.confidence,
                    "notes": entry.notes
                }
                for dld_name, entry in self.project_mapping.items()
            }
        }

# Global instance for use throughout the application
normalization_lookup = AddressNormalizationLookup()
