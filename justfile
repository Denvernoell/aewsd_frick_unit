# Run the local Streamlit app (equivalent to local.sh)

local:
    cd "/c/1-Projects/aewsd_frick_unit/app" && \
    uv run --project "/c/3-Resources/envs/fh_online" app.py
reqs:
    env="/c/3-Resources/envs/fh_online" && \
    uv export --project "$env" > ./railway/requirements.txt && \
    uv lock --project "$env" && \
    cp "$env/uv.lock" ./railway/uv.lock && \
    cp "$env/pyproject.toml" ./railway/pyproject.toml
