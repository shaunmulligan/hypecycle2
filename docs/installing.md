-  the config.txt should be as follows:
```
#Overclock 1350

arm_freq=1200
initial_turbo=45

# Enable audio (loads snd_bcm2835)
dtparam=audio=on

# Automatically load overlays for detected cameras
camera_auto_detect=1

# Automatically load overlays for detected DSI displays
display_auto_detect=1

# Enable DRM VC4 V3D driver
dtoverlay=vc4-kms-v3d
max_framebuffers=2

# Disable compensation for displays with overscan
disable_overscan=1

[all]

[pi4]

# Run as fast as firmware / board allows
arm_boost=1

[all]

dtoverlay=vc4-kms-dpi-hyperpixel4
gpu_mem=32
```

- Need to install zram to allow browser stuff to run well with low RAM on the pi zero. Follow this https://haydenjames.io/raspberry-pi-performance-add-zram-kernel-parameters/
- Switch to network-manager:
	- `sudo apt install network-manager`
	- `sudo raspi-config` and then go to the “`6 Advanced Options`”
- install nodejs (development only)
```
sudo su
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
sudo apt install nodejs
```
- Install deps and build frontend:
```
cd hypecycle-frontend 
npm install
npm run build:client
```
- Install rust (build/development only)
```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# install missing glib dep
sudo apt-get install libwebkit2gtk-4.0-dev libglib2.0-dev build-essential libgtk-3-dev javascriptcoregtk-4.0 libsoup2.4-dev
```
- Using a rust project called WRY as the browser window, this needs to be build as a binary on a RPI4, because the build fails on the pizero, there is not enough ram to finish. Run `cargo build --release` from with in `/hypecycle-browser`. This is only buildable on a RPI4 with about 4GB ram. This will take a while!!
-  install lighttpd (`sudo apt install lighttpd`)  and configure it to point to the /dist/client folder in hypercycle-frontend `sudo nano /etc/lighttpd/lighttpd.conf` and then start the service with `sudo service lighttpd start`
- Install the python3 backend:
	1. `cd hypecycle2 && pip install -r requirements.txt`
	2. Intialize the DB: `python model/db.py`
	3. start backend with `./launch.sh`