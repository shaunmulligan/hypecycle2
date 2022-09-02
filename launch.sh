# Create symlink to make working with i2c easier
sudo ln -s /dev/i2c-11 /dev/i2c-1

python -m uvicorn main:app --reload --workers 1 --host 0.0.0.0 --port 8001 --lifespan on