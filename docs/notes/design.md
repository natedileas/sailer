# concept

Robotic RC sailboat which can operate autonomously in lake ontario with a maximum mission time of 6 months. 

# subsystems
## power

Solar power with a lithium battery bank. MVP is a flexible COTS 20-30W panel of dimensions compatible with the hull with usb output, directly connected to the bank input. Battery bank MVP is a COTS battery bank, approx 50Ah for 5-12V outputs, with usb in and out. cracking the case and soldering leads to the power button and status leds might be a good idea for reliable battery status and operations.

## comm

Base options: LTE, LORA, satellite. LTE is easy, covers most of the lake. LORA is more extensible, potentially less coverage. Sat is expensive, slow, low bandwidth, global coverage. More musings on this in [data.md](data.md)

## mast

ss thinwall outer shell with solid rod inner furling. ss thin wall boom welded on. mast will be rotated by inner worm wheel servo so that holding position is very cheap energetically. same with furler and rudder. tradeoff here is that it is slow and more mechanically complex than a line control servo with a brake, but sturdier for the same price. bearings will be integrated into the mast head and foot 3-d prints, possibly just simple nylon sleeve bearings.

## sailing control

sail control is done by boom/hull angle servo. a roller furler will be used to control sail area, design max 15 knots for normal sailing operations due to low weight. a PID loop for rudder and boom angle with wind spd, heading, and target heading input is needed.

### furling

updatable formula for furling. idea being that there's a speed below whcih we never furl. in between that and our max speed, simple linear mapping of furling fraction. Initial design parameters of 10 knots for start of furl, 15 knots max.

    furl_fraction = 0  { measured_wind_spd <= param_furl_start_wspd } 
    furl_fraction = (measured_wind_spd-param_furl_start_wspd) / (param_max_windspd-param_furl_start_wspd)
    furl_fraction = 1 { measured_wind_spd >= param_max_windspd }

### boom/rudder control

for upwind sailing, tacking is required. this requires some state to track progress versus a waypoint.

for downwind, the assumption is that no tacking is required. simple separate PID loops should work, although some scaling with wind speed might be required. one loop will have wind direction modifying boom angle, and bearing to waypoint modifying rudder angle. There is a discontinuity in downwind boom angle when the wind direction crosses 180, bt it is not as extreme as for upwind.

alternatively, could have an algo where speed is being maximized?

kalman filter state estimation? for bearings, winddir, etc? position?


## radio

A onboard VHF radio would be pretty cool. Not a neccesary piece of safety equipment for an unmanned craft, but interesting to hear from other vessels and possibly neccesary to talk with authorities. MVP is a handheld vhf with the case stripped off and buttons resoldered to leads for external control. 

requires something like 10 externally operated buttons, plus speaker and mic. this might require another esp32 or something. power hungry in transmit.

## position

gps module and antenna (may be combined with lte module). relatively infrequent reads to keep power usage down.

## hull

planning to constuct the hull out of 6in clear pvc pipe (so that solar can remain inside), 3d-printed parts for complicated internal stuctures, and steel sheet/shaft for strength critical items. aluminum for keel and rudder. standard pvc fittings will be used for the bow and transom, sealed with 4200/5200 as the application dictates. orings will be used on the mast and rudder control shaft hull penetrations.

below water line, the keel will be fixed by a 3-d printed scaffold, covered in glass+epoxy+gelcoat?

nav lights are a little silly in this application, probably a good idea. plus a status led or 2 for com/mode info to an observer.

## sensing

temp (multiple spots? servos, battery?), humidity, pressure, camera, wind spd, wind direction, compass, attitude

### camera

probably this requires a esp32cam or similar at the top of the mast, connected via i2c/UART/etc twisted pair to the main board. camera cables are unshielded. maybe ethernet (cat5e) or similar for power and data up to the masthead. would be cool to have another of these inside the hull, pointed up, or sideways, or down.

# operations

Operations will take place over command/control channel defined in the comm subsytem. more notes on this in [data.md](data.md). MVP is a python website which relays CNC and also serves the public detailed information, while gating command functionality behind auth.

## modes

power analysis for these lives in a google sheet at the moment.

### recovery
        gps once/hour
        comm 1/hour
        no compass/att
        no sail - auto retract into safe position
        rudder hard right?
        no cam
        exit mode
            on command
### waypoint/nav
        entered by command only
        gps 1/hour
        comm 1/hour
        compass/att 2/s
        sail control 1/s
        rudder control 1/s
        cam 10 min
        exit to recovery mode 
            if attitude too nuts
            if battery falls below limit
            if gps/comm/att failure?
            if progress toward target not made for 3 hours?

### manual
        enter mode
            on command
        comm,gps,cam 10s interval
        exit mode
            by command

## tough cases
### hard restart

all the batteries run down, it drifts, sun comes out, reboot into recovery?
