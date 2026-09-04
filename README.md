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



### 12. Dockerize the application
Created two Dockerfiles in `dockerfiles/`, following the reference project's structure:

**`dockerfiles/backend.dockerfile`**
\`\`\`dockerfile
FROM python:3.13-slim
COPY backend/ /app/
RUN pip install --no-cache-dir uv
WORKDIR /app
RUN uv sync --no-dev
WORKDIR /app/src/backend
CMD [ "uv" , "run", "uvicorn", "api:app", "--host", "0.0.0.0"]
\`\`\`

**`dockerfiles/frontend.dockerfile`**
\`\`\`dockerfile
FROM python:3.13-slim
COPY frontend/ /app/
RUN pip install --no-cache-dir uv
WORKDIR /app
RUN uv sync --no-dev
WORKDIR /app/src/frontend
CMD [ "uv" , "run", "streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
\`\`\`

Fixed `DATA_PATH` in `constants.py` to be resolved relative to the file's own location (using `pathlib.Path(__file__)`) rather than the working directory, since the working directory differs between local runs and the container (`WORKDIR /app/src/backend`).

### 13. Docker Compose
Created a root-level `docker-compose.yaml` to build and run both services together, and to connect them for local testing:
\`\`\`yaml
services:
  backend:
    container_name: backend
    platform: linux/amd64
    build:
      context: .
      dockerfile: dockerfiles/backend.dockerfile
    ports:
      - "8000:8000"
    image: eclipsebordacrzineb-fncsbjcbcwdqeydc.azurecr.io/backend:v1

  frontend:
    container_name: frontend
    platform: linux/amd64
    build:
      context: .
      dockerfile: dockerfiles/frontend.dockerfile
    ports:
      - "8501:8501"
    environment:
      BACKEND_URL: http://backend:8000
    image: eclipsebordacrzineb-fncsbjcbcwdqeydc.azurecr.io/frontend:v1
\`\`\`

Updated `dashboard.py` to read `BACKEND_URL` from an environment variable, falling back to `localhost` for local (non-Docker) runs:
\`\`\`python
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
\`\`\`

Tested locally with:
\`\`\`bash
docker compose build
docker compose up
\`\`\`

### 14. Azure setup
Created the following Azure resources under a single resource group `eclipsebord-rg` (Azure for Students subscription):

- **Resource Group**: `eclipsebord-rg`
- **Azure Container Registry (ACR)**: `eclipsebordacrzineb` — stores the built Docker images
- **Container Apps Environment**: created in `Germany West Central` (the originally intended `Sweden Central` region hit a quota limit — `MaxNumberOfEnvironmentsInSubExceeded` — and `North Europe`/`West Europe` were blocked by the subscription's regional policy; checked the allowed region list via **Policy → Assignments → Allowed resource deployment regions**)
- **Backend**: deployed as an Azure **Container App** (`eclipsebord-container-app`), pulling the `backend:v1` image from ACR
- **Frontend**: deployed as an Azure **Web App for Containers** (`eclipsbord-fullstack`), pulling the `frontend:v1` image from ACR

### 15. Push images to ACR
\`\`\`bash
az login
az acr login --name eclipsebordacrzineb
docker compose build
docker compose push
\`\`\`

### 16. Configure environment variables
Set the following Application/Environment settings on the frontend Web App so it can reach the backend and Streamlit binds correctly:

| Name | Value |
|---|---|
| `BACKEND_URL` | `https://eclipsebord-container-app.salmoncliff-9981b840.germanywestcentral.azurecontainerapps.io` |
| `WEBSITES_PORT` | `8501` |
| `STREAMLIT_SERVER_PORT` | `8501` |
| `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` |

### 17. Troubleshooting the deployment
The frontend container kept restarting in a loop (visible in **Log Stream** as repeated `Stopping...` every few minutes, despite Streamlit starting successfully each time). Root cause: the container's **Port** setting (under Deployment Center → Containers → Edit container) was left at Azure's default `80`, while the app actually listens on `8501` (set via `WEBSITES_PORT`). Azure couldn't reach the app on port 80, considered it unresponsive, and kept recycling the container. Fixed by setting **Port = 8501** in the container configuration to match `WEBSITES_PORT`.

### 18. Live deployment
- **Frontend (dashboard)**: https://eclipsbord-fullstack-bha3degagkgzh6eh.germanywestcentral-01.azurewebsites.net
- **Backend (API docs)**: https://eclipsebord-container-app.salmoncliff-9981b840.germanywestcentral.azurecontainerapps.io/docs