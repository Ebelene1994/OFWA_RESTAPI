from datetime import datetime, timezone
from typing import Any, Dict, Optional

from db import ofwa_dash_db


analysis_logs_collection = ofwa_dash_db["analysis_logs"]


class AnalysisLogger:
    def __init__(self):
        self.collection = analysis_logs_collection

    async def log_success(
        self,
        *,
        analysis_id: str,
        dataset_id: str,
        analyst_user_id: str,
        parameters: Dict[str, Any],
        results: Dict[str, Any],
    ) -> str:
        doc = {
            "analysis_id": analysis_id,
            "dataset_id": dataset_id,
            "analyst_user_id": analyst_user_id,
            "parameters": parameters,
            "results": results,
            "executed_at": datetime.now(timezone.utc),
            "status": "success",
        }
        res = await self.collection.insert_one(doc)
        return str(res.inserted_id)

    async def log_failure(
        self,
        *,
        analysis_id: str,
        dataset_id: str,
        analyst_user_id: str,
        parameters: Dict[str, Any],
        error: str,
        results: Optional[Dict[str, Any]] = None,
    ) -> str:
        doc = {
            "analysis_id": analysis_id,
            "dataset_id": dataset_id,
            "analyst_user_id": analyst_user_id,
            "parameters": parameters,
            "results": results,
            "error": error,
            "executed_at": datetime.now(timezone.utc),
            "status": "failure",
        }
        res = await self.collection.insert_one(doc)
        return str(res.inserted_id)

    async def get_by_analysis_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"analysis_id": analysis_id})

    async def update_log(self, *args, **kwargs):  # noqa: D401
        raise RuntimeError("Analysis logs are immutable and cannot be updated.")

    async def delete_log(self, *args, **kwargs):  # noqa: D401
        raise RuntimeError("Analysis logs are immutable and cannot be deleted.")


analysis_logger = AnalysisLogger()
