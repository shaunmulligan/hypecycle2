
class Machine():

    def __init__(self, brightness=255, enableWifi=True):
        self._enableWifi = enableWifi
        self.brightness = brightness #call the function to actually set the value
    
    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, level):
        if not isinstance(level, int):
            raise TypeError
        if level <=255 and level >= 0:
            self._brightness = (255 - level) #flip level so that our range is from 0 - 255
            with open('/sys/waveshare/rpi_backlight/brightness', 'w') as f:
                f.write(str(self._brightness))
        else:
            raise ValueError('level needs to be an integer between 0 and 255')

    @brightness.deleter
    def brightness(self):
        del self._brightness

    @property
    def enableWifi(self):
        #TODO: check if wifi is enabled
        return self._enableWifi
    
    @enableWifi.setter
    def enableWifi(self, value):
        if isinstance(value, bool):
            self._enableWifi = value
            #TODO: enable wifi here and only set if successful
    
    @enableWifi.deleter
    def enableWifi(self):
        del self._enableWifi