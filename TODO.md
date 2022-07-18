# TODO:

- Add input buttons in a asyncio.to_thread() because adafruit lib is sync. Use threading.Event() to pass back button presses to main thread. buttons: 
    - start/pause (start will create a ride if one isn't active and start data recording, pause will pause data recording)
    - stop (ends ride, saves data and presents summary page)
    - shutdown?
- Get battery voltage (%) using Pico
- Create recording task that will pull data from hypecycleState and write to gpx and db.
- Figure out BLE reconnect logic
    - Periodically re-run scanner ??
- get first hrm and power sensor addresses from db before scanner
