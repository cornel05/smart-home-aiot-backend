import time


class DHT20:
    ADDRESS = 0x38

    def __init__(self, i2c, address=ADDRESS):
        self.i2c = i2c
        self.address = address
        self._temperature = None
        self._humidity = None
        self._init_sensor()

    def _init_sensor(self):
        time.sleep_ms(100)
        try:
            status = self.i2c.readfrom(self.address, 1)[0]
        except OSError:
            return
        if (status & 0x18) != 0x18:
            self.i2c.writeto(self.address, b"\xbe\x08\x00")
            time.sleep_ms(20)

    def read(self):
        self.i2c.writeto(self.address, b"\xac\x33\x00")
        time.sleep_ms(80)
        data = self.i2c.readfrom(self.address, 7)
        if data[0] & 0x80:
            raise OSError("DHT20 busy")

        raw_h = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
        raw_t = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]

        self._humidity = raw_h * 100.0 / 1048576
        self._temperature = raw_t * 200.0 / 1048576 - 50
        return self._temperature, self._humidity

    def temperature(self):
        return self._temperature

    def humidity(self):
        return self._humidity
