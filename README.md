# Sarvm.ai FastAPI Backend

This project is now powered by FastAPI and Uvicorn.

## Running Locally

```sh
pip install -r requirements.txt
uvicorn main:app --reload
```

## Render Deployment

- **Build Command:**
  ```sh
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```sh
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

## Features
- File upload
- Result display
- Static file serving

## Project Structure
- `main.py` — FastAPI app
- `boarding/static/boarding/` — Static files
- `boarding/templates/boarding/` — Jinja2 templates
- `sample_data/` — Example CSV files 