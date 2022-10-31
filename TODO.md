# TODO:
- Figure out better method to keep track of distance
    - Maybe can store a distance difference between two adjacent points and then add them all up?
- Figure out BLE reconnect logic
    - Periodically re-run scanner ??
    - can check list of connected devices using something like https://github.com/hbldh/bleak/issues/367#issuecomment-774980838 

# Setup Stuff:

- disable cursor: `sudo sed -i -- "s/#xserver-command=X/xserver-command=X -nocursor/" /etc/lightdm/lightdm.conf` 
- run browser:  `DISPLAY=:0 ./hc-browser  http://localhost:5173/`