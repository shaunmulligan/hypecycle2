import asyncio

class Machine():

    def __init__(self, brightness=255, wifi=True):
        self._wifi = wifi
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
    def wifi(self):
        return self._wifi

    async def wifiEnable(self):
        stdO, stdE = await self._run("rfkill unblock wifi")
        if stdE:
            print(f'[stderr]\n{stdE.decode()}')
        else:
            self._wifi = True
    
    async def wifiDisable(self):
        stdO, stdE = await self._run("rfkill block wifi")
        if stdE:
            print(f'[stderr]\n{stdE.decode()}')
        else:
            self._wifi = False

    async def _run(self, cmd: str):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stderr=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        print(f'[{cmd!r} exited with {proc.returncode}]')
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')
        return stdout, stderr

async def main() -> None:
    m = Machine(100,True)
    await m.wifiDisable()
    await asyncio.sleep(30)
    await m.wifiEnable()

if __name__ == "__main__":
    asyncio.run(main())