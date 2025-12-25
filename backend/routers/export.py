from storage import storage
from fastapi import APIRouter, HTTPException, Depends, Response
import pandas as pd
import numpy as np
import io
from datetime import datetime

router = APIRouter(prefix="/export", tags=["export"])

@router.post("/code")
async def export_python_code(session_id: str):
    """Export reproducible Python code for the analysis"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Construct dataset info from session
    dataset_info = {
        'filename': session['filename'],
        'shape': session['dataframe_shape'],
        'columns': session.get('analysis', {}).get('columns', [])
    }
    
    # If columns missing in analysis, try to read from parquet
    if not dataset_info['columns']:
        try:
            df = pd.read_parquet(session['parquet_path'])
            dataset_info['columns'] = list(df.columns)
        except:
            dataset_info['columns'] = []

    analyses = storage.get_analyses(session_id)
    
    code = generate_python_code(dataset_info, analyses)
    
    return {
        "code": code,
        "filename": f"insight_studio_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
        "language": "python"
    }

@router.post("/clean")
async def export_clean_data(session_id: str, format: str = "csv"):
    """Export cleaned data in specified format"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_path = session['parquet_path']
    
    try:
        df = pd.read_parquet(file_path)
        
        # Basic cleaning operations
        df_clean = df.copy()
        df_clean = df_clean.dropna(axis=1, how='all')
        
        for col in df_clean.columns:
            if df_clean[col].dtype in [np.float64, np.int64]:
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            else:
                df_clean[col] = df_clean[col].fillna('Unknown')
        
        if format == "csv":
            output = df_clean.to_csv(index=False)
            media_type = "text/csv"
            filename = f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            return Response(
                content=output,
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        elif format == "excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_clean.to_excel(writer, index=False, sheet_name='Cleaned Data')
            output.seek(0)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            return Response(
                content=output.getvalue(),
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")

def generate_python_code(dataset_info, analyses):
    """Generate reproducible Python code for the analysis"""
    
    code = f'''# Insight Studio Generated Code
# Dataset: {dataset_info['filename']}
# Generated: {datetime.now().isoformat()}
# Rows: {dataset_info['shape'][0]}, Columns: {dataset_info['shape'][1]}

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("Dataset Overview")
print("=" * 50)
print(f"Shape: {dataset_info['shape']}")
print(f"Columns: {list(dataset_info['columns'])}")

# Load your data
# df = pd.read_csv('your_dataset.csv')

# Data Quality Check
print("\\\\nData Quality Assessment")
print("=" * 50)
print("Missing values by column:")
# for col in df.columns:
#     missing_count = df[col].isnull().sum()
#     if missing_count > 0:
#         print(f"  {{col}}: {{missing_count}} missing values ({{missing_count/len(df)*100:.1f}}%)")

# Basic Statistics
print("\\\\nBasic Statistics")
print("=" * 50)
# print(df.describe())

# Example visualization code
def create_basic_visualizations(df):
    """Create basic visualizations for numeric data"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) > 0:
        # Histograms for numeric columns
        df[numeric_cols].hist(bins=30, figsize=(15, 10))
        plt.suptitle("Distribution of Numeric Variables")
        plt.tight_layout()
        plt.show()
        
        # Correlation heatmap
        if len(numeric_cols) > 1:
            plt.figure(figsize=(10, 8))
            sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', center=0)
            plt.title("Correlation Heatmap")
            plt.tight_layout()
            plt.show()

# Uncomment to run visualizations
# create_basic_visualizations(df)

print("\\\\nAnalysis complete!")
print("=" * 50)
'''
    return code