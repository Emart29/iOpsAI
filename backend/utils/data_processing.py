# backend/utils/data_processing.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from scipy import stats
import json

def generate_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate comprehensive data profile"""
    profile = {
        "overview": {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_usage": int(df.memory_usage(deep=True).sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "total_missing": int(df.isnull().sum().sum()),
            "completeness_score": float(1 - (df.isnull().sum().sum() / (len(df) * len(df.columns))))
        },
        "columns": {},
        "data_quality": {
            "score": calculate_data_quality_score(df),
            "issues": detect_data_quality_issues(df)
        }
    }
    
    for column in df.columns:
        col_data = df[column]
        dtype = str(col_data.dtype)
        
        column_profile = {
            "dtype": dtype,
            "missing": int(col_data.isnull().sum()),
            "missing_percentage": float(col_data.isnull().sum() / len(df)),
            "unique": int(col_data.nunique()),
            "sample_data": get_sample_data(col_data)
        }
        
        # Numeric columns
        if np.issubdtype(col_data.dtype, np.number):
            column_profile["type"] = "numeric"
            column_profile["stats"] = {
                "mean": float(col_data.mean()) if not col_data.empty else 0,
                "std": float(col_data.std()) if not col_data.empty else 0,
                "min": float(col_data.min()) if not col_data.empty else 0,
                "max": float(col_data.max()) if not col_data.empty else 0,
                "median": float(col_data.median()) if not col_data.empty else 0,
                "q1": float(col_data.quantile(0.25)) if not col_data.empty else 0,
                "q3": float(col_data.quantile(0.75)) if not col_data.empty else 0
            }
            # Detect outliers
            outliers = detect_column_outliers(col_data)
            column_profile["outliers"] = outliers
            
        # Categorical columns
        else:
            column_profile["type"] = "categorical"
            value_counts = col_data.value_counts()
            column_profile["stats"] = {
                "top_value": value_counts.index[0] if not value_counts.empty else None,
                "top_frequency": int(value_counts.iloc[0]) if not value_counts.empty else 0,
                "unique_values": int(col_data.nunique())
            }
        
        profile["columns"][column] = column_profile
    
    return profile

def detect_outliers(df: pd.DataFrame, method: str = "iqr") -> Dict[str, Any]:
    """Detect outliers using specified method"""
    outliers = {
        "method": method,
        "columns": {},
        "summary": {
            "total_outliers": 0,
            "affected_columns": 0
        }
    }
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        col_outliers = detect_column_outliers(df[col], method)
        outliers["columns"][col] = col_outliers
        
        if col_outliers["count"] > 0:
            outliers["summary"]["total_outliers"] += col_outliers["count"]
            outliers["summary"]["affected_columns"] += 1
    
    return outliers

def detect_column_outliers(series: pd.Series, method: str = "iqr") -> Dict[str, Any]:
    """Detect outliers in a single column"""
    series_clean = series.dropna()
    
    if len(series_clean) == 0:
        return {"count": 0, "indices": [], "percentage": 0.0}
    
    if method == "iqr":
        Q1 = series_clean.quantile(0.25)
        Q3 = series_clean.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_mask = (series_clean < lower_bound) | (series_clean > upper_bound)
    
    elif method == "zscore":
        z_scores = np.abs(stats.zscore(series_clean))
        outlier_mask = z_scores > 3
    
    else:
        raise ValueError(f"Unknown outlier detection method: {method}")
    
    outlier_indices = series_clean[outlier_mask].index.tolist()
    
    return {
        "count": int(outlier_mask.sum()),
        "indices": outlier_indices,
        "percentage": float(outlier_mask.sum() / len(series_clean)),
        "method": method
    }

def generate_correlations(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate correlation matrix and insights"""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if len(numeric_df.columns) < 2:
        return {
            "matrix": {},
            "strong_correlations": [],
            "message": "Not enough numeric columns for correlation analysis"
        }
    
    correlation_matrix = numeric_df.corr()
    
    # Find strong correlations (absolute value > 0.7)
    strong_correlations = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            corr_value = correlation_matrix.iloc[i, j]
            if abs(corr_value) > 0.7:
                strong_correlations.append({
                    "variables": [
                        correlation_matrix.columns[i],
                        correlation_matrix.columns[j]
                    ],
                    "correlation": float(corr_value),
                    "strength": "strong" if abs(corr_value) > 0.8 else "moderate"
                })
    
    return {
        "matrix": correlation_matrix.to_dict(),
        "strong_correlations": strong_correlations,
        "summary": {
            "total_variables": len(numeric_df.columns),
            "strong_correlations_count": len(strong_correlations)
        }
    }

