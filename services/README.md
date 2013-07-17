# //services

## install service user
    
    make create-service-user service-user
    $EDITOR /opt/services/services.txt

## install and run test-server.py as systemd service

### install dependencies

    pacman -S python2-pyasn1 twisted

### install systemd service and configuration

    cp /krebs/services/etc/systemd/system/krebs-services-test-server.service \
        /etc/systemd/system/
    cp /krebs/services/etc/conf.d/krebs-services-test-server \
        /etc/conf.d/

### create services user and populate it's home

    useradd -m -r -l -f -1 -d /opt/services -k /var/empty services
    sudo -u services ssh-keygen -t rsa -P '' -f /opt/services/test.key
    $EDITOR /opt/services/services.txt

### run now and every reboot

    systemctl start krebs-services-test-server
    systemctl enable krebs-services-test-server
