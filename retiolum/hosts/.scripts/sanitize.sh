sudo sed -n '/tinc.retiolum/{s/.*tinc.retiolum\[[1-9]*\]: //gp}' /var/log/everything.log |  ./parse.py | tee here.dot | dot -Tpng -o retiolum.png
mirage retiolum.png
