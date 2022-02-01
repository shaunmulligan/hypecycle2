import asyncio
import serial_asyncio
import pathlib
import datetime

class Gps(object):
    """ class for USB GPS Receiver. """

    def __init__(self, state):
        """ """
        self.state = state
        self.is_gps_quality_ok = False
        self.asyncio_loop = None

    async def start(self):
        """ """
        self.asyncio_loop = asyncio.get_event_loop()
        # Check if USB GPS is connected.
        gps_device_path_found = None
        for gps_device_path in ["/dev/ttyACM1", "/dev/ttyUSB0", "/dev/cu.usbmodem101"]:
            gps_device = pathlib.Path(gps_device_path)
            if gps_device.exists():
                gps_device_path_found = gps_device_path
                break
        # Read serial, if connected.
        if gps_device_path_found:
            self.serial_coro = serial_asyncio.create_serial_connection(
                self.asyncio_loop,
                ReadGpsSerialNmea,
                gps_device_path_found,  # For example "/dev/ttyACM0".
                baudrate=9600,  # 9600, 19200, 38400
            )
            # Start. Serial_protocol is instance of ReadGpsSerialNmea
            self.serial_transport, self.serial_protocol = await self.serial_coro
            # To be used for calls back to master.
            self.serial_protocol.gps_manager = self
        else:
            # GPS device not found.
            self.is_gps_quality_ok = False
            self.last_used_lat_dd = 0.0
            self.last_used_long_dd = 0.0

    async def stop(self):
        """ """
        if self.serial_coro:
            if self.serial_transport:
                self.serial_transport.close()

    def parse_nmea(self, data):
        """ 
        From NMEA documentation:

        RMC - NMEA has its own version of essential gps pvt 
        (position, velocity, time) data. It is called RMC, 
        The Recommended Minimum, which will look similar to:
        $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
        Where:
            RMC          Recommended Minimum sentence C
            123519       Fix taken at 12:35:19 UTC
            A            Status A=active or V=Void.
            4807.038,N   Latitude 48 deg 07.038' N
            01131.000,E  Longitude 11 deg 31.000' E
            022.4        Speed over the ground in knots
            084.4        Track angle in degrees True
            230394       Date - 23rd of March 1994
            003.1,W      Magnetic Variation
            *6A          The checksum data, always begins with *

        Example from test (Navilock NL-602U):
            $GPRMC,181841.000,A,5739.7158,N,01238.3515,E,0.52,289.92,040620,,,A*6D
        """
        parts = data.split(",")
        # print("Used NMEA: ", data)

        # GPGGA. Check quality.
        if (len(parts) >= 8) and (len(parts[0]) >= 6) and (parts[0][3:6] == "GGA"):
            if parts[6] == "0":
                # Fix quality 0 = invalid.
                self.is_gps_quality_ok = False
                return
            number_of_satellites = parts[7]
            if int(number_of_satellites) < 3:
                # More satellites needed.
                self.is_gps_quality_ok = False
                return
            # Seems to be ok.
            self.is_gps_quality_ok = True
            self.state.gps_altitude = parts[9]
            print("")
            print("GPS fix: ", self.is_gps_quality_ok)
            print("GPS Altitude: ", self.state.gps_altitude)
            print("")
            return

        # GPRMC. Get date, time and lat/long.
        if (len(parts) >= 8) and (len(parts[0]) >= 6) and (parts[0][3:6] == "RMC"):
            if self.is_gps_quality_ok == False:
                return

            latitude_dd = 0.0
            longitude_dd = 0.0

            if (len(data) >= 50) and (len(parts) >= 8):
                time = parts[1]
                _gps_status = parts[2]
                latitude = parts[3]
                lat_n_s = parts[4]
                longitude = parts[5]
                long_w_e = parts[6]
                speed_knots = parts[7]
                date = parts[9]
            else:
                self.last_used_lat_dd = 0.0
                self.last_used_long_dd = 0.0
                return

            # Extract date and time.
            datetime_utc = datetime.datetime(
                int("20" + date[4:6]),
                int(date[2:4]),
                int(date[0:2]),
                int(time[0:2]),
                int(time[2:4]),
                int(time[4:6]),
            )
            # Extract latitude and longitude.
            latitude_dd = round(
                float(latitude[0:2]) + (float(latitude[2:].strip()) / 60.0), 5
            )
            if lat_n_s == "S":
                latitude_dd *= -1.0
            longitude_dd = round(
                float(longitude[0:3]) + (float(longitude[3:].strip()) / 60.0), 5
            )
            if long_w_e == "W":
                longitude_dd *= -1.0

            self.gps_datetime_utc = datetime_utc
            self.gps_latitude = latitude_dd
            self.gps_longitude = longitude_dd

            print("")
            print("GPS datetime: ", datetime_utc)
            print("GPS latitude: ", latitude_dd)
            print("GPS longitude: ", longitude_dd)
            print("")
            self.state.location = {
                "latitude": latitude_dd,
                "longitude": longitude_dd,
                "gps_time": datetime_utc
            }
            self.state.speed = float(speed_knots) * 1.852 if speed_knots is not None else 0
            print("GPS speed: ", self.state.speed, " km/h")

class ReadGpsSerialNmea(asyncio.Protocol):
    """ Serial connection for serial_asyncio. """

    def __init__(self):
        """ """
        super().__init__()
        self.buf = bytes()
        self.gps_manager = None

    def connection_made(self, transport):
        transport.serial.rts = False
        # self.gps_manager: GPS manager for callbacks will be set externally.
        print("GPS: Connection made.")

    def data_received(self, data):
        try:
            # print("Data: ", data)
            # Avoid problems with data streams without new lines.
            if len(self.buf) >= 1000:
                self.buf = bytes()
            #
            self.buf += data
            if b"\n" in self.buf:
                rows = self.buf.split(b"\n")
                self.buf = rows[-1]  # Save remaining part.
                for row in rows[:-1]:
                    row = row.decode().strip()

                    # print("Received row: ", row)

                    if (row.find("RMC,") > 0) or (row.find("GGA,") > 0):
                        # print("NMEA: ", row)
                        if self.gps_manager:
                            self.gps_manager.parse_nmea(row)
        except Exception as e:
            # Logging debug.
            message = "EXCEPTION in GPS:ReadGpsSerialNmea:data_received: " + str(e)
            print(message)

    def connection_lost(self, exc):
        pass


# === MAIN - for test ===
async def main():
    """ """
    print("Test started.")
    hypecycleState = type('', (), {})()
    gps_test = Gps(hypecycleState)
    await gps_test.start()
    await asyncio.sleep(60.0)
    await gps_test.stop()
    print("Test finished.")


if __name__ == "__main__":
    """ """
    asyncio.run(main(), debug=True)