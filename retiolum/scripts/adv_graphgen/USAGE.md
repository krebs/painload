# Example usage
make sure you have the correct permissions!

# High Level

    # creates all graphs with predefined paths (see source code of this script)
    ./all_the_graphs.sh

    # create anonymized graphs to /tmp
    ./anonytize.sh /tmp
    
    # create full detail graphs to /var/www/graph.retiolum
    ./sanitize.sh /var/ww/graph.retiolum

    # return currently availabe supernodes
    tinc_stats/Supernodes.py

# Low Level

    # returns the current tinc graph as json
    tinc_stats/Log2JSON.py

    # adds GEOIP information to the json file
    tinc_stats/Log2JSON.py | tinc_stats/Geo.py

    # creates a grapviz file from current graph, pipes into a timpfile
    tinc_stats/Log2JSON.py | tinc_stats/Graph.py complete > /tmp/out.graphviz
