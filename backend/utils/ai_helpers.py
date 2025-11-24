# backend/utils/ai_helpers.py
import pandas as pd
import numpy as np
import re
from typing import Dict, Any, List
from datetime import datetime

def generate_ai_response(df: pd.DataFrame, question: str) -> Dict[str, Any]:
    """Generate AI response based on dataset and question"""
    question_lower = question.lower()
    
    # Basic question classification and response generation
    if any(word in question_lower for word in ['missing', 'null', 'empty', 'na']):
        return handle_missing_data_question(df, question)
    
    elif any(word in question_lower for word in ['outlier', 'anomaly', 'unusual']):
        return handle_outlier_question(df, question)
    
    elif any(word in question_lower for word in ['correlation', 'relationship', 'related']):
        return handle_correlation_question(df, question)
    
    elif any(word in question_lower for word in ['distribution', 'histogram', 'frequency']):
        return handle_distribution_question(df, question)
    
    elif any(word in question_lower for word in ['summary', 'overview', 'describe']):
        return handle_summary_question(df, question)
    
    elif any(word in question_lower for word in ['pattern', 'trend', 'insight']):
        return handle_pattern_question(df, question)
    
    else:
        return handle_general_question(df, question)

def handle_missing_data_question(df: pd.DataFrame, question: str) -> Dict[str, Any]:
    """Handle questions about missing data"""
    missing_data = df.isnull().sum()
    missing_cols = missing_data[missing_data > 0]
    
    if len(missing_cols) == 0:
        answer = "Excellent! Your dataset has no missing values. This means you have complete data for all columns, which is ideal for analysis."
        confidence = 0.95
        suggestions = [
            "Proceed with statistical analysis and modeling",
            "Generate comprehensive visualizations",
            "Explore correlations between variables"
        ]
    else:
        most_affected = missing_cols.idxmax()
        most_missing = missing_cols.max()
        missing_pct = (most_missing / len(df)) * 100
        
        answer = f"I found {len(missing_cols)} columns with missing values. "
        answer += f"The most affected column is '{most_affected}' with {most_missing} missing values ({missing_pct:.1f}% of the data). "
        
        if missing_pct > 50:
            answer += "This column has significant missing data and might need special handling or removal."
            confidence = 0.85
        elif missing_pct > 20:
            answer += "This column has considerable missing data. Consider advanced imputation techniques."
            confidence = 0.80
        else:
            answer += "The missing data is relatively minor and can be handled with standard imputation methods."
            confidence = 0.75
        
        suggestions = [
            "Use mean/median imputation for numeric columns",
            "Use mode imputation for categorical columns",
            "Consider multiple imputation for significant missingness",
            "Remove columns with >50% missing data if not critical"
        ]
    
    return {
        "answer": answer,
        "confidence": confidence,
        "suggestions": suggestions,
        "analysis_type": "missing_data_analysis"
    }

def handle_outlier_question(df: pd.DataFrame, question: str) -> Dict[str, Any]:
    """Handle questions about outliers"""
    from utils.data_processing import detect_outliers
    
    try:
        outliers = detect_outliers(df)
        total_outliers = outliers["summary"]["total_outliers"]
        affected_columns = outliers["summary"]["affected_columns"]
        
        if total_outliers == 0:
            answer = "Great news! I didn't detect any significant outliers in your numeric data using the IQR method. Your data appears to be well-distributed."
            confidence = 0.90
            suggestions = [
                "Proceed with statistical analysis",
                "Check for multivariate outliers",
                "Validate data collection process"
            ]
        else:
            # Find column with most outliers
            max_outliers_col = None
            max_outliers_count = 0
            for col, col_outliers in outliers["columns"].items():
                if col_outliers["count"] > max_outliers_count:
                    max_outliers_count = col_outliers["count"]
                    max_outliers_col = col
            
            outlier_pct = (total_outliers / (len(df) * len(df.select_dtypes(include=[np.number]).columns))) * 100
            
            answer = f"I detected {total_outliers} potential outliers across {affected_columns} numeric columns. "
            answer += f"The column '{max_outliers_col}' has the most outliers ({max_outliers_count}). "
            
            if outlier_pct > 5:
                answer += "The outlier percentage is relatively high. These might represent genuine extreme values or data errors."
                confidence = 0.80
            else:
                answer += "The outlier percentage is within expected ranges. These are likely genuine extreme values."
                confidence = 0.75
            
            suggestions = [
                "Investigate outliers for data quality issues",
                "Use robust statistical methods if outliers are genuine",
                "Consider winsorization for extreme values",
                "Create visualizations to examine outlier patterns"
            ]
        
        return {
            "answer": answer,
            "confidence": confidence,
            "suggestions": suggestions,
            "analysis_type": "outlier_detection"
        }
        
    except Exception as e:
        return {
            "answer": "I encountered an error while analyzing outliers. Please ensure you have numeric columns in your dataset.",
            "confidence": 0.60,
            "suggestions": ["Check that your dataset contains numeric columns", "Verify data types are correctly assigned"],
            "analysis_type": "outlier_detection"
        }

