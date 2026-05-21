# Yolo:Bit Firmware

Upload these files to the Yolo:Bit root filesystem:

- `main.py`
- `dht20.py`
- `lcd_1602.py`
- `task_actuators.py` (optional actuator outputs)

Expected serial output:

```text
TEMP:25.3,HUM:61.5,LIGHT:430,IR:0
```

Expected command input from the gateway:

```text
CMD:{device},{state}
```

Current provisional actuator pins are `fan` on pin 10 and `light` on pin 13.

## Wiring

```text
DHT20   -> I2C port
LCD1602 -> I2C port
LDR     -> P2
IR/PIR  -> P1
```

The code uses `SoftI2C(scl=Pin(22), sda=Pin(21))` by default. If `I2C_SCAN:[]`
prints, edit `main.py` and try these pairs:

```python
I2C_SCL_PIN = 19
I2C_SDA_PIN = 20
```

If still empty, try swapped pairs:

```python
I2C_SCL_PIN = 20
I2C_SDA_PIN = 19
```

```python
I2C_SCL_PIN = 21
I2C_SDA_PIN = 22
```

## Pymakr Upload

1. Open VS Code.
2. Open `firmware/yolobit/yolobit.code-workspace`.
3. Connect Yolo:Bit USB.
4. In Pymakr, select `/dev/ttyUSB0`.
5. Stop running code with `Ctrl+C` in Pymakr terminal.
6. Upload project to device.
7. Reset board.
8. Open Pymakr terminal and confirm `I2C_SCAN` contains:

```text
56
```

`56` is DHT20 (`0x38`). LCD is usually `33` (`0x21`), `39` (`0x27`), or `63` (`0x3f`).

If LCD address is not `33`, update:

```python
LCD_ADDR = 0x27
```

or:

```python
LCD_ADDR = 0x3f
```
