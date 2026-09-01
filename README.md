# eClipseBord_mouhib_DE25
## Project Setup

This project uses a **uv workspace** to manage the backend (FastAPI) and frontend (Streamlit) as separate packages within a single repository.

### 1. Create the folder structure
\`\`\`bash
mkdir backend frontend dockerfiles
\`\`\`

### 2. Initialize the root workspace
\`\`\`bash
uv init --name eclipsebord
\`\`\`
This created the root `pyproject.toml`, `.python-version`, and a placeholder `main.py` (removed, since app code lives in `backend/` and `frontend/`).

\`\`\`bash
rm main.py
\`\`\`

### 3. Declare the workspace members
Added the following to the root `pyproject.toml`:
\`\`\`toml
[tool.uv.workspace]
members = [
    "backend",
    "frontend",
]
\`\`\`

### 4. Initialize backend and frontend as workspace members
\`\`\`bash
cd backend && uv init --name backend --package --no-workspace
cd ../frontend && uv init --name frontend --package --no-workspace
\`\`\`
The `--package` flag creates an installable package structure (`src/<name>/`). `--no-workspace` was needed because `uv init` otherwise tries to validate the whole workspace before all members exist yet.

### 5. Sync the workspace
\`\`\`bash
cd ..
uv sync
\`\`\`
This resolved and locked dependencies for both packages into a single root `uv.lock`.





### 6. Set up EDA
Created a `notebook/` folder in the root (kept separate from `backend/` and `frontend/` so it isn't included in the Docker images) with `EDA.ipynb` for initial data exploration.

Added `pandas` and `ipykernel` to the root workspace:
\`\`\`bash
uv add pandas
uv add --dev ipykernel
\`\`\`

### 7. Data
Placed the dataset(s) in a root-level `data/` folder, shared between the EDA notebook and the backend. Used a `DATA_PATH` variable to reference the files consistently:
\`\`\`python
DATA_PATH = "../data"
df = pd.read_csv(f"{DATA_PATH}/<filename>.csv")
\`\`\`


### 8. Restructure to match project conventions
Initially placed the dataset in a shared root-level `data/` folder. After reviewing the 
reference structure, moved it into `backend/data/` so it's included when the backend 
Docker image is built later. The EDA notebook remains in the root-level `notebook/` 
folder, kept separate so it isn't shipped inside the container.

### 9. Build the FastAPI backend
Restructured `backend/src/backend/` into three files, following the reference project's 
convention of separating concerns:
- **`constants.py`** — holds `DATA_PATH`
- **`data_processing.py`** — functions `load_lunar_data()` and `load_solar_data()` that 
  read the CSV files into DataFrames
- **`api.py`** — the FastAPI app and all endpoints, importing data-loading functions from 
  `data_processing.py`

Installed backend dependencies:
\`\`\`bash
cd backend
uv add fastapi uvicorn pandas
\`\`\`

### 10. API endpoints
| Endpoint | Description |
|---|---|
| `GET /` | Health check — confirms the API is running |
| `GET /eclipses/{eclipse_type}` | Returns all records for `lunar` or `solar` |
| `GET /eclipses/{eclipse_type}/filter?year=&type_filter=` | Filters by year and/or eclipse type |
| `GET /eclipses/{eclipse_type}/map` | Returns date, type, and coordinates — for map visualization |
| `GET /eclipses/{eclipse_type}/stats` | Returns counts per eclipse type |

### 11. Running the backend locally
\`\`\`bash
cd backend
uv run uvicorn src.backend.api:app --reload
\`\`\`
Visit `http://127.0.0.1:8000/docs` for interactive API documentation, or 
`http://127.0.0.1:8000/eclipses/lunar` directly to see raw data (note: very large 
responses may not render properly inside the Swagger UI viewer itself, but work fine 
when accessed directly or via `curl`).