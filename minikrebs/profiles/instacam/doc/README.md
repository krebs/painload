# Project Instacam

# Description

The aim of the project is to reliably push a video stream directly to the internets for
everyone to see at a very low price.

# Hardware

## Core (Wifi / Ethernet)
- TP-Link WR703n[Amazon](https://www.amazon.de/dp/B008UNA6FS/?tag=krebsco-21)[Ebay China](http://www.ebay.de/itm/BLUE-Mini-Nano-TP-LINK-TL-WR703N-150Mbps-WiFi-for-iPhone-4S-Wireless-Router-HOT-/360501556127?pt=COMP_EN_Routers&hash=item53ef91339f )        ~ 16 Euro
- USB Webcam
    - [Logitech C270 with Autofocus (AZ)](https://www.amazon.de/dp/B003PAOAWG/?tag=krebsco-21) ~ 25 Euro
    - [China NoName Cam (DX)](http://dx.com/p/compact-1-3mp-pc-usb-webcam-with-built-in-microphone-black-51874?Utm_rid=93398939&Utm_source=affiliate)        ~ 5++ Euro
    - [\* List of UVC Supported Devices](http://www.ideasonboard.org/uvc/ )
    - [\* List of GSPCA Supported Devices](http://linuxtv.org/wiki/index.php/Gspca_devices)
## 4G / 3G / UMTS
Currently Untested:
- usb hub ~ 4  Euro
    - [NoName USB 2.0 Hub (DX)](http://dx.com/p/4-port-usb-2-0-hub-7980?Utm_rid=93398939&Utm_source=affiliate)
    - [NoName USB 2.0 Hub (Ebay)](http://www.ebay.de/itm/200825754462?ssPageName=STRK:MEWNX:IT&_trksid=p3984.m1497.l2649#ht_2486wt_1366)
- umts stick ~ 20 Euro
- MicroSD card (optional)

## Mobile Version
either use (easy mode):
- USB Battery Bank
    - [Dealextreme](http://dx.com/p/rechargeable-2000mah-mobile-emergency-power-battery-with-6-adapters-66902?Utm_rid=93398939&Utm_source=affiliate)
or (expert mode):
- DC-DC StepDown Module
    - [Ebay](http://www.ebay.de/itm/221162832094?ssPageName=STRK:MEWNX:IT&_trksid=p3984.m1497.l2649#ht_3092wt_1132)
- Battery Pack
    - take any battery pack you can find (car battery, model making)

# Software

## Build Firmware

    git clone github.com/krebscode/painload krebs
    cd krebs/minikrebs
    ./prepare instacam
    builder/init

## Flash 

    # flash image is at:
    #       builder/bin/ar71xx/openwrt-ar71xx-generic-tl-wr703n-v1-squashfs-sysupgrade.bin 
    
    # either flash image directly via web interface or
    # after obtaining ssh-access on the router run

    OWN_IP=<<your ip>> ./upgrade <<remote ip>>
