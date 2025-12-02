"""
Helper script to set up the XGBoost model for the backend.
Run this after downloading the model from Kaggle.
"""
import shutil
from pathlib import Path
from src.config import MODEL_ARTIFACTS_DIR

def setup_model(model_file_path: str = None):
    """
    Set up the XGBoost model for the backend.
    
    Args:
        model_file_path: Path to the downloaded xgboost_nba_model.pkl file.
                        If None, prompts user for path.
    """
    if model_file_path is None:
        print("=" * 70)
        print("XGBoost Model Setup")
        print("=" * 70)
        print("\nPlease provide the path to your downloaded model file.")
        print("The file should be named 'xgboost_nba_model.pkl'")
        print("\nExample paths:")
        print("  - Windows: C:\\Users\\YourName\\Downloads\\xgboost_nba_model.pkl")
        print("  - Mac/Linux: ~/Downloads/xgboost_nba_model.pkl")
        print()
        model_file_path = input("Enter model file path: ").strip().strip('"').strip("'")
    
    # Convert to Path object
    source_path = Path(model_file_path)
    
    if not source_path.exists():
        print(f"\n❌ Error: File not found at {source_path}")
        print("Please check the path and try again.")
        return False
    
    # Destination path
    dest_path = MODEL_ARTIFACTS_DIR / "xgboost_nba_model.pkl"
    
    # Copy file
    try:
        shutil.copy2(source_path, dest_path)
        file_size = dest_path.stat().st_size / (1024 * 1024)  # Size in MB
        print(f"\n✅ Model copied successfully!")
        print(f"   Source: {source_path}")
        print(f"   Destination: {dest_path}")
        print(f"   File size: {file_size:.2f} MB")
        print(f"\n🎉 Model is ready to use!")
        print(f"   The backend will automatically load it when making predictions.")
        return True
    except Exception as e:
        print(f"\n❌ Error copying file: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    else:
        model_path = None
    
    setup_model(model_path)

