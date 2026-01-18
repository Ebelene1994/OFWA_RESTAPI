from typing import Any, Dict, Optional
from fastapi import HTTPException, status

CSV_EXTENSIONS = (".csv",)
EXCEL_EXTENSIONS = (".xlsx", ".xls")
JSON_EXTENSIONS = (".json",)
DATASET_ALLOWED_EXTENSIONS = CSV_EXTENSIONS + EXCEL_EXTENSIONS + JSON_EXTENSIONS

CSV_MIME_TYPES = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "text/plain",
}

DEFAULT_GALAMSAY_THRESHOLD = 10
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


def replace_mongo_id(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


def is_csv_filename(filename: str) -> bool:
    return filename.lower().endswith(CSV_EXTENSIONS)


def is_csv_mime_type(content_type: Optional[str]) -> bool:
    return bool(content_type) and content_type.lower() in CSV_MIME_TYPES


def validate_csv(filename: str, content_type: Optional[str] = None) -> None:
    if not is_csv_filename(filename):
        raise ValueError("Only CSV files are allowed")
    if content_type and not is_csv_mime_type(content_type):
        raise ValueError("Invalid CSV content type")


def api_success(message: str, data: Optional[Dict[str, Any]] = None, **meta) -> Dict[str, Any]:
    resp: Dict[str, Any] = {"success": True, "message": message}
    if data is not None:
        resp["data"] = data
    if meta:
        resp["meta"] = meta
    return resp


def api_error(message: str, code: Optional[str] = None, errors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    resp: Dict[str, Any] = {"success": False, "message": message}
    if code:
        resp["code"] = code
    if errors:
        resp["errors"] = errors
    return resp


def raise_http_error(
    message: str,
    http_status_code: int = status.HTTP_400_BAD_REQUEST,
    code: Optional[str] = None,
    errors: Optional[Dict[str, Any]] = None,
) -> None:
    detail = api_error(message=message, code=code, errors=errors)
    raise HTTPException(status_code=http_status_code, detail=detail)


def format_exception(exc: Exception, context: Optional[str] = None) -> str:
    base = f"{exc.__class__.__name__}: {str(exc)}"
    return f"{context} | {base}" if context else base


def error_detail(exc: Exception, context: Optional[str] = None) -> Dict[str, Any]:
    detail: Dict[str, Any] = {"type": exc.__class__.__name__, "message": str(exc)}
    if context:
        detail["context"] = context
    return detail
