# Proposed HypeCycle Feature Set:

- Crisp high density 4” touch screen: 800x480 pixels (~235 PPI) Hyperpixel
- Bluetooth sensor compatibility (HR and Power)
- Front facing Camera with ability to record
- Fast fix (possibly assisted-GPS) or at least coincell 
- Automatic upload to strava when in wifi
- High accuracy altimeter and ambient temperature
- Controllable Front facing LED lights for visibility
- Quadcore rpi zero 2 W at its heart
- 1200mah high capacity Lipo battery
- 100% opensource
- 3 physical buttons
- Integrated into bar mount

maybes:
- Wireless charging
- Haptic buzzer you can feel in the handlebars
- Ability to bluetooth tether to phone for internet access.

Current Design:
- Uses pimoroni io-expander to read battery level and button presses, potentially will drive PWM and LEDs? Connected via i2c
- BMP388 to messure altitude using pressure. Also gives us temp. Connected to the i2c on the screen.
- Using Adafruit miniGPS connected via i2c

