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