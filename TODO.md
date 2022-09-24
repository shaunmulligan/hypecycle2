# TODO:

- Create recording task that will pull data from hypecycleState and write to gpx and db.
- Figure out BLE reconnect logic
    - Periodically re-run scanner ??
    - can check list of connected devices using something like https://github.com/hbldh/bleak/issues/367#issuecomment-774980838 

# Setup Stuff:

- disable cursor: `sudo sed -i -- "s/#xserver-command=X/xserver-command=X -nocursor/" /etc/lightdm/lightdm.conf` 
