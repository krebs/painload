# //Reaktor

## Quickstart

    ## 1. prepare Reaktor
    //Reaktor/install

    ## 2. create a dedicated user
    useradd Reaktor

    ## 3. marry Reaktor with /sbin/init

    ## 3a. /etc/inittab-like foo
    echo 10:2345:respawn:/bin/su Reaktor -c /krebs/Reaktor/index >>/etc/inittab
    # or 10:2345:respawn:/usr/bin/sudo -u Reaktor /krebs/Reaktor/index
    # if Reaktor's shell is /bin/false or similar
    # [check with e.g getent passwd Reaktor]
    telinit q

    ## 3b. upstart-like foo

    cat > /etc/init/Reaktor.conf <<EOF
    description "Krebs Reaktor"
    author      "The Ministerium"
    stop on runlevel [016]
    respawn
    exec /usr/bin/sudo -u Reaktor /krebs/Reaktor/index
    EOF
    start Reaktor
