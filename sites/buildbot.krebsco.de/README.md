# buildbot.krebsco.de
The buildbot is configured to run all of the fancy test cases in painload (and
possibly more project).

# Testing the Painload
Subprojects may contain folders called t/ which may contain executables which
will be called by running `make test` in the respective folder.
A sample `make test` may look like `//krebs/ship/Makefile`.
The buildbot master may include these paths into the test chain.

# Master & Slave
Buildbot contains of a master with all the configuration magic and n slaves
which will be building. Both the master and the slave are started at system
startup as the user ci (see INSTALLATION.md).
The configuration file is currently stored at tahoe:

    krebs:ci/buildbot/master/master.cfg
    # and 
    krebs:ci/buildbot/slave/buildbot.tac

# Docker
For more flexibility in testing the painload contains test which are using
docker virtual environments. These have the advantage of providing a new
environment at every run.

Docker access must be made available to the CI user.

For a Sample Docker Test, see /krebs/ship/t/docker/docker_remote_punani.sh

