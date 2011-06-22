sudo pkill xscreensaver
sudo pkill tmux
sleep 1
export DISPLAY=:0

export URL="${URL-http://txgen_chinaman:lolwut@uk.btcguild.com:8332}"
#export URL="http://txgen:qJrXefWX@bitcoinpool.com:8334"
slock &
tmux start-server
tmux new-session -d -s mining -n mining
printenv > /home/user/environment
tmux new-window -t mining:1 'AMDOverdriveCtrl -i 0  mining.ovdr' 
tmux new-window -t mining:2 'AMDOverdriveCtrl -i 3  mining.ovdr' 
sleep 5
tmux new-window -t mining:3 "cd /opt/miners/phoenix; while sleep 1; do sudo python phoenix.py -u $URL -k phatk DEVICE=0 VECTORS BFI_INT WORKSIZE=256 AGGRESSION=12 FASTLOOPS=false;done"
tmux new-window -t mining:4 "cd /opt/miners/phoenix; while sleep 1;do  sudo python phoenix.py -u $URL -k phatk DEVICE=1 VECTORS BFI_INT WORKSIZE=256 AGGRESSION=10 FASTLOOPS=false ; done"
