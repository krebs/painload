GRAPH_SETTER1=dot
GRAPH_SETTER2=circo
LOG_FILE=/var/log/everything.log
OPENER=/bin/true

sudo pkill -USR2 tincd
sudo sed -n '/tinc.retiolum/{s/.*tinc.retiolum\[[0-9]*\]: //gp}' $LOG_FILE |\
    ./parse.py > retiolum.dot

$GRAPH_SETTER1 -Tpng -o $1retiolum_1.png retiolum.dot
$GRAPH_SETTER2 -Tpng -o $1retiolum_2.png retiolum.dot
$OPENER retiolum_1.png &>/dev/null 
rm retiolum.dot
