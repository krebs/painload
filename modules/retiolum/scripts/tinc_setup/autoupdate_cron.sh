cat <<EOF
# Add these lines to your crontab:

12 23 * * * /home/node/usr/sbin/tincd -n retiolum &>/dev/null
12 23 * * * cd /home/node/etc/tinc/retiolum/hosts/ && /opt/local/bin/git pull && pkill -HUP tincd
EOF

