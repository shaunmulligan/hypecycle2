# TODO:

- Add input buttons in a asyncio.to_thread() because adafruit lib is sync. Use threading.Event() to pass back button presses to main thread.
- Get battery voltage (%) using MCP2221's AnalogIn(board.G1)
- wrap icp1025.get_pressure() calls in a to_thread() to get highprecision altitude measurements and augment GPS altitude data.
- Figure out BLE reconnect logic
    - Periodically re-run scanner ??
- get first hrm and power sensor addresses from db before scanner
