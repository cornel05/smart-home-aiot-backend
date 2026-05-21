# YoloBit Hardware Interface

Sensor frame from board:

`TEMP:{float},HUM:{float},LIGHT:{number},IR:{number}`

Current backend/gateway command contract:

`{"device":"fan|light","action":"on|off","value":number?}` on `smarthome/commands`

Board-side serial actuator target:

`CMD:{device},{state}`

Known YoloFarm-proven output pins:

- pin10: relay/pump output via `yolobit.pin10.write_digital(0|1)`
- pin13: alternate relay/pump output via `yolobit.pin13.write_digital(0|1)`

YoloHome real fan/light pin mapping is provisional. Confirm wiring before final pin assignment.
