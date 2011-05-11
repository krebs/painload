sudo sed -n '/tinc.retiolum/{s/.*tinc.retiolum\[[0-9]*\]: //gp}' /var/log/everything.log | ./parse.py | tee here.dot | dot | gvcolor | dot -Tpng -O
mirage noname.dot.png
