import time
from machine import ADC, Pin, SoftI2C

from dht20 import DHT20
from lcd_1602 import LCD1602

try:
    import task_actuators
except ImportError:
    task_actuators = None

try:
    import select
    import sys

    stdin_poll = select.poll()
    stdin_poll.register(sys.stdin, select.POLLIN)
except Exception:
    stdin_poll = None
    sys = None


# If I2C scan is empty, try (19, 20), then (22, 21), then swap SDA/SCL.
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
LDR_ADC_PIN = 2
IR_PIN = 1
LCD_ADDR = 0x21
SAMPLE_SECONDS = 5


try:
    from yolobit import pin1 as yolo_pin1, pin2 as yolo_pin2
except ImportError:
    yolo_pin1 = None
    yolo_pin2 = None


def make_i2c():
    return SoftI2C(scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=100000)


def make_adc(pin_no):
    adc = ADC(Pin(pin_no))
    try:
        adc.atten(ADC.ATTN_11DB)
    except AttributeError:
        pass
    return adc


def read_light(adc):
    if yolo_pin2:
        return yolo_pin2.read_analog()
    try:
        return adc.read()
    except AttributeError:
        return adc.read_u16() >> 4


def read_ir(pin):
    if yolo_pin1:
        return yolo_pin1.read_digital()
    return pin.value()


def fit16(text):
    return str(text)[:16].ljust(16)


def handle_serial_command(line):
    if not line.startswith("CMD:"):
        return False
    if not task_actuators:
        return False

    parts = line[4:].split(",")
    if len(parts) != 2:
        return False

    try:
        state = int(parts[1])
    except ValueError:
        return False

    return task_actuators.set_device(parts[0], state)


def poll_serial_command():
    if not stdin_poll or not sys:
        return

    try:
        if stdin_poll.poll(0):
            line = sys.stdin.readline().strip()
            if line:
                handle_serial_command(line)
    except Exception as exc:
        print("CMD_ERROR:{}".format(exc))


i2c = make_i2c()
print("I2C_SCAN:{}".format(i2c.scan()))

dht = DHT20(i2c)
lcd = None
try:
    lcd = LCD1602(i2c, addr=LCD_ADDR)
    lcd.backlight_on()
    lcd.move_to(0, 0)
    lcd.putstr("SmartHome ready")
except OSError as exc:
    print("LCD_ERROR:{}".format(exc))

light_adc = make_adc(LDR_ADC_PIN)
ir_pin = Pin(IR_PIN, Pin.IN)
if task_actuators:
    try:
        task_actuators.task_init()
    except Exception as exc:
        print("ACTUATOR_ERROR:{}".format(exc))

while True:
    poll_serial_command()

    try:
        temp, hum = dht.read()
    except OSError as exc:
        print("DHT20_ERROR:{}".format(exc))
        temp = -99.0
        hum = -1.0

    light = read_light(light_adc)
    ir = read_ir(ir_pin)
    frame = "TEMP:{:.1f},HUM:{:.1f},LIGHT:{},IR:{}".format(temp, hum, light, ir)
    print(frame)

    if lcd:
        try:
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr(fit16("T:{:.1f}C H:{:.0f}%".format(temp, hum)))
            lcd.move_to(0, 1)
            lcd.putstr(fit16("L:{} IR:{}".format(light, ir)))
        except OSError as exc:
            print("LCD_ERROR:{}".format(exc))
            lcd = None

    time.sleep(SAMPLE_SECONDS)
