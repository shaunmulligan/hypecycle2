# Create symlink to make working with i2c easier
FILE=/dev/i2c-1
FILE2=/dev/i2c-11
if ! [ -L $FILE ]; then
    echo "No $FILE found, creating symlink"
    if ! [ -L $FILE2 ]; then
        echo "No i2c-11 found, trying i2c-22"
        sudo ln -s /dev/i2c-11 /dev/i2c-1
    else
        sudo ln -s /dev/i2c-11 /dev/i2c-1
    fi
else
    echo "$FILE exists."
fi

# Clear BLE devices cache before start
sudo rm -rf /var/lib/bluetooth/B8:27:EB:79:D0:BF/cache

python -m uvicorn main:app --workers 1 --host 0.0.0.0 --port 8001 --lifespan on  #--reload