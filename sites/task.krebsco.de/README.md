# task.krebsco.de
a taskd server deployment

# Installation

  yaourt -S taskd
  cp /usr/share/taskd/pki/generate.client /var/lib/taskd

# configuration
taskd uses pki for login

    systemctl enable taskd
    systemctl start taskd
    export TASKDDATA=/var/lib/taskd
    taskd add org Krebs
    taskd config --force pid.file $TASKDDIR/taskd.pid
    taskd config --force log $TASKDDIR/taskd.log
    taskd config --force client.allow '^task [2-9],^taskd,^libtaskd'

# add new client
for a new client we need to create certificates:
    
    # on server
    cd /var/lib/taskd
    ./generate.client username
    # give new certs to user
    curl -F'p=username.cert.pem' http://paste
    curl -F'p=username.key.pem' http://paste
    curl -F'p=ca.cert.pem' http://paste
    taskd add user krebs username
    # outputs <uid>

    # on client
    mkdir ~/.task
    curl http://paste/abcde > username.cert.pem
    curl http://paste/efghi > username.key.pem
    curl http://paste/jklmn > ca.cert.pem
    task config taskd.server task.krebsco.de:53589
    task config taskd.credentials 'krebs/makefu/<uid>'
    task sync init
