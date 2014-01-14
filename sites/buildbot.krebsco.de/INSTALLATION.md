#?/bin/sh
# something like this

useradd ci
punani install python-virtualenv 
su ci
virtualenv buildbot
echo ". $HOME/buildbot/bin/activate" >~/.bashrc
pip install buildbot-slave buildbot
buildbot create-master master
# tahoe cp krebs:master.conf master/master.conf
buildbot reconf master
# or reconfigure as many slaves as you wish
buildslave create-slave slave localhost "ubuntu1204-local-slave" <PWD>
buildbot start master
buildslave start slave
# now make sure that docker is up and working
