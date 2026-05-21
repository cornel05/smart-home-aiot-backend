# -*- coding: utf-8 -*-
from yolobit import pin10, pin13

DEVICE_PINS = {
    "fan": pin10,
    "light": pin13,
}

device_state = {
    "fan": 0,
    "light": 0,
}


def task_init():
    for device in DEVICE_PINS:
        set_device(device, 0)


def set_device(device, state):
    if device not in DEVICE_PINS:
        print("[ACTUATOR] unknown device:", device)
        return False
    value = 1 if int(state) else 0
    DEVICE_PINS[device].write_digital(value)
    device_state[device] = value
    print("[ACTUATOR] {}={}".format(device, value))
    return True
