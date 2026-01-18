# OFWA Dashly

A FastAPI-based dashboard application for analyzing CSV datasets using generic statistical methods.

## Structure

- **dependencies/**: Authentication and authorization helpers.
  - `authh.py`: JWT handling and password hashing.
  - `authz.py`: Role-based access control.
- **routes/**: API endpoints.
  - `users.py`: User management.
  - `health.py`: Service health check.
  - `datasets.py`: Dataset upload and management.
  - `analysis.py`: Data analysis operations.
- **services/**: Business logic and external services.
  - `csv_analysis_service.py`: Pandas-based CSV analysis.
  - `cloudinary_service.py`: Cloudinary file upload integration.
  - `analysis_logger.py`: Logging utility.
- **models/**: Pydantic models for data validation.
- **tests/**: Unit and integration tests.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env`:

   - `MONGO_URI`
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
   - `JWT_SECRET_KEY`

3. Run the application:
   ```bash
   fastapi dev main.py
   ```

## Testing

Run tests with pytest:

```bash
pytest
```
