import pandas as pd
from io import StringIO
from typing import Dict, Any, List

class CSVAnalysisService:
    @staticmethod
    def analyze_content(content: str) -> Dict[str, Any]:
        """
        Analyze CSV content and return summary statistics.
        """
        try:
            df = pd.read_csv(StringIO(content))
            return {
                "columns": df.columns.tolist(),
                "row_count": len(df),
                "summary": df.describe().to_dict(),
                "missing_values": df.isnull().sum().to_dict()
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_correlations(content: str) -> Dict[str, Any]:
        try:
            df = pd.read_csv(StringIO(content))
            # Filter only numeric columns for correlation
            numeric_df = df.select_dtypes(include=['number'])
            if numeric_df.empty:
                return {"error": "No numeric columns found for correlation"}
            return numeric_df.corr().to_dict()
        except Exception as e:
            return {"error": str(e)}
