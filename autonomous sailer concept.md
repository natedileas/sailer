autonomous sailer concept

camera at mast head
    esp32cam probably. 

roller furling, single main sail. - current - 35mA no load - 200mA stall.
    rigid boom, captive foot?
    no boom?
    https://www.robotshop.com/products/e-s-motor-micro-dc-worm-gear-motor-160w-encoder-6v-98rpm
    1/2 emt outer shell or thin wall ss 1" tube, plain steel 1/4" rod mast?


pvc pipe body, angle iron keel/ballast
solar power; 
    ballpark 20W nominal of panels? 
        something like this: https://www.amazon.com/Retisee-Polycrystalline-Photovoltaic-Charger-Battery/dp/B0C8T85TKL?dib=eyJ2IjoiMSJ9.KWGgzRDNBrOFlGsXZ8heL3jEkfLr5YVy9wh06p8HRewk9IUzvE1IOVMfSgqXa3QTXJDi1ZzOM1cH2ks__-7nX4pBWO3yGWwz4CzsyZPNFMIk5agJUnxEzBo7Ho8UEe-0L5xhiBaSvPT1Oj4neA1oL8VHhMAZZwfWEd3_lHUKq0dfrHjPm5enr4fjzvHEBbkmXHwyQytpWMg3tQKL89wREmn60b8a3Gw3pah1bP_3p68.yjAakHpemDG0jpOKhi5wa02VT0L-KdR_qhmlPjvi_fM&dib_tag=se&keywords=mini+solar+cell&qid=1761423803&sr=8-15
        laid in two rows along the top
        or maybe something stupid like buying this and cutting it apart: https://www.walmart.com/ip/Portable-20W-solar-panel-foldable-and-waterproof-5VUSB-solar-charging-board/3105923579?wmlspartner=wlpa&selectedSellerId=101302630&selectedOfferId=20383E69202C4B97AF35A2F7F8DE3459

    manager
    batteries
        >= 10AH. that would allow ~30 hours operation in auto. 2Sx4P 18650 will do that.
        probably building my own pack is more work than it's worth. some kind of high-quality ots pack will probably work; well; 50000 mAH usb packs exist for about 70 bucks. would use a usb breakout board or solar charger board. need to make sure there's no timeout and that it can charge and discharge at the same time.
             https://www.bestbuy.com/product/energizer-ultimate-lithium-50000-mah-30w-power-delivery-3-port-usb-c-universal-portable-battery-charger-power-bank-w-lcd-display-black/J36C4YXK4S/sku/6589870?utm_source=feed

compass/attitude
    https://www.pololu.com/product/2863, 5mA

gps/comm
    https://store-usa.arduino.cc/products/4g-module-global, sleep=5mA, gps=500mA, lte=1000mA

main board - uno? 5v/3A
    https://store-usa.arduino.cc/products/uno-q?pr_prod_strat=jac&pr_rec_id=ad16a4cf3&pr_rec_pid=7733694267599&pr_ref_pid=7384757797071&pr_seq=uniform

modes
    recovery
        gps once/hour
        comm 1/hour
        no compass/att
        no sail - auto retract into safe position
        rudder hard right?
        no cam
        exit mode
            on command
    waypoint/nav
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
    manual
        enter mode
            on command
        comm,gps,cam 10s interval
        exit mode
            by command
        