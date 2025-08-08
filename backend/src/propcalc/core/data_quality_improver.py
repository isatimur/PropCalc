"""
Data Quality Improvement Module for PropCalc
Addresses data quality issues identified in testing
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

class DataQualityImprover:
    """Improves data quality by addressing identified issues"""

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("..")
        self.improvement_results = {}

    async def improve_all_sources(self) -> dict[str, ImprovementResult]:
        """Improve data quality for all sources"""
        logger.info("🔧 Starting Data Quality Improvement Process")
        logger.info("=" * 60)

        # Sources with identified quality issues
        priority_sources = [
            ("rent_contracts", "Rent_Contracts.csv"),
            ("units", "Units.csv"),
            ("buildings", "Buildings.csv"),
            ("map_requests", "Map_Requests.csv")
        ]

        results = {}

        for source_name, filename in priority_sources:
            file_path = self.data_dir / filename
            if file_path.exists():
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

        # Read original data
        original_df = pd.read_csv(file_path, low_memory=False)
        original_records = len(original_df)
        original_quality = self._calculate_quality_score(original_df)

        # Apply improvements
        cleaned_df = original_df.copy()
        improvements_applied = []

        # 1. Handle high null ratios
        null_improvements = self._handle_null_values(cleaned_df, source_name)
        if null_improvements:
            improvements_applied.extend(null_improvements)

        # 2. Normalize mixed data types
        type_improvements = self._normalize_data_types(cleaned_df, source_name)
        if type_improvements:
            improvements_applied.extend(type_improvements)

        # 3. Remove duplicates
        if cleaned_df.duplicated().sum() > 0:
            cleaned_df = cleaned_df.drop_duplicates()
            improvements_applied.append("removed_duplicates")

        # 4. Validate formats
        format_improvements = self._validate_formats(cleaned_df, source_name)
        if format_improvements:
            improvements_applied.extend(format_improvements)

        # Calculate final metrics
        cleaned_records = len(cleaned_df)
        removed_records = original_records - cleaned_records
        final_quality = self._calculate_quality_score(cleaned_df)
        processing_time = (datetime.now() - start_time).total_seconds()

        # Save improved data
        improved_file_path = file_path.parent / f"{file_path.stem}_improved.csv"
        cleaned_df.to_csv(improved_file_path, index=False)

        result = ImprovementResult(
            source=source_name,
            original_records=original_records,
            cleaned_records=cleaned_records,
            removed_records=removed_records,
            quality_score_before=original_quality,
            quality_score_after=final_quality,
            improvements_applied=improvements_applied,
            processing_time_seconds=processing_time
        )

        logger.info(f"   📊 Quality: {original_quality:.1%} → {final_quality:.1%}")
        logger.info(f"   🗑️ Removed: {removed_records:,} records")
        logger.info(f"   ⚡ Applied: {len(improvements_applied)} improvements")

        return result

    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate data quality score"""
        if len(df) == 0:
            return 0.0

        # Calculate completeness (non-null ratio)
        non_null_ratio = df.notna().sum().sum() / (len(df) * len(df.columns))

        # Calculate consistency (no duplicates)
        duplicate_ratio = 1 - (df.duplicated().sum() / len(df))

        # Calculate validity (basic format checks)
        validity_score = self._calculate_validity_score(df)

        # Combined score
        quality_score = (non_null_ratio * 0.5 + duplicate_ratio * 0.3 + validity_score * 0.2)

        return quality_score

    def _calculate_validity_score(self, df: pd.DataFrame) -> float:
        """Calculate data validity score - OPTIMIZED for large datasets"""
        if len(df) == 0:
            return 0.0

        total_records = len(df)

        # Process in chunks to avoid memory issues and improve performance
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

            # Log progress for large datasets
            if total_chunks > 10 and (chunk_idx + 1) % 10 == 0:
                logger.info(f"   📈 Processed {chunk_idx + 1}/{total_chunks} chunks...")

        validity_score = valid_records / total_records if total_records > 0 else 0.0
        logger.info(f"   ✅ Validity score: {validity_score:.3f} ({valid_records:,}/{total_records:,} valid rows)")

        return validity_score

    def _handle_null_values(self, df: pd.DataFrame, source_name: str) -> list[str]:
        """Handle high null ratios"""
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
                # Fill with appropriate defaults for >50% null values
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col].fillna(0, inplace=True)
                    improvements.append(f"filled_nulls_{col}_with_zero")
                else:
                    df[col].fillna("Unknown", inplace=True)
                    improvements.append(f"filled_nulls_{col}_with_unknown")
                logger.info(f"     🔧 Filled nulls in '{col}' ({null_ratio:.1%} null)")

            elif null_ratio > 0.3:
                # Use forward fill for moderate null values
                df[col].fillna(method='ffill', inplace=True)
                df[col].fillna(method='bfill', inplace=True)  # Fill remaining nulls
                improvements.append(f"forward_filled_{col}")
                logger.info(f"     🔄 Forward-filled '{col}' ({null_ratio:.1%} null)")

        return improvements

    def _normalize_data_types(self, df: pd.DataFrame, source_name: str) -> list[str]:
        """Normalize mixed data types"""
        improvements = []

        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column contains mixed data types
                sample_values = df[col].dropna().head(100)

                # Check for numeric values in string columns
                numeric_count = pd.to_numeric(sample_values, errors='coerce').notna().sum()
                numeric_ratio = numeric_count / len(sample_values) if len(sample_values) > 0 else 0

                if numeric_ratio > 0.7:
                    # Convert to numeric
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    improvements.append(f"converted_to_numeric_{col}")
                    logger.info(f"     🔢 Converted '{col}' to numeric")

                elif numeric_ratio > 0.3:
                    # Mixed types - create separate numeric column
                    numeric_col = pd.to_numeric(df[col], errors='coerce')
                    if numeric_col.notna().sum() > 0:
                        df[f"{col}_numeric"] = numeric_col
                        improvements.append(f"created_numeric_column_{col}")
                        logger.info(f"     ➕ Created numeric column for '{col}'")

        return improvements

    def _validate_formats(self, df: pd.DataFrame, source_name: str) -> list[str]:
        """Validate and fix data formats"""
        improvements = []

        # Date format validation
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        for col in date_columns:
            if col in df.columns:
                # Try to convert to datetime
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
                # Basic email validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                valid_emails = df[col].str.match(email_pattern, na=False)
                invalid_count = (~valid_emails).sum()

                if invalid_count > 0:
                    # Remove invalid emails
                    df.loc[~valid_emails, col] = None
                    improvements.append(f"cleaned_invalid_emails_{col}")
                    logger.info(f"     🧹 Cleaned {invalid_count} invalid emails in '{col}'")

        # Phone number validation
        phone_columns = [col for col in df.columns if 'phone' in col.lower() or 'mobile' in col.lower()]
        for col in phone_columns:
            if col in df.columns:
                # Basic phone validation (digits only)
                phone_pattern = r'^[\d\s\-\+\(\)]+$'
                valid_phones = df[col].str.match(phone_pattern, na=False)
                invalid_count = (~valid_phones).sum()

                if invalid_count > 0:
                    # Clean phone numbers
                    df[col] = df[col].str.replace(r'[^\d\s\-\+\(\)]', '', regex=True)
                    improvements.append(f"cleaned_phone_numbers_{col}")
                    logger.info(f"     📞 Cleaned {invalid_count} invalid phone numbers in '{col}'")

        return improvements

    async def generate_improvement_report(self) -> dict[str, Any]:
        """Generate comprehensive improvement report"""
        logger.info("\n📊 Generating Data Quality Improvement Report")
        logger.info("=" * 60)

        if not self.improvement_results:
            logger.warning("No improvement results available")
            return {}

        # Calculate overall metrics
        total_original_records = sum(r.original_records for r in self.improvement_results.values())
        total_cleaned_records = sum(r.cleaned_records for r in self.improvement_results.values())
        total_removed_records = sum(r.removed_records for r in self.improvement_results.values())

        avg_quality_before = np.mean([r.quality_score_before for r in self.improvement_results.values()])
        avg_quality_after = np.mean([r.quality_score_after for r in self.improvement_results.values()])

        total_improvements = sum(len(r.improvements_applied) for r in self.improvement_results.values())

        report = {
            'summary': {
                'sources_improved': len(self.improvement_results),
                'total_original_records': total_original_records,
                'total_cleaned_records': total_cleaned_records,
                'total_removed_records': total_removed_records,
                'removal_rate': total_removed_records / total_original_records if total_original_records > 0 else 0,
                'avg_quality_before': avg_quality_before,
                'avg_quality_after': avg_quality_after,
                'quality_improvement': avg_quality_after - avg_quality_before,
                'total_improvements_applied': total_improvements,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': {
                source: {
                    'original_records': result.original_records,
                    'cleaned_records': result.cleaned_records,
                    'removed_records': result.removed_records,
                    'quality_score_before': result.quality_score_before,
                    'quality_score_after': result.quality_score_after,
                    'improvements_applied': result.improvements_applied,
                    'processing_time_seconds': result.processing_time_seconds
                }
                for source, result in self.improvement_results.items()
            },
            'improvement_types': self._categorize_improvements(),
            'recommendations': self._generate_recommendations()
        }

        # Save report
        report_file = Path("data_quality_improvement_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info("📊 Improvement Summary:")
        logger.info(f"   Sources Improved: {len(self.improvement_results)}")
        logger.info(f"   Records: {total_original_records:,} → {total_cleaned_records:,}")
        logger.info(f"   Removed: {total_removed_records:,} ({total_removed_records/total_original_records:.1%})")
        logger.info(f"   Quality: {avg_quality_before:.1%} → {avg_quality_after:.1%}")
        logger.info(f"   Improvements: {total_improvements} applied")

        logger.info(f"\n💾 Detailed report saved to: {report_file}")

        return report

    def _categorize_improvements(self) -> dict[str, int]:
        """Categorize improvements by type"""
        categories = {}

        for result in self.improvement_results.values():
            for improvement in result.improvements_applied:
                category = improvement.split('_')[0]
                categories[category] = categories.get(category, 0) + 1

        return categories

    def _generate_recommendations(self) -> list[dict[str, str]]:
        """Generate recommendations based on improvement results"""
        recommendations = []

        # Analyze improvement results
        for source, result in self.improvement_results.items():
            quality_improvement = result.quality_score_after - result.quality_score_before

            if quality_improvement < 0.1:
                recommendations.append({
                    'source': source,
                    'recommendation': f"Consider more aggressive cleaning for {source}",
                    'priority': 'MEDIUM',
                    'reason': f"Low quality improvement ({quality_improvement:.1%})"
                })

            if result.removed_records > result.original_records * 0.1:
                recommendations.append({
                    'source': source,
                    'recommendation': f"Review data source quality for {source}",
                    'priority': 'HIGH',
                    'reason': f"High record removal rate ({result.removed_records/result.original_records:.1%})"
                })

        return recommendations

# Global instance
_data_quality_improver = None

async def get_data_quality_improver(data_dir: Path = None) -> DataQualityImprover:
    """Get global data quality improver instance"""
    global _data_quality_improver
    if _data_quality_improver is None:
        _data_quality_improver = DataQualityImprover(data_dir)
    return _data_quality_improver