def handle_correlation_question(df: pd.DataFrame, question: str) -> Dict[str, Any]:
    """Handle questions about correlations"""
    from utils.data_processing import generate_correlations
    
    try:
        correlations = generate_correlations(df)
        strong_corrs = correlations["strong_correlations"]
        
        if not strong_corrs:
            answer = "I didn't find any strong correlations (|r| > 0.7) between your numeric variables. The variables appear to be relatively independent."
            confidence = 0.85
            suggestions = [
                "Explore weaker correlations that might still be meaningful",
                "Consider non-linear relationships",
                "Check for correlations within subgroups of your data"
            ]
        else:
            answer = f"I found {len(strong_corrs)} strong correlation(s) in your data:\n"
            for i, corr in enumerate(strong_corrs[:3]):  # Show top 3
                vars = corr["variables"]
                strength = corr["strength"]
                value = corr["correlation"]
                answer += f"\n• {vars[0]} and {vars[1]} ({strength} correlation: r = {value:.2f})"
            
            if len(strong_corrs) > 3:
                answer += f"\n\n... and {len(strong_corrs) - 3} more strong correlations."
            
            confidence = 0.88
            suggestions = [
                "Create scatter plots for strongly correlated variables",
                "Investigate causal relationships",
                "Check for multicollinearity in regression models",
                "Explore these relationships in your visualizations"
            ]
        
        return {
            "answer": answer,
            "confidence": confidence,
            "suggestions": suggestions,
            "analysis_type": "correlation_analysis"
        }
        
    except Exception as e:
        return {
            "answer": "I couldn't perform correlation analysis. This might be because you don't have enough numeric columns or there's an issue with the data.",
            "confidence": 0.65,
            "suggestions": ["Ensure you have at least two numeric columns", "Check for valid numeric data"],
            "analysis_type": "correlation_analysis"
        }

