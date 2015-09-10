# Generate Graphs from tinc

## Install
### Nix

    # tinc_pre is required:
    nix-env -i -f tinc_graphs.nix

    ## e.g. in Retiolum:
    ## krebs.retiolum.tinc = pkgs.tinc_pre
### Local

    python setup.py install
    # also install graphviz,imagemagic for building graphs


### Usage:

see source of the 2 builder scripts:

    #all-around-builder
    # env: EXTERNAL_FOLDER, INTERNAL_FOLDER, GEODB, TINC_HOSTPATH
    all-the-graphs

    # build actual graphs
    build-graph

    # exported py scripts
    tinc-stats2json         # - parses tinc current state into json
    tinc-build-graph        # - transfers json to graph
    copy-map                # - copies map.html into $1
    add-geodata             # - adds geodata to json
    tinc-availability-stats # adds availability data to json

## Geodb infos

- http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
- nix-env -iA geolite-legacy
