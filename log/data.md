# comm
## protocol 

https

## auth

basic. Should be fine with https. password will be a super secret.

## message

http post from robot to server at intervals

### request

will be the data files built up over the last comm interval. multipart/form-data encoded.  since these are sampled at different intervals, just have a separate data file for each and concatenate them to the response. should result in less data overall. split into att/pos/motor (fast sample rate), temp/humid/pos/battery (slow sample rate), and once per comm (parameters, waypoints, other long term goals). Pictures as well. comm id (uint32) should be included in the file name. use http multi-part file upload with names like this: "data-{comm_id:06d}.{type}"

#### volumetrics

fast sample rate (1 per second): att (6x float), wind dir/spd (2x float), compass (1x float),  = 40 B, 27kB / 10 minutes
slow sample rate ( 10 minutes): temp/humid/lat-lon/battery (5x float),motor ( 3x uint16) = 18B
once/comm rate: parameters (20x float?), commID (uint16),  = 40 B
pictures (10 minutes): 640x480 uint8 = 300 kB

~330 kB/10 minutes
~46.4 MB per day
~16.5 GB per year

### response

the response content will be any command(s) which have been issued in the last interval. the server takes responsibility for re-issuing commands if missed? mechanism for this?

the content will look something like this:

    #commandtype:arg1,arg2
    changetomode:2
    setparam:RUDDER_CENTER,50
    reboot

Still working out a full list of commands and their arguments. The total volume of commands is likely to be fairly small.

### volumetrics

less than 1 kB, unless we have a problem.