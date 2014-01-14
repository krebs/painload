# paste.retiolum

paste is a minimalistic pastebin with sprunge.us in mind.
This paste may be a supplement to all the 'open' pastebins as the punching
lemma applies to this installation.
The installation always runs on a higher port (4000), to get a really short
hostname, the host which provides this service should have a short name as well
and have an nginx or apache which translates all request to hostname:80 to
localhost:4000. see Nginx Configuration.

# Sources

- https://github.com/makefu/bump

# Installation

## Environment

    git clone https://github.com/makefu/bump
    useradd -a bump -m -d /opt/bump
    cd /opt/paste
    virtualenv .
    pip install -r deps.txt

## Nginx

see etc/nginx/

## Supervisor

see etc/supervisor.d/