def calculate_data_quality_score(df: pd.DataFrame) -> float:
    """Calculate overall data quality score (0-100)"""
    try:
        # Completeness (40%)
        completeness = 1 - (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]))
        
        # Consistency (30%)
        consistency = 1.0
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for mixed types
                unique_types = set(type(x) for x in df[col].dropna() if x is not None)
                if len(unique_types) > 1:
                    consistency *= 0.8
        
        # Uniqueness (30%) - avoid perfect scores for ID columns
        uniqueness_scores = []
        for col in df.columns:
            unique_ratio = df[col].nunique() / len(df)
            # Penalize both too low and too high uniqueness
            if unique_ratio < 0.01:  # Almost constant
                uniqueness_scores.append(0.3)
            elif unique_ratio > 0.99:  # Almost unique (like IDs)
                uniqueness_scores.append(0.7)
            else:
                uniqueness_scores.append(1.0)
        
        uniqueness = np.mean(uniqueness_scores) if uniqueness_scores else 0.5
        
        total_score = (completeness * 0.4 + consistency * 0.3 + uniqueness * 0.3) * 100
        return min(max(total_score, 0), 100)
        
    except:
        return 50.0  # Default score if calculation fails

def detect_data_quality_issues(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Detect various data quality issues"""
    issues = []
    
    # Check for missing values
    missing_cols = df.columns[df.isnull().any()].tolist()
    for col in missing_cols:
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / len(df)) * 100
        if missing_pct > 10:  # Only flag significant missingness
            issues.append({
                "type": "missing_data",
                "column": col,
                "severity": "high" if missing_pct > 50 else "medium",
                "message": f"{missing_pct:.1f}% missing values in {col}",
                "suggestion": "Consider imputation or removal of this column"
            })
    
    # Check for constant columns
    for col in df.columns:
        if df[col].nunique() <= 1:
            issues.append({
                "type": "constant_column",
                "column": col,
                "severity": "low",
                "message": f"Column '{col}' has constant values",
                "suggestion": "Consider removing this column from analysis"
            })
    
    # Check for duplicate rows
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        duplicate_pct = (duplicate_count / len(df)) * 100
        issues.append({
            "type": "duplicate_rows",
            "severity": "medium" if duplicate_pct > 5 else "low",
            "message": f"{duplicate_count} duplicate rows ({duplicate_pct:.1f}%)",
            "suggestion": "Review and remove duplicate entries if necessary"
        })
    
    return issues

def get_sample_data(series: pd.Series, n: int = 5) -> List:
    """Get sample data from a series"""
    non_null_data = series.dropna()
    if len(non_null_data) == 0:
        return []
    
    sample = non_null_data.head(n).tolist()
    # Convert non-serializable types to strings
    return [str(x) if not isinstance(x, (str, int, float, bool)) else x for x in sample]

def generate_basic_profile(df: pd.DataFrame) -> dict:
    """Generate basic data profile (lighter version)"""
    total = df.size
    missing = df.isnull().sum().sum()
    completeness = 1 - (missing / total) if total else 0
    cols = {}
    for col in df.columns:
        s = df[col]
        cols[col] = {
            "dtype": str(s.dtype),
            "missing": int(s.isnull().sum()),
            "unique": int(s.nunique()),
            "type": "numeric" if pd.api.types.is_numeric_dtype(s) else "categorical",
            "sample": s.dropna().head(3).tolist()
        }
    return {
        "overview": {"rows": len(df), "columns": len(df.columns), "total_missing": int(missing), "completeness_score": round(completeness, 4)},
        "columns": cols,
        "data_quality": {"score": round(80 + 20 * completeness, 1), "issues": []}
    }

def generate_plotly_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate JSON data for interactive Plotly charts"""
    charts = {}
    
    # 1. Histograms for Numeric Columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols[:10]:  # Limit to 10
        charts[f"hist_{col}"] = {
            "data": [{
                "x": df[col].dropna().tolist(),
                "type": "histogram",
                "marker": {"color": "#6366f1"}
            }],
            "layout": {
                "title": f"Distribution of {col}",
                "xaxis": {"title": col},
                "yaxis": {"title": "Count"},
                "autosize": True
            }
        }
    
    # 2. Bar Charts for Categorical Columns
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in cat_cols[:10]:
        val_counts = df[col].value_counts().head(15)
        charts[f"bar_{col}"] = {
            "data": [{
                "x": val_counts.index.tolist(),
                "y": val_counts.values.tolist(),
                "type": "bar",
                "marker": {"color": "#8b5cf6"}
            }],
            "layout": {
                "title": f"Top Values in {col}",
                "xaxis": {"title": col},
                "yaxis": {"title": "Frequency"},
                "autosize": True
            }
        }
        
    # 3. Correlation Heatmap
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        charts["correlation_heatmap"] = {
            "data": [{
                "z": corr.values.tolist(),
                "x": corr.columns.tolist(),
                "y": corr.index.tolist(),
                "type": "heatmap",
                "colorscale": "Viridis"
            }],
            "layout": {
                "title": "Correlation Matrix",
                "autosize": True
            }
        }
        
    # 4. Scatter Matrix (Top 3 Numeric)
    if len(numeric_cols) >= 2:
        top_numeric = numeric_cols[:3]
        charts["scatter_matrix"] = {
            "data": [{
                "type": "splom",
                "dimensions": [
                    {"label": col, "values": df[col].replace({np.nan: None}).tolist()} 
                    for col in top_numeric
                ],
                "marker": {"color": "#ec4899"}
            }],
            "layout": {
                "title": "Scatter Matrix",
                "autosize": True
            }
        }

    return charts