def handle_distribution_question(df: pd.DataFrame, question: str) -> Dict[str, Any]:
    """Handle questions about data distributions"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    if len(numeric_cols) == 0 and len(categorical_cols) == 0:
        answer = "I couldn't find any numeric or categorical columns to analyze distributions. Please check your data types."
        confidence = 0.70
        suggestions = ["Verify that your data contains numeric or categorical columns", "Check data type assignments"]
    else:
        answer = "Here's what I found about your data distributions:\n"
        
        if len(numeric_cols) > 0:
            answer += f"\n• You have {len(numeric_cols)} numeric columns"
            # Check for normality in first few numeric columns
            for col in numeric_cols[:2]:
                data = df[col].dropna()
                if len(data) > 30:  # Only test for normality with sufficient data
                    from scipy import stats
                    _, p_value = stats.normaltest(data)
                    if p_value > 0.05:
                        answer += f"\n  - {col} appears normally distributed"
                    else:
                        answer += f"\n  - {col} doesn't appear normally distributed"
        
        if len(categorical_cols) > 0:
            answer += f"\n• You have {len(categorical_cols)} categorical columns"
            for col in categorical_cols[:2]:
                unique_count = df[col].nunique()
                answer += f"\n  - {col} has {unique_count} unique values"
        
        confidence = 0.80
        suggestions = [
            "Create histograms for numeric variables",
            "Generate bar charts for categorical variables",
            "Check for skewed distributions that might need transformation",
            "Explore value counts for categorical variables"
        ]
    
    return {
        "answer": answer,
        "confidence": confidence,
        "suggestions": suggestions,
        "analysis_type": "distribution_analysis"
    }

def handle_summary_question(df: pd.DataFrame, question: str) -> Dict[str, Any]:
    """Handle general summary questions"""
    from utils.data_processing import generate_data_profile
    
    profile = generate_data_profile(df)
    overview = profile["overview"]
    
    answer = f"Here's a summary of your dataset:\n"
    answer += f"• **Size**: {overview['rows']} rows × {overview['columns']} columns\n"
    answer += f"• **Completeness**: {overview['completeness_score']*100:.1f}% complete data\n"
    answer += f"• **Quality Score**: {profile['data_quality']['score']:.1f}/100\n"
    answer += f"• **Duplicate Rows**: {overview['duplicate_rows']}\n"
    
    # Column type summary
    numeric_count = sum(1 for col_info in profile["columns"].values() if col_info["type"] == "numeric")
    categorical_count = sum(1 for col_info in profile["columns"].values() if col_info["type"] == "categorical")
    
    answer += f"• **Column Types**: {numeric_count} numeric, {categorical_count} categorical\n"
    
    # Data quality issues
    issues = profile["data_quality"]["issues"]
    if issues:
        answer += f"• **Quality Issues**: {len(issues)} detected\n"
    
    confidence = 0.90
    suggestions = [
        "Explore individual column statistics",
        "Generate detailed data quality report",
        "Create comprehensive visualizations",
        "Perform advanced statistical analysis"
    ]
    
    return {
        "answer": answer,
        "confidence": confidence,
        "suggestions": suggestions,
        "analysis_type": "dataset_summary"
    }

def handle_pattern_question(df: pd.DataFrame, question: str) -> Dict[str, Any]:
    """Handle questions about patterns and trends"""
    # Simple pattern detection
    patterns = []
    
    # Check for time-based patterns if datetime columns exist
    datetime_cols = df.select_dtypes(include=['datetime']).columns
    if len(datetime_cols) > 0:
        patterns.append("Time-based data detected - consider time series analysis")
    
    # Check for numeric trends
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols[:3]:  # Check first 3 numeric columns
        data = df[col].dropna()
        if len(data) > 10:
            # Simple trend detection
            x = np.arange(len(data))
            correlation = np.corrcoef(x, data)[0,1]
            if abs(correlation) > 0.5:
                trend = "increasing" if correlation > 0 else "decreasing"
                patterns.append(f"Potential {trend} trend in {col}")
    
    if patterns:
        answer = "I detected several interesting patterns in your data:\n• " + "\n• ".join(patterns[:5])
        if len(patterns) > 5:
            answer += f"\n\n... and {len(patterns) - 5} more patterns."
    else:
        answer = "I didn't detect obvious patterns automatically. Consider exploring specific relationships or using advanced pattern detection methods."
    
    confidence = 0.75
    suggestions = [
        "Use time series decomposition for temporal data",
        "Explore clustering patterns",
        "Check for seasonal variations",
        "Perform principal component analysis"
    ]
    
    return {
        "answer": answer,
        "confidence": confidence,
        "suggestions": suggestions,
        "analysis_type": "pattern_detection"
    }

def handle_general_question(df: pd.DataFrame, question: str) -> Dict[str, Any]:
    """Handle general questions not covered by specific categories"""
    # Fallback response for general questions
    answer = f"I've analyzed your dataset with {len(df)} rows and {len(df.columns)} columns. "
    answer += "The data appears ready for comprehensive analysis. "
    answer += "For more specific insights, try asking about missing data, outliers, correlations, or data distributions."
    
    confidence = 0.70
    suggestions = [
        "Ask about data quality issues",
        "Request correlation analysis",
        "Explore outlier detection",
        "Get distribution insights"
    ]
    
    return {
        "answer": answer,
        "confidence": confidence,
        "suggestions": suggestions,
        "analysis_type": "general_analysis"
    }

def detect_semantic_types(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect semantic types of columns (beyond basic dtypes)"""
    semantic_types = {}
    
    for col in df.columns:
        col_data = df[col].dropna()
        
        if len(col_data) == 0:
            semantic_types[col] = {"type": "unknown", "confidence": 0.0}
            continue
        
        # Check for different semantic types
        if is_id_column(col_data, col):
            semantic_types[col] = {"type": "identifier", "confidence": 0.85}
        elif is_date_column(col_data):
            semantic_types[col] = {"type": "datetime", "confidence": 0.80}
        elif is_categorical_column(col_data):
            semantic_types[col] = {"type": "categorical", "confidence": 0.75}
        elif is_numeric_measurement(col_data, col):
            semantic_types[col] = {"type": "measurement", "confidence": 0.80}
        elif is_currency_column(col_data, col):
            semantic_types[col] = {"type": "currency", "confidence": 0.70}
        elif is_text_column(col_data):
            semantic_types[col] = {"type": "text", "confidence": 0.75}
        else:
            # Fall back to basic dtype
            basic_type = "numeric" if np.issubdtype(df[col].dtype, np.number) else "categorical"
            semantic_types[col] = {"type": basic_type, "confidence": 0.60}
    
    return semantic_types

