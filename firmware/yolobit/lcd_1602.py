import time


class LCD1602:
    ENABLE = 0x04
    BACKLIGHT = 0x08

    def __init__(self, i2c, addr=0x21, cols=16, rows=2):
        self.i2c = i2c
        self.addr = addr
        self.cols = cols
        self.rows = rows
        self.backlight = self.BACKLIGHT
        time.sleep_ms(50)
        for value in (0x03, 0x03, 0x03, 0x02):
            self._write4(value << 4)
            time.sleep_ms(5)
        self._command(0x28)
        self._command(0x0C)
        self._command(0x06)
        self.clear()

    def _write_raw(self, value):
        self.i2c.writeto(self.addr, bytes([value | self.backlight]))

    def _pulse(self, value):
        self._write_raw(value | self.ENABLE)
        time.sleep_us(1)
        self._write_raw(value & ~self.ENABLE)
        time.sleep_us(50)

    def _write4(self, value):
        self._write_raw(value)
        self._pulse(value)

    def _send(self, value, mode=0):
        self._write4((value & 0xF0) | mode)
        self._write4(((value << 4) & 0xF0) | mode)

    def _command(self, value):
        self._send(value, 0)

    def clear(self):
        self._command(0x01)
        time.sleep_ms(2)

    def move_to(self, col, row):
        row_offsets = (0x00, 0x40)
        self._command(0x80 | (col + row_offsets[row]))

    def putstr(self, text):
        for char in text:
            self._send(ord(char), 1)

    def backlight_on(self):
        self.backlight = self.BACKLIGHT
        self._write_raw(0)

    def backlight_off(self):
        self.backlight = 0
        self._write_raw(0)
