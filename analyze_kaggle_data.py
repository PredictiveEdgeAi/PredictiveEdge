"""
Script to analyze Kaggle datasets and generate a comprehensive report.
"""
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

def analyze_csv_file(file_path):
    """Analyze a single CSV file and return its metadata."""
    try:
        df = pd.read_csv(file_path, low_memory=False)
        
        info = {
            'file_name': os.path.basename(file_path),
            'file_path': file_path,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'null_percentages': (df.isnull().sum() / len(df) * 100).to_dict(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'sample_data': df.head(3).to_dict('records') if len(df) > 0 else [],
            'date_columns': [],
            'numeric_columns': [],
            'categorical_columns': []
        }
        
        # Identify column types
        for col in df.columns:
            dtype = str(df[col].dtype)
            if 'int' in dtype or 'float' in dtype:
                info['numeric_columns'].append(col)
            elif 'object' in dtype or 'category' in dtype:
                info['categorical_columns'].append(col)
                # Check if it might be a date
                if 'date' in col.lower() or 'time' in col.lower():
                    info['date_columns'].append(col)
        
        # Get unique value counts for categorical columns (limited to first 10)
        info['unique_counts'] = {}
        for col in info['categorical_columns'][:10]:
            unique_count = df[col].nunique()
            info['unique_counts'][col] = {
                'count': unique_count,
                'sample_values': df[col].unique()[:5].tolist() if unique_count <= 20 else df[col].value_counts().head(5).index.tolist()
            }
        
        # Get basic stats for numeric columns
        info['numeric_stats'] = {}
        if len(info['numeric_columns']) > 0:
            numeric_df = df[info['numeric_columns']]
            info['numeric_stats'] = numeric_df.describe().to_dict()
        
        return info
    except Exception as e:
        return {
            'file_name': os.path.basename(file_path),
            'file_path': file_path,
            'error': str(e)
        }

def generate_report():
    """Generate comprehensive report on all Kaggle datasets."""
    base_path = Path("data/Kaggle Datasets")
    
    # Find all CSV files
    csv_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    print("=" * 80)
    print("KAGGLE DATASETS COMPREHENSIVE ANALYSIS REPORT")
    print("=" * 80)
    print(f"\nTotal CSV files found: {len(csv_files)}\n")
    
    all_analyses = {}
    
    # Analyze each file
    for file_path in sorted(csv_files):
        print(f"Analyzing: {file_path}...")
        analysis = analyze_csv_file(file_path)
        all_analyses[file_path] = analysis
    
    # Generate detailed report
    print("\n" + "=" * 80)
    print("DETAILED FILE ANALYSIS")
    print("=" * 80)
    
    for file_path, info in all_analyses.items():
        print(f"\n{'='*80}")
        print(f"FILE: {info['file_name']}")
        print(f"Path: {file_path}")
        print(f"{'='*80}")
        
        if 'error' in info:
            print(f"ERROR: {info['error']}")
            continue
        
        print(f"\n[ BASIC STATISTICS ]")
        print(f"  - Total Rows: {info['rows']:,}")
        print(f"  - Total Columns: {info['columns']}")
        print(f"  - Memory Usage: {info['memory_usage_mb']:.2f} MB")
        
        print(f"\n[ COLUMNS ({info['columns']} total) ]")
        for i, col in enumerate(info['column_names'], 1):
            dtype = info['dtypes'][col]
            null_count = info['null_counts'][col]
            null_pct = info['null_percentages'][col]
            null_str = f" ({null_count:,} null, {null_pct:.1f}%)" if null_count > 0 else ""
            print(f"  {i:2d}. {col:<40} {str(dtype):<15}{null_str}")
        
        if info['numeric_columns']:
            print(f"\n[ NUMERIC COLUMNS ({len(info['numeric_columns'])}) ]")
            for col in info['numeric_columns']:
                stats = info['numeric_stats'].get(col, {})
                if stats:
                    print(f"  - {col}:")
                    print(f"    Min: {stats.get('min', 'N/A')}")
                    print(f"    Max: {stats.get('max', 'N/A')}")
                    print(f"    Mean: {stats.get('mean', 'N/A'):.2f}" if 'mean' in stats else f"    Mean: N/A")
                    print(f"    Std: {stats.get('std', 'N/A'):.2f}" if 'std' in stats else f"    Std: N/A")
        
        if info['categorical_columns']:
            print(f"\n[ CATEGORICAL COLUMNS ({len(info['categorical_columns'])}) ]")
            for col in info['categorical_columns'][:10]:  # Limit to first 10
                if col in info['unique_counts']:
                    unique_info = info['unique_counts'][col]
                    print(f"  - {col}:")
                    print(f"    Unique Values: {unique_info['count']}")
                    if unique_info['count'] <= 20:
                        print(f"    Values: {unique_info['sample_values']}")
                    else:
                        print(f"    Top Values: {unique_info['sample_values']}")
        
        if info['date_columns']:
            print(f"\n[ DATE COLUMNS ]")
            for col in info['date_columns']:
                print(f"  - {col}")
        
        if info['sample_data']:
            print(f"\n[ SAMPLE DATA (First 3 rows) ]")
            for i, row in enumerate(info['sample_data'][:3], 1):
                print(f"  Row {i}:")
                for key, value in list(row.items())[:10]:  # Show first 10 columns
                    print(f"    {key}: {value}")
                if len(row) > 10:
                    print(f"    ... and {len(row) - 10} more columns")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    total_rows = sum(info.get('rows', 0) for info in all_analyses.values() if 'error' not in info)
    total_columns = sum(info.get('columns', 0) for info in all_analyses.values() if 'error' not in info)
    total_memory = sum(info.get('memory_usage_mb', 0) for info in all_analyses.values() if 'error' not in info)
    
    print(f"\n[ OVERALL SUMMARY ]")
    print(f"  - Total Files: {len(csv_files)}")
    print(f"  - Total Rows: {total_rows:,}")
    print(f"  - Total Columns: {total_columns}")
    print(f"  - Total Memory: {total_memory:.2f} MB")
    
    # Group by directory
    print(f"\n[ FILES BY DIRECTORY ]")
    basketball_files = [f for f in csv_files if 'Basketball' in f]
    csv_files_list = [f for f in csv_files if 'csv' in f and 'Basketball' not in f]
    
    print(f"\n  Basketball/ ({len(basketball_files)} files):")
    for f in basketball_files:
        info = all_analyses[f]
        rows = info.get('rows', 0) if 'error' not in info else 0
        print(f"    - {os.path.basename(f)}: {rows:,} rows")
    
    print(f"\n  csv/ ({len(csv_files_list)} files):")
    for f in csv_files_list:
        info = all_analyses[f]
        rows = info.get('rows', 0) if 'error' not in info else 0
        print(f"    - {os.path.basename(f)}: {rows:,} rows")
    
    print("\n" + "=" * 80)
    print("REPORT GENERATION COMPLETE")
    print("=" * 80)
    
    return all_analyses

if __name__ == "__main__":
    analyses = generate_report()

