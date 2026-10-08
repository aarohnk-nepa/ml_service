uv add psycopg2-binary
uv sync
source .venv/bin/activate
python -m ipykernel install --user --name=ml_service --display-name "ml_service" \
  $(grep -v '^#' .env | grep -v '^$' | sed 's/=/ /' | awk '{print "--env "$1" "$2}')