def generate_suggestions(df: pd.DataFrame, goal: str = None) -> List[str]:
    """Generate AI suggestions for data analysis"""
    suggestions = []
    
    # Basic suggestions based on data characteristics
    if len(df) > 1000:
        suggestions.append("Perform statistical significance testing")
    
    if df.select_dtypes(include=[np.number]).shape[1] >= 3:
        suggestions.append("Explore multivariate correlations")
        suggestions.append("Consider principal component analysis (PCA)")
    
    if df.select_dtypes(include=['object']).shape[1] >= 2:
        suggestions.append("Analyze categorical variable relationships")
        suggestions.append("Create cross-tabulation tables")
    
    if df.isnull().sum().sum() > 0:
        suggestions.append("Address missing data with appropriate imputation")
    
    # Goal-specific suggestions
    if goal:
        goal_lower = goal.lower()
        if "predict" in goal_lower or "forecast" in goal_lower:
            suggestions.extend([
                "Split data into training and testing sets",
                "Explore feature importance",
                "Consider multiple machine learning models"
            ])
        elif "segment" in goal_lower or "cluster" in goal_lower:
            suggestions.extend([
                "Perform clustering analysis",
                "Use dimensionality reduction for visualization",
                "Evaluate cluster quality metrics"
            ])
        elif "validate" in goal_lower or "quality" in goal_lower:
            suggestions.extend([
                "Create data quality dashboard",
                "Establish validation rules",
                "Monitor data quality metrics over time"
            ])
    
    # Always include these general suggestions
    general_suggestions = [
        "Create comprehensive data profile",
        "Generate correlation matrix",
        "Detect and handle outliers",
        "Export analysis results",
        "Document findings and insights"
    ]
    
    suggestions.extend(general_suggestions)
    return list(set(suggestions))[:10]  # Remove duplicates and limit to 10

# Helper functions for semantic type detection
def is_id_column(data, col_name):
    """Check if column is likely an identifier"""
    col_name_lower = col_name.lower()
    id_keywords = ['id', 'code', 'key', 'number', 'num', 'ref']
    if any(keyword in col_name_lower for keyword in id_keywords):
        return True
    
    # Check if data has high uniqueness
    uniqueness = data.nunique() / len(data)
    return uniqueness > 0.9 and len(data) > 10

def is_date_column(data):
    """Check if column contains date-like data"""
    sample_values = data.head(10).astype(str)
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',
        r'\d{2}/\d{2}/\d{4}',
        r'\d{2}-\d{2}-\d{4}',
        r'\d{1,2}/\d{1,2}/\d{2,4}'
    ]
    
    for pattern in date_patterns:
        if sample_values.str.match(pattern).any():
            return True
    return False

def is_categorical_column(data):
    """Check if column is categorical"""
    if data.dtype == 'object':
        uniqueness = data.nunique() / len(data)
        return uniqueness < 0.5  # Less than 50% unique values
    return False

def is_numeric_measurement(data, col_name):
    """Check if column is a numeric measurement"""
    if not np.issubdtype(data.dtype, np.number):
        return False
    
    col_name_lower = col_name.lower()
    measurement_keywords = ['amount', 'quantity', 'score', 'rating', 'level', 'value']
    return any(keyword in col_name_lower for keyword in measurement_keywords)

def is_currency_column(data, col_name):
    """Check if column contains currency values"""
    col_name_lower = col_name.lower()
    currency_keywords = ['price', 'cost', 'revenue', 'salary', 'amount', 'fee']
    if any(keyword in col_name_lower for keyword in currency_keywords):
        return True
    
    # Check if values look like currency
    sample_values = data.head(10).astype(str)
    return sample_values.str.contains(r'^\$?[\d,]+\.?\d*$').any()

def is_text_column(data):
    """Check if column contains free text"""
    if data.dtype != 'object':
        return False
    
    sample_values = data.head(10).dropna()
    if len(sample_values) == 0:
        return False
    
    # Check if values contain spaces and have variable lengths
    has_spaces = sample_values.astype(str).str.contains(' ').any()
    length_variance = sample_values.astype(str).str.len().std()
    
    return has_spaces and length_variance > 5