#!/usr/bin/env python3
"""
Unified Data Quality Module for PropCalc
Consolidates all data quality functionality into a single, well-designed module
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class QualityIssueType(Enum):
    """Types of data quality issues"""
    HIGH_NULL_RATIO = "high_null_ratio"
    MIXED_DATA_TYPES = "mixed_data_types"
    DUPLICATE_RECORDS = "duplicate_records"
    INVALID_FORMATS = "invalid_formats"
    OUTLIERS = "outliers"

class DataQualityLevel(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"            # 75-89%
    FAIR = "fair"            # 60-74%
    POOR = "poor"            # <60%

@dataclass
class QualityIssue:
    """Data quality issue details"""
    source: str
    issue_type: QualityIssueType
    severity: str
    description: str
    affected_columns: List[str]
    impact_score: float
    recommended_action: str

@dataclass
class DataQualityReport:
    """Comprehensive data quality report"""
    source: str
    total_records: int
    valid_records: int
    quality_score: float
    quality_level: DataQualityLevel
    processing_time_seconds: float
    timestamp: datetime
    errors: List[str]
    warnings: List[str]
    issues: List[QualityIssue]

@dataclass
class ImprovementResult:
    """Result of data quality improvement"""
    source: str
    original_records: int
    cleaned_records: int
    removed_records: int
    quality_score_before: float
    quality_score_after: float
    improvements_applied: List[str]
    processing_time_seconds: float

class DataQualityManager:
    """
    Unified data quality manager that handles all data quality operations
    
    This class consolidates functionality from multiple duplicate classes and provides
    a single, consistent interface for data quality management.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(".")
        self.improvement_results: Dict[str, ImprovementResult] = {}
        
        # Priority sources for improvement (focus on largest files first)
        self.priority_sources = [
            'rent_contracts',      # 4GB file
            'units',               # 784MB file
            'buildings',           # 84MB file
            'map_requests',        # 199MB file
            'real_estate_permits', # 39MB file
            'valuation',           # 19MB file
            'projects',            # 2MB file
            'brokers',             # 1.4MB file
            'offices',             # 1.4MB file
            'real_estate_licenses', # 1.2MB file
            'developers',          # 0.5MB file
            'accredited_escrow_agents',  # 2KB file
            'free_zone_companies', # 69KB file
            'licensed_owner_associations',  # 21KB file
            'valuator_licensing'   # 34KB file
        ]

    async def improve_all_sources(self) -> Dict[str, ImprovementResult]:
        """Improve data quality for all sources"""
        logger.info("🔧 Starting Unified Data Quality Improvement Process")
        logger.info("=" * 60)

        results = {}

        for source_name in self.priority_sources:
            file_path = self.data_dir / f"{source_name.replace('_', '_').title()}.csv"

            if not file_path.exists():
                logger.warning(f"⚠️ File not found: {file_path}")
                continue

            logger.info(f"🔧 Improving {source_name}...")
            try:
                result = await self.improve_source(source_name, file_path)
                results[source_name] = result
                logger.info(f"✅ {source_name}: {result.quality_score_after:.1%} quality score")
            except Exception as e:
                logger.error(f"❌ Error improving {source_name}: {e}")

        self.improvement_results = results
        return results

    async def improve_source(self, source_name: str, file_path: Path) -> ImprovementResult:
        """Improve data quality for a specific source"""
        start_time = datetime.now()

        # Read data with optimized settings for large files
        logger.info(f"   📖 Reading {file_path.name}...")

        # Use chunking for very large files
        if file_path.stat().st_size > 100 * 1024 * 1024:  # > 100MB
            logger.info("   📊 Large file detected, using chunked processing...")
            df = await self._read_large_file_chunked(file_path)
        else:
            df = pd.read_csv(file_path, low_memory=False)

        original_records = len(df)
        logger.info(f"   📊 Loaded {original_records:,} records")

        # Calculate original quality score
        original_quality = self._calculate_quality_score(df)
        logger.info(f"   📈 Original quality: {original_quality:.1%}")

        # Apply improvements
        improvements = []

        # 1. Handle null values
        null_improvements = self._handle_null_values(df, source_name)
        improvements.extend(null_improvements)

        # 2. Normalize data types
        type_improvements = self._normalize_data_types(df, source_name)
        improvements.extend(type_improvements)

        # 3. Remove duplicates
        duplicate_improvements = self._remove_duplicates(df, source_name)
        improvements.extend(duplicate_improvements)

        # 4. Validate formats
        format_improvements = self._validate_formats(df, source_name)
        improvements.extend(format_improvements)

        # Calculate final quality score
        final_quality = self._calculate_quality_score(df)
        cleaned_records = len(df)
        removed_records = original_records - cleaned_records

        # Save improved data
        output_path = file_path.parent / f"{file_path.stem}_improved.csv"
        df.to_csv(output_path, index=False)

        processing_time = (datetime.now() - start_time).total_seconds()

        result = ImprovementResult(
            source=source_name,
            original_records=original_records,
            cleaned_records=cleaned_records,
            removed_records=removed_records,
            quality_score_before=original_quality,
            quality_score_after=final_quality,
            improvements_applied=improvements,
            processing_time_seconds=processing_time
        )

        logger.info(f"   📊 Quality: {original_quality:.1%} → {final_quality:.1%}")
        logger.info(f"   🗑️ Removed: {removed_records:,} records")
        logger.info(f"   ⚡ Applied: {len(improvements)} improvements")

        return result

    async def _read_large_file_chunked(self, file_path: Path) -> pd.DataFrame:
        """Read large files in chunks to avoid memory issues"""
        chunk_size = 100000  # 100K rows per chunk
        chunks = []
        
        for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
            chunks.append(chunk)
            
        return pd.concat(chunks, ignore_index=True)

    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate comprehensive data quality score"""
        if len(df) == 0:
            return 0.0

        # Calculate completeness (non-null ratio)
        non_null_ratio = df.notna().sum().sum() / (len(df) * len(df.columns))

        # Calculate consistency (no duplicates)
        duplicate_ratio = 1 - (df.duplicated().sum() / len(df))

        # Calculate validity (format checks)
        validity_score = self._calculate_validity_score(df)

        # Combined score with weights
        quality_score = (non_null_ratio * 0.5 + duplicate_ratio * 0.3 + validity_score * 0.2)

        return quality_score

    def _calculate_validity_score(self, df: pd.DataFrame) -> float:
        """Calculate data validity score - optimized for large datasets"""
        if len(df) == 0:
            return 0.0

        total_records = len(df)
        chunk_size = 10000
        total_chunks = (total_records + chunk_size - 1) // chunk_size if total_records > chunk_size else 1

        logger.info(f"   📊 Processing {total_records:,} rows in {total_chunks} chunks...")

        valid_records = 0

        for chunk_idx in range(total_chunks):
            start_idx = chunk_idx * chunk_size
            end_idx = min(start_idx + chunk_size, total_records)

            # Get chunk
            chunk = df.iloc[start_idx:end_idx]

            # Vectorized operations for better performance
            chunk_valid = pd.Series([True] * len(chunk), index=chunk.index)

            for col in chunk.columns:
                # Skip if column is already marked as invalid
                if not chunk_valid.any():
                    break

                # Check for null values
                null_mask = chunk[col].isna() | (chunk[col] == '')
                chunk_valid &= ~null_mask

                # Check for obvious invalid string values
                if pd.api.types.is_string_dtype(df[col]):
                    invalid_strings = chunk[col].astype(str).str.lower().isin(['null', 'none', 'nan', 'undefined'])
                    empty_strings = chunk[col].astype(str).str.strip() == ''
                    chunk_valid &= ~(invalid_strings | empty_strings)

                # Check numeric columns for negative values (except price/amount/value columns)
                elif pd.api.types.is_numeric_dtype(df[col]):
                    if col.lower() not in ['price', 'amount', 'value']:
                        negative_mask = chunk[col] < 0
                        chunk_valid &= ~negative_mask

            # Count valid rows in this chunk
            valid_records += chunk_valid.sum()

        validity_score = valid_records / total_records if total_records > 0 else 0.0
        return validity_score

    def _handle_null_values(self, df: pd.DataFrame, source_name: str) -> List[str]:
        """Handle null values intelligently based on source type"""
        improvements = []
        original_count = len(df)

        # Source-specific null handling strategies
        if source_name in ['rent_contracts', 'units', 'buildings']:
            # For property data, remove rows with critical missing information
            critical_columns = [col for col in df.columns if any(keyword in col.lower() 
                                                              for keyword in ['id', 'name', 'type', 'location'])]
            
            if critical_columns:
                df.dropna(subset=critical_columns, inplace=True)
                improvements.append("removed_rows_with_critical_missing_data")

        elif source_name in ['developers', 'brokers', 'offices']:
            # For entity data, fill missing names with placeholders
            name_columns = [col for col in df.columns if 'name' in col.lower()]
            for col in name_columns:
                df[col].fillna(f"Unknown_{col}", inplace=True)
            improvements.append("filled_missing_names_with_placeholders")

        # General null handling
        null_counts = df.isnull().sum()
        high_null_columns = null_counts[null_counts > len(df) * 0.5].index.tolist()
        
        if high_null_columns:
            df.drop(columns=high_null_columns, inplace=True)
            improvements.append(f"removed_high_null_columns: {', '.join(high_null_columns)}")

        removed_count = original_count - len(df)
        if removed_count > 0:
            improvements.append(f"removed_{removed_count}_null_rows")

        return improvements

    def _normalize_data_types(self, df: pd.DataFrame, source_name: str) -> List[str]:
        """Normalize data types for consistency"""
        improvements = []

        for col in df.columns:
            col_lower = col.lower()
            
            # Date columns
            if any(keyword in col_lower for keyword in ['date', 'created', 'updated', 'timestamp']):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    improvements.append(f"normalized_date_column: {col}")
                except Exception:
                    pass

            # Numeric columns
            elif any(keyword in col_lower for keyword in ['price', 'amount', 'value', 'area', 'size', 'count']):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    improvements.append(f"normalized_numeric_column: {col}")
                except Exception:
                    pass

            # Boolean columns
            elif any(keyword in col_lower for keyword in ['is_', 'has_', 'active', 'enabled']):
                try:
                    df[col] = df[col].astype(str).str.lower().isin(['true', '1', 'yes', 'active', 'enabled'])
                    improvements.append(f"normalized_boolean_column: {col}")
                except Exception:
                    pass

        return improvements

    def _remove_duplicates(self, df: pd.DataFrame, source_name: str) -> List[str]:
        """Remove duplicate records efficiently"""
        improvements = []
        original_count = len(df)

        # Remove exact duplicates
        df.drop_duplicates(inplace=True)

        # Remove duplicates based on key columns (if they exist)
        key_columns = [col for col in df.columns if 'id' in col.lower() or 'key' in col.lower()]
        if key_columns:
            df.drop_duplicates(subset=key_columns, inplace=True)
            improvements.append("removed_duplicates_by_key_columns")

        removed_count = original_count - len(df)
        if removed_count > 0:
            improvements.append(f"removed_{removed_count}_duplicates")
            logger.info(f"     🗑️ Removed {removed_count:,} duplicate records")

        return improvements

    def _validate_formats(self, df: pd.DataFrame, source_name: str) -> List[str]:
        """Validate data formats and apply corrections"""
        improvements = []

        for col in df.columns:
            col_lower = col.lower()
            
            # Email validation
            if 'email' in col_lower:
                email_mask = df[col].astype(str).str.contains(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', na=False)
                invalid_emails = (~email_mask).sum()
                if invalid_emails > 0:
                    df.loc[~email_mask, col] = None
                    improvements.append(f"cleaned_invalid_emails: {invalid_emails}")

            # Phone number validation
            elif 'phone' in col_lower or 'mobile' in col_lower:
                phone_mask = df[col].astype(str).str.contains(r'^[\d\s\-\+\(\)]+$', na=False)
                invalid_phones = (~phone_mask).sum()
                if invalid_phones > 0:
                    df.loc[~phone_mask, col] = None
                    improvements.append(f"cleaned_invalid_phones: {invalid_phones}")

            # URL validation
            elif 'url' in col_lower or 'website' in col_lower:
                url_mask = df[col].astype(str).str.contains(r'^https?://', na=False)
                invalid_urls = (~url_mask).sum()
                if invalid_urls > 0:
                    df.loc[~url_mask, col] = None
                    improvements.append(f"cleaned_invalid_urls: {invalid_urls}")

        return improvements

    async def generate_improvement_report(self) -> Dict[str, Any]:
        """Generate comprehensive improvement report"""
        if not self.improvement_results:
            return {"message": "No improvement results available"}

        total_sources = len(self.improvement_results)
        total_original = sum(r.original_records for r in self.improvement_results.values())
        total_cleaned = sum(r.cleaned_records for r in self.improvement_results.values())
        total_removed = sum(r.removed_records for r in self.improvement_results.values())
        
        avg_quality_before = np.mean([r.quality_score_before for r in self.improvement_results.values()])
        avg_quality_after = np.mean([r.quality_score_after for r in self.improvement_results.values()])
        
        total_processing_time = sum(r.processing_time_seconds for r in self.improvement_results.values())

        # Categorize improvements
        improvement_categories = self._categorize_improvements()

        # Generate recommendations
        recommendations = self._generate_recommendations()

        report = {
            "summary": {
                "total_sources_processed": total_sources,
                "total_original_records": total_original,
                "total_cleaned_records": total_cleaned,
                "total_removed_records": total_removed,
                "average_quality_before": f"{avg_quality_before:.1%}",
                "average_quality_after": f"{avg_quality_after:.1%}",
                "total_processing_time_seconds": total_processing_time,
                "overall_improvement": f"{((avg_quality_after - avg_quality_before) / avg_quality_before * 100):.1f}%"
            },
            "improvement_categories": improvement_categories,
            "recommendations": recommendations,
            "detailed_results": {
                source: {
                    "original_records": result.original_records,
                    "cleaned_records": result.cleaned_records,
                    "removed_records": result.removed_records,
                    "quality_before": f"{result.quality_score_before:.1%}",
                    "quality_after": f"{result.quality_score_after:.1%}",
                    "improvements_applied": result.improvements_applied,
                    "processing_time": result.processing_time_seconds
                }
                for source, result in self.improvement_results.items()
            }
        }

        return report

    def _categorize_improvements(self) -> Dict[str, int]:
        """Categorize improvements by type"""
        categories = {}
        
        for result in self.improvement_results.values():
            for improvement in result.improvements_applied:
                category = improvement.split(':')[0] if ':' in improvement else improvement
                categories[category] = categories.get(category, 0) + 1
                
        return categories

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on results"""
        recommendations = []
        
        # Analyze quality scores
        low_quality_sources = [
            source for source, result in self.improvement_results.items()
            if result.quality_score_after < 0.7
        ]
        
        if low_quality_sources:
            recommendations.append({
                "priority": "high",
                "action": "investigate_data_sources",
                "description": f"Sources with low quality scores: {', '.join(low_quality_sources)}",
                "recommendation": "Review data collection processes and source reliability"
            })

        # Analyze processing times
        slow_sources = [
            source for source, result in self.improvement_results.items()
            if result.processing_time_seconds > 60
        ]
        
        if slow_sources:
            recommendations.append({
                "priority": "medium",
                "action": "optimize_processing",
                "description": f"Slow processing sources: {', '.join(slow_sources)}",
                "recommendation": "Consider implementing parallel processing or chunking"
            })

        # Analyze data loss
        high_loss_sources = [
            source for source, result in self.improvement_results.items()
            if result.removed_records / result.original_records > 0.1
        ]
        
        if high_loss_sources:
            recommendations.append({
                "priority": "high",
                "action": "review_cleaning_rules",
                "description": f"High data loss sources: {', '.join(high_loss_sources)}",
                "recommendation": "Review and potentially relax data cleaning rules"
            })

        return recommendations

# Factory function for backward compatibility
async def get_data_quality_manager(data_dir: Optional[Path] = None) -> DataQualityManager:
    """Get a data quality manager instance"""
    return DataQualityManager(data_dir)

# Legacy aliases for backward compatibility
DataQualityImprover = DataQualityManager
OptimizedDataQualityImprover = DataQualityManager
