# //Reaktor

## Quickstart

    ## 1. create a dedicated user
    useradd reaktor

    ## 2. marry Reaktor with /sbin/init

    ## 2a. /etc/inittab-like foo
    echo 10:2345:respawn:/bin/su reaktor -c /krebs/Reaktor/index >>/etc/inittab
    # or 10:2345:respawn:/usr/bin/sudo -u reaktor /krebs/Reaktor/index
    # if reaktor's shell is /bin/false or similar
    # [check with e.g getent passwd reaktor]
    telinit q

    ## 2b. upstart-like foo

    cat > /etc/init/Reaktor.conf <<EOF
    description "Krebs Reaktor"
    author      "The Ministerium"
    stop on runlevel [016]
    respawn
    exec /usr/bin/sudo -u reaktor /krebs/Reaktor/index
    EOF
    start Reaktor
