GRAPH_SETTER=dot
LOG_FILE=/var/log/everything.log

sudo pkill -USR2 tincd
sudo sed -n '/tinc.retiolum/{s/.*tinc.retiolum\[[1-9]*\]: //gp}' $LOG_FILE |\
    ./parse.py | tee retiolum.dot |\
    $GRAPH_SETTER -Tpng -o retiolum.png
xdg-open retiolum.png
