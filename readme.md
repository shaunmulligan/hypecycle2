# Proposed HypeCycle Feature Set:

- Crisp high density 4” touch screen: 800x480 pixels (~235 PPI) Hyperpixel
- Bluetooth sensor compatibility (HR and Power)
- Front facing Camera with ability to record
- Fast fix (possibly assisted-GPS) or at least coincell 
- Automatic upload to strava when in wifi
- High accuracy altimeter and ambient temperature
- Controllable Front facing LED lights for visibility
- Quadcore rpi zero 2 W at its heart
- 3700mah high capacity Lipo battery
- 100% opensource
- 3 physical buttons
- Integrated into bar mount

maybes:
- Wireless charging
- Haptic buzzer you can feel in the handlebars
- Ability to bluetooth tether to phone for internet access.

# Install:

To setup a Raspberry Pi OS device follow the install instructions in [docs/installing.md]

# Usage:

For development run the following:
1. Start the frontend server with hot reload: `cd hypecycle-frontend && npm run dev`
2. Start the backend service `cd hypecycle2 && ./launch.sh`
3. Start the webkit webview pointing at the frontend instance `DISPLAY=:0 ./hc-browser  http://localhost:5173/`
4. You can also access all the backend API endpoint swagger docs via `<YOUR_DEVICE_IP>:8001/docs#/`