export BLINKA_MCP2221="1"

uvicorn main:app --reload --workers 1 --host 0.0.0.0 --port 8001 --lifespan on