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

    @staticmethod
    def analyze_galamsay(
        content: str,
        city_column: str = "city",
        region_column: str = "region",
        sites_column: str = "sites",
        threshold: int = 10,
    ) -> Dict[str, Any]:
        try:
            try:
                df = pd.read_csv(StringIO(content))
            except Exception:
                df = pd.read_csv(StringIO(content), engine="python")

            original_columns = {c.lower().strip(): c for c in df.columns}

            def resolve(col_name: str):
                return original_columns.get(col_name.lower().strip())

            city_col = resolve(city_column)
            region_col = resolve(region_column)
            sites_col = resolve(sites_column)

            if not sites_col:
                return {"error": f"Required column '{sites_column}' not found"}

            sites_series = pd.to_numeric(df[sites_col], errors="coerce").fillna(0)
            sites_series = sites_series.mask(sites_series < 0, 0)
            df[sites_col] = sites_series

            total_sites = int(df[sites_col].sum())

            region_with_highest_sites = None
            if region_col:
                region_totals = df.groupby(region_col)[sites_col].sum()
                if not region_totals.empty:
                    top_region = region_totals.idxmax()
                    region_with_highest_sites = {
                        "region": None if pd.isna(top_region) else str(top_region),
                        "sites": int(region_totals.loc[top_region]) if not pd.isna(top_region) else 0,
                    }

            cities_exceeding_threshold = []
            if city_col:
                per_city = df.groupby(city_col)[sites_col].sum()
                exceeding = per_city[per_city > threshold].sort_values(ascending=False)
                cities_exceeding_threshold = [
                    {"city": None if pd.isna(name) else str(name), "sites": int(val)}
                    for name, val in exceeding.items()
                ]

            average_sites_per_region = {}
            if region_col:
                if city_col:
                    per_city_region = df.groupby([region_col, city_col])[sites_col].sum().reset_index()
                    avg_series = per_city_region.groupby(region_col)[sites_col].mean()
                else:
                    avg_series = df.groupby(region_col)[sites_col].mean()
                average_sites_per_region = {(
                    None if pd.isna(k) else str(k)
                ): float(v) for k, v in avg_series.items()}

            return {
                "total_sites": total_sites,
                "region_with_highest_sites": region_with_highest_sites,
                "cities_exceeding_threshold": cities_exceeding_threshold,
                "average_sites_per_region": average_sites_per_region,
            }
        except Exception as e:
            return {"error": str(e)}
