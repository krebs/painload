# //Reaktor

## Quickstart

    //Reaktor/install

    echo 10:2345:respawn:/bin/su nobody -c /krebs/Reaktor/index >>/etc/inittab
    # or 10:2345:respawn:/usr/bin/sudo -u nobody /krebs/Reaktor/index
    # if nobody's shell is /bin/false or similar

    telinit q
