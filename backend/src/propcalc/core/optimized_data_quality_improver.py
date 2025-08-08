#!/usr/bin/env python3
"""
Optimized Data Quality Improver for Large Files
Handles large CSV files efficiently without row-by-row iteration
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualityIssueType(Enum):
    """Types of data quality issues"""
    HIGH_NULL_RATIO = "high_null_ratio"
    MIXED_DATA_TYPES = "mixed_data_types"
    DUPLICATE_RECORDS = "duplicate_records"
    INVALID_FORMATS = "invalid_formats"
    OUTLIERS = "outliers"

class ImprovementStrategy(Enum):
    """Data improvement strategies"""
    CLEAN_NULLS = "clean_nulls"
    NORMALIZE_TYPES = "normalize_types"
    REMOVE_DUPLICATES = "remove_duplicates"
    VALIDATE_FORMATS = "validate_formats"
    HANDLE_OUTLIERS = "handle_outliers"

@dataclass
class QualityIssue:
    """Data quality issue details"""
    source: str
    issue_type: QualityIssueType
    severity: str
    description: str
    affected_columns: list[str]
    impact_score: float
    recommended_action: str

@dataclass
class ImprovementResult:
    """Result of data quality improvement"""
    source: str
    original_records: int
    cleaned_records: int
    removed_records: int
    quality_score_before: float
    quality_score_after: float
    improvements_applied: list[str]
    processing_time_seconds: float

class OptimizedDataQualityImprover:
    """Optimized data quality improver for large files"""

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("..")
        self.improvement_results = {}

        # Priority sources for improvement (focus on largest files first)
        self.priority_sources = [
            'rent_contracts',  # 4GB file
            'units',           # 784MB file
            'buildings',       # 84MB file
            'map_requests',    # 199MB file
            'real_estate_permits',  # 39MB file
            'valuation',       # 19MB file
            'projects',        # 2MB file
            'brokers',         # 1.4MB file
            'offices',         # 1.4MB file
            'real_estate_licenses',  # 1.2MB file
            'developers',      # 0.5MB file
            'accredited_escrow_agents',  # 2KB file
            'free_zone_companies',  # 69KB file
            'licensed_owner_associations',  # 21KB file
            'valuator_licensing'  # 34KB file
        ]

    async def improve_all_sources(self) -> dict[str, ImprovementResult]:
        """Improve data quality for all sources - OPTIMIZED for large files"""
        logger.info("🔧 Starting Optimized Data Quality Improvement")
        logger.info("=" * 60)

        results = {}

        for source_name in self.priority_sources:
            file_path = self.data_dir / f"{source_name.replace('_', '_').title()}.csv"

            if not file_path.exists():
                logger.warning(f"⚠️ File not found: {file_path}")
                continue

            logger.info(f"\n🔧 Improving {source_name}...")
            try:
                result = await self.improve_source_optimized(source_name, file_path)
                results[source_name] = result
                logger.info(f"✅ {source_name}: {result.quality_score_after:.1%} quality score")
            except Exception as e:
                logger.error(f"❌ Error improving {source_name}: {e}")

        return results

    async def improve_source_optimized(self, source_name: str, file_path: Path) -> ImprovementResult:
        """Optimized source improvement - handles large files efficiently"""
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

        # Calculate original quality score (optimized)
        original_quality = self._calculate_quality_score_optimized(df)
        logger.info(f"   📈 Original quality: {original_quality:.1%}")

        # Apply improvements
        improvements = []

        # 1. Handle null values
        null_improvements = self._handle_null_values_optimized(df, source_name)
        improvements.extend(null_improvements)

        # 2. Normalize data types
        type_improvements = self._normalize_data_types_optimized(df, source_name)
        improvements.extend(type_improvements)

        # 3. Remove duplicates
        duplicate_improvements = self._remove_duplicates_optimized(df, source_name)
        improvements.extend(duplicate_improvements)

        # 4. Validate formats
        format_improvements = self._validate_formats_optimized(df, source_name)
        improvements.extend(format_improvements)

        # Calculate final quality score
        final_quality = self._calculate_quality_score_optimized(df)
        cleaned_records = len(df)
        removed_records = original_records - cleaned_records

        # Save improved data
        output_path = file_path.parent / f"{file_path.stem}_improved.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"   💾 Saved improved data to: {output_path.name}")

        processing_time = (datetime.now() - start_time).total_seconds()

        return ImprovementResult(
            source=source_name,
            original_records=original_records,
            cleaned_records=cleaned_records,
            removed_records=removed_records,
            quality_score_before=original_quality,
            quality_score_after=final_quality,
            improvements_applied=improvements,
            processing_time_seconds=processing_time
        )

    async def _read_large_file_chunked(self, file_path: Path) -> pd.DataFrame:
        """Read large files in chunks to avoid memory issues"""
        chunk_size = 50000  # Process 50K rows at a time
        chunks = []

        for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
            chunks.append(chunk)

            # Log progress
            if len(chunks) % 10 == 0:
                logger.info(f"      📖 Processed {len(chunks) * chunk_size:,} rows...")

        # Combine chunks
        df = pd.concat(chunks, ignore_index=True)
        logger.info(f"      ✅ Loaded {len(df):,} total records")
        return df

    def _calculate_quality_score_optimized(self, df: pd.DataFrame) -> float:
        """Calculate quality score using vectorized operations"""
        if df.empty:
            return 0.0

        # Calculate completeness (non-null values)
        completeness_score = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))

        # Calculate consistency (data type consistency)
        consistency_score = self._calculate_consistency_score(df)

        # Calculate validity (reasonable values)
        validity_score = self._calculate_validity_score_optimized(df)

        # Weighted average
        quality_score = (completeness_score * 0.4 +
                        consistency_score * 0.3 +
                        validity_score * 0.3)

        return quality_score

    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calculate data type consistency score"""
        if df.empty:
            return 0.0

        consistent_columns = 0
        total_columns = len(df.columns)

        for col in df.columns:
            try:
                # Check if column has consistent data types
                if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                    # Numeric column - check for non-numeric values
                    non_numeric_ratio = pd.to_numeric(df[col], errors='coerce').isna().sum() / len(df)
                    if non_numeric_ratio < 0.1:  # Less than 10% non-numeric
                        consistent_columns += 1
                else:
                    # String column - check for mixed types
                    sample = df[col].dropna().head(100)
                    if len(sample) > 0:
                        numeric_ratio = pd.to_numeric(sample, errors='coerce').notna().sum() / len(sample)
                        if numeric_ratio < 0.3:  # Less than 30% numeric in string column
                            consistent_columns += 1
            except:
                pass

        return consistent_columns / total_columns if total_columns > 0 else 0.0

    def _calculate_validity_score_optimized(self, df: pd.DataFrame) -> float:
        """Calculate validity score using vectorized operations"""
        if df.empty:
            return 0.0

        total_cells = len(df) * len(df.columns)
        valid_cells = 0

        # Process columns efficiently
        for col in df.columns:
            try:
                # Check for null values
                null_count = df[col].isna().sum()

                # Check for invalid string values
                if df[col].dtype == 'object':
                    invalid_strings = (df[col].astype(str).str.strip() == '').sum()
                    invalid_strings += df[col].astype(str).str.lower().isin(['null', 'none', 'nan', 'undefined']).sum()
                else:
                    invalid_strings = 0

                # Check for negative values in numeric columns (except price/amount/value)
                if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                    if col.lower() not in ['price', 'amount', 'value', 'cost', 'fee']:
                        negative_count = (df[col] < 0).sum()
                    else:
                        negative_count = 0
                else:
                    negative_count = 0

                # Calculate valid cells for this column
                invalid_cells = null_count + invalid_strings + negative_count
                valid_cells += (len(df) - invalid_cells)

            except Exception as e:
                logger.warning(f"Error processing column {col}: {e}")
                continue

        return valid_cells / total_cells if total_cells > 0 else 0.0

    def _handle_null_values_optimized(self, df: pd.DataFrame, source_name: str) -> list[str]:
        """Handle null values using vectorized operations"""
        improvements = []

        # Calculate null ratios per column
        null_ratios = df.isnull().sum() / len(df)
        high_null_columns = null_ratios[null_ratios > 0.3].index.tolist()

        for col in high_null_columns:
            null_ratio = null_ratios[col]

            if null_ratio > 0.8:
                # Remove columns with >80% null values
                df.drop(columns=[col], inplace=True)
                improvements.append(f"removed_column_{col}")
                logger.info(f"     🗑️ Removed column '{col}' ({null_ratio:.1%} null)")

            elif null_ratio > 0.5:
                # Fill with appropriate defaults
                if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                    df[col].fillna(0, inplace=True)
                    improvements.append(f"filled_nulls_{col}_with_zero")
                else:
                    df[col].fillna("Unknown", inplace=True)
                    improvements.append(f"filled_nulls_{col}_with_unknown")
                logger.info(f"     🔧 Filled nulls in '{col}' ({null_ratio:.1%} null)")

            elif null_ratio > 0.3:
                # Use forward fill
                df[col].fillna(method='ffill', inplace=True)
                df[col].fillna(method='bfill', inplace=True)
                improvements.append(f"forward_filled_{col}")
                logger.info(f"     🔄 Forward-filled '{col}' ({null_ratio:.1%} null)")

        return improvements

    def _normalize_data_types_optimized(self, df: pd.DataFrame, source_name: str) -> list[str]:
        """Normalize data types using vectorized operations"""
        improvements = []

        for col in df.columns:
            if df[col].dtype == 'object':
                # Sample for efficiency
                sample_values = df[col].dropna().head(100)

                if len(sample_values) > 0:
                    # Check for numeric values
                    numeric_count = pd.to_numeric(sample_values, errors='coerce').notna().sum()
                    numeric_ratio = numeric_count / len(sample_values)

                    if numeric_ratio > 0.7:
                        # Convert to numeric
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        improvements.append(f"converted_to_numeric_{col}")
                        logger.info(f"     🔢 Converted '{col}' to numeric")

                    elif numeric_ratio > 0.3:
                        # Create separate numeric column
                        numeric_col = pd.to_numeric(df[col], errors='coerce')
                        if numeric_col.notna().sum() > 0:
                            df[f"{col}_numeric"] = numeric_col
                            improvements.append(f"created_numeric_column_{col}")
                            logger.info(f"     ➕ Created numeric column for '{col}'")

        return improvements

    def _remove_duplicates_optimized(self, df: pd.DataFrame, source_name: str) -> list[str]:
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

    def _validate_formats_optimized(self, df: pd.DataFrame, source_name: str) -> list[str]:
        """Validate and fix data formats efficiently"""
        improvements = []

        # Date format validation
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    improvements.append(f"converted_to_datetime_{col}")
                    logger.info(f"     📅 Converted '{col}' to datetime")
                except:
                    pass

        # Email validation
        email_columns = [col for col in df.columns if 'email' in col.lower()]
        for col in email_columns:
            if col in df.columns:
                # Simple email validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                valid_emails = df[col].astype(str).str.match(email_pattern)
                invalid_count = (~valid_emails).sum()
                if invalid_count > 0:
                    logger.info(f"     📧 Found {invalid_count} invalid emails in '{col}'")

        return improvements

    async def generate_improvement_report(self) -> dict[str, Any]:
        """Generate comprehensive improvement report"""
        logger.info("\n📊 Generating Improvement Report")
        logger.info("=" * 50)

        total_sources = len(self.improvement_results)
        total_original_records = sum(r.original_records for r in self.improvement_results.values())
        total_cleaned_records = sum(r.cleaned_records for r in self.improvement_results.values())
        total_removed_records = sum(r.removed_records for r in self.improvement_results.values())

        avg_quality_before = np.mean([r.quality_score_before for r in self.improvement_results.values()])
        avg_quality_after = np.mean([r.quality_score_after for r in self.improvement_results.values()])

        total_processing_time = sum(r.processing_time_seconds for r in self.improvement_results.values())

        report = {
            "summary": {
                "total_sources": total_sources,
                "total_original_records": total_original_records,
                "total_cleaned_records": total_cleaned_records,
                "total_removed_records": total_removed_records,
                "avg_quality_before": avg_quality_before,
                "avg_quality_after": avg_quality_after,
                "quality_improvement": avg_quality_after - avg_quality_before,
                "total_processing_time_seconds": total_processing_time
            },
            "source_details": {
                source: {
                    "original_records": result.original_records,
                    "cleaned_records": result.cleaned_records,
                    "removed_records": result.removed_records,
                    "quality_before": result.quality_score_before,
                    "quality_after": result.quality_score_after,
                    "improvements_applied": result.improvements_applied,
                    "processing_time_seconds": result.processing_time_seconds
                }
                for source, result in self.improvement_results.items()
            },
            "generated_at": datetime.now().isoformat()
        }

        # Save report
        with open("optimized_improvement_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info("📊 Improvement Summary:")
        logger.info(f"   Sources processed: {total_sources}")
        logger.info(f"   Records processed: {total_original_records:,}")
        logger.info(f"   Records cleaned: {total_cleaned_records:,}")
        logger.info(f"   Records removed: {total_removed_records:,}")
        logger.info(f"   Avg quality before: {avg_quality_before:.1%}")
        logger.info(f"   Avg quality after: {avg_quality_after:.1%}")
        logger.info(f"   Quality improvement: {avg_quality_after - avg_quality_before:.1%}")
        logger.info(f"   Total processing time: {total_processing_time:.1f}s")

        return report

async def get_optimized_data_quality_improver(data_dir: Path = None) -> OptimizedDataQualityImprover:
    """Get optimized data quality improver instance"""
    return OptimizedDataQualityImprover(data_dir)
