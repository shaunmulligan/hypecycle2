# TODO:

- add BleScanner class to scan before connection like two_hrm_test.py example
- add @backoff.on_exception(backoff.constant, bleak.exc.BleakError, interval=5) to retry connection when exceptions are thrown. https://pypi.org/project/backoff/
- Add ble disconnect handler and link to asyncio.Event() to notify
- Periodically re-run scanner ??
- get first hrm and power sensor addresses from db before scanner
- Add input buttons in a asyncio.to_thread() because adafruit lib is sync. Use threading.Event() to pass back button presses to main thread.
- extract speed and altitude from NMEA senstences http://aprs.gids.nl/nmea/#gga 
- wrap icp1025.get_pressure() calls in a to_thread() to get highprecision altitude measurements and augment GPS altitude data.