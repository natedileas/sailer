
## com+cam

idea; combine communication and camera at top of mast so that images do not have to travel by i2c or can or uart. 

    nav lights?

## main board 

lives in the gut.
 uart interface to comm/cam 
 wind spd(1 pins, interrupt / digital counter) 
 wind dir (1 pin, ADC), 
 attitude (i2c) 
 setting motor values (i2c). 
 battery i2c? 
 relays for motors? 1 pin per
 relay for comm/cam? 1 pin per
 nav lights?

## motor controller board
    communicate over i2c. simple verb/value like these examples:
        0 (set value), 1 (value id), 5.5 (4-byte value)
        1 (reset)
        2 (read value), 3 (value id)

    2 interrupt pins for encoder feedback
    2 interrupt pins for limit switches
    1 PWM for motor control
    1 logic for motor direction

