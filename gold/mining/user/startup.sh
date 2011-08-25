sudo pkill tmux
sleep 5
source ~/.profile
export DISPLAY=:0
export URL="${URL-http://txgen_chinaman:lolwut@uk.btcguild.com:8332}"
#export URL="http://txgen:qJrXefWX@bitcoinpool.com:8334"
tmux start-server
tmux new-session -d -s mining -n mining
tmux new-window -t mining:1 'cd ~;AMDOverdriveCtrl -i 0 mining.ovdr' 
tmux new-window -t mining:2 'cd ~;AMDOverdriveCtrl -i 3 mining.ovdr' 
sleep 5
tmux new-window -t mining:3 "cd /usr/src/phoenix-miner/; while sleep 1; do sudo ./phoenix.py -u $URL -k phatk DEVICE=0 VECTORS BFI_INT WORKSIZE=256 AGGRESSION=12 FASTLOOPS=false;done"
tmux new-window -t mining:4 "cd /usr/src/phoenix-miner/; while sleep 1; do sudo ./phoenix.py -u $URL -k phatk DEVICE=1 VECTORS BFI_INT WORKSIZE=256 AGGRESSION=12 FASTLOOPS=false;done"
