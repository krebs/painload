#!/usr/bin/python2 
import sys, os, time, socket, subprocess, thread, random, Queue, binascii, logging, hashlib, urllib2 #these should all be in the stdlib
from optparse import OptionParser

def pub_encrypt(netname, hostname_t, text):  #encrypt data with public key
    logging.debug("encrypt: " + text)
    if hostname_t.find("`") != -1: return(-1)
    try:
        enc_text = subprocess.os.popen("echo '" + text + "' | openssl rsautl -pubin -inkey /etc/tinc/" + netname + "/hosts/.pubkeys/" + hostname_t + " -encrypt | base64 -w0")
        return(enc_text.read())
    except:
        return(-1)

def priv_decrypt(netname, enc_data): #decrypt data with private key
    if enc_data.find("`") != -1: return(-1)
    dec_text = subprocess.os.popen("echo '" + enc_data + "' | base64 -d | openssl rsautl -inkey /etc/tinc/" + netname + "/rsa_key.priv -decrypt")
    return(dec_text.read())

def address2hostfile(netname, hostname, address): #adds address to hostsfile or restores it if address is empty
    hostfile = "/etc/tinc/" + netname + "/hosts/" + hostname
    addr_file = open(hostfile, "r")
    addr_cache = addr_file.readlines()
    addr_file.close()
    if address != "": 
        addr_cache.insert(0, "Address = " + address + "\n")
        addr_file = open(hostfile, "w")
        addr_file.writelines(addr_cache)
        addr_file.close
        logging.info("sending ALRM to tinc deamon!")
        tincd_ALRM = subprocess.call(["tincd -n " + netname + " --kill=HUP" ],shell=True)
    else: 
       recover = subprocess.os.popen("tar xzf /etc/tinc/" + netname + "/hosts/hosts.tar.gz -C /etc/tinc/" + netname + "/hosts/ " + hostname)

def findhostinlist(hostslist, hostname, ip): #finds host + ip in list
    for line in xrange(len(hostslist)):
        if hostname == hostslist[line][0] and ip == hostslist[line][1]:
            return line
    return -1 #nothing found

def getHostname(netname):
    tconf = open("/etc/tinc/" + netname + "/tinc.conf", "r")
    feld = tconf.readlines()
    tconf.close()
    for x in feld:
        if x.startswith("Name"):
            return str(x.partition("=")[2].lstrip().rstrip("\n"))
             
    print("hostname not found!")
    return -1 #nothing found

def get_hostfiles(netname, url_files, url_md5sum):
    try:
        get_hosts_tar = urllib2.urlopen(url_files)
        get_hosts_md5 = urllib2.urlopen(url_md5sum)
        hosts_tar = get_hosts_tar.read()
        hosts_md5 = get_hosts_md5.read()
    
        if str(hosts_md5) == str(hashlib.md5(hosts_tar).hexdigest() + "  hosts.tar.gz\n"):
            hosts = open("/etc/tinc/" + netname + "/hosts/hosts.tar.gz", "w")
            hosts.write(hosts_tar)
            hosts.close()
        else:
            logging.error("hosts.tar.gz md5sum check failed!")
    except:
        logging.error("hosts file  download failed!")
    

####Thread functions


def sendthread(netname, hostname, sendfifo, ghostmode): #send to multicast, sends keep alive packets
    while True:
        try:
            #{socket init start
            ANY = "0.0.0.0"
            SENDPORT = 23542
            MCAST_ADDR = "224.168.2.9"
            MCAST_PORT = 1600

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) #initalize socket with udp
            sock.bind((ANY,SENDPORT)) #now bound to Interface and Port
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255) #activate multicast
            #}socket init end

            if ghostmode == 0:
    
                i = 9 
    
                while True:
                    i += 1
                    if not sendfifo.empty():
                        sock.sendto(sendfifo.get(), (MCAST_ADDR,MCAST_PORT) )
                        logging.info("send: sending sendfifo")
                    else:
                        time.sleep(1)
                    if i == 10:
                        sock.sendto("#Stage1#" + netname + "#" + hostname + "#", (MCAST_ADDR,MCAST_PORT) )
                        logging.debug("send: sending keep alive")
                        i = 0
            else:
                while True:
                    if not sendfifo.empty():
                        sock.sendto(sendfifo.get(), (MCAST_ADDR,MCAST_PORT) )
                        logging.info("send: sending sendfifo")
                    else:
                        time.sleep(1)

        except:
            logging.error("send: socket init failed")
            time.sleep(10)



def recvthread(netname, hostname, timeoutfifo, authfifo): #recieves input from multicast, send them to timeout or auth
    while True:
        try:
            ANY = "0.0.0.0"
            MCAST_ADDR = "224.168.2.9"
            MCAST_PORT = 1600
        
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) #create a UDP socket
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) #allow multiple sockets to use the same PORT number
            sock.bind((ANY,MCAST_PORT)) #Bind to the port that we know will receive multicast data
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255) #tell the kernel that we are a multicast socket
        
        
            status = sock.setsockopt(socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,   #Tell the kernel that we want to add ourselves to a multicast group
            socket.inet_aton(MCAST_ADDR) + socket.inet_aton(ANY)); #The address for the multicast group is the third param
        
            while True:
                while True:
            
                    try:
                        data, addr = sock.recvfrom(1024)
                        ip, port = addr
                        break
                    except socket.error, e:
                        pass
                    
                logging.debug("recv: got data")
                dataval = data.split("#")
                if dataval[0] == "":
                    if dataval[2] == netname:
                        if dataval[1] == "Stage1":
                            if dataval[3] != hostname:
                                timeoutfifo.put(["tst", dataval[3], ip])
                                logging.info("recv: got Stage1: writing data to timeout")
                                logging.debug("recv: ;tst;" + dataval[3] + ";" + ip)
                        if dataval[1] == "Stage2":
                            if dataval[3] == hostname:
                                authfifo.put([dataval[1], dataval[3], ip, dataval[4]])
                                logging.info("recv: got Stage2: writing data to auth")
                                logging.debug("recv: ;" + dataval[1] + ";" + dataval[3] + ";" + ip + ";" + dataval[4])
                        if dataval[1] == "Stage3":
                            if dataval[3] != hostname:
                                authfifo.put([dataval[1], dataval[3], ip, dataval[4]])
                                logging.info("recv: got Stage3: writing data to auth")
                                logging.debug("recv: ;" + dataval[1] + ";" + dataval[3] + ";" + ip + ";" + dataval[4])
        except:
            logging.error("recv: socket init failed")
            time.sleep(10)

def timeoutthread(netname, timeoutfifo, authfifo): #checks if the hostname is already in the list, deletes timeouted nodes
    hostslist = [] #hostname, ip, timestamp

    while True:
        if not timeoutfifo.empty():
            curhost = timeoutfifo.get()
            if curhost[0] == "add":
                hostslist.append([curhost[1], curhost[2], time.time()])
                address2hostfile(netname, curhost[1], curhost[2])
                logging.info("adding host to hostslist")
            elif curhost[0] == "tst":
                line = findhostinlist(hostslist, curhost[1], curhost[2])
                if line != -1:
                    hostslist[line][2] = time.time()
                    logging.debug("timeout: refreshing timestamp of " + hostslist[line][0])
                else:
                    authfifo.put(["Stage1", curhost[1], curhost[2]])
                    logging.info("timeout: writing to auth")

        else:
            i = 0
            while i < len(hostslist):
                if time.time() - hostslist[i][2] > 60:
                    address2hostfile(netname, hostslist[i][0], "")
                    del hostslist[i]
                    logging.info("timeout: deleting dead host")
                else:
                    i += 1
            time.sleep(2)

def auththread(netname, hostname, authfifo, sendfifo, timeoutfifo): #manages authentication with clients (bruteforce sensitve, should be fixed)
    authlist = [] #hostname, ip, Challenge, timestamp


    while True:
        try:
            if not authfifo.empty():
                logging.debug("auth: authfifo is not empty")
                curauth = authfifo.get()
                if curauth[0] == "Stage1":
                    line = findhostinlist(authlist, curauth[1], curauth[2])
                    if line == -1:
                        challengenum = random.randint(0,65536)
                        encrypted_message = pub_encrypt(netname, curauth[1], "#" + hostname + "#" + str(challengenum) + "#")
                        authlist.append([curauth[1], curauth[2], challengenum, time.time()])
                    else:
                        encrypted_message = pub_encrypt(netname, authlist[line][0], "#" + hostname + "#" + str(authlist[line][2]) + "#") 
                    if encrypted_message == -1:
                        logging.info("auth: RSA Encryption Error")
                    else:
                        sendtext = "#Stage2#" + netname + "#" + curauth[1] + "#" + encrypted_message + "#"
                        sendfifo.put(sendtext)
                        logging.info("auth: got Stage1 sending now Stage2")
                        logging.debug("auth: " + sendtext)
    
                if curauth[0] == "Stage2":
                    dec_message = priv_decrypt(netname, curauth[3])
                    splitmes = dec_message.split("#")
                    if splitmes[0] == "":
                        encrypted_message = pub_encrypt(netname, splitmes[1], "#" + splitmes[2] + "#")
                        if encrypted_message == -1:
                            logging.error("auth: RSA Encryption Error")
                        else:
                            sendtext = "#Stage3#" + netname + "#" + curauth[1] + "#" + encrypted_message  + "#"
                            sendfifo.put(sendtext)
                            logging.info("auth: got Stage2 sending now Stage3")
                            logging.debug("auth: " + sendtext)
    
                if curauth[0] == "Stage3":
                    line = findhostinlist(authlist, curauth[1], curauth[2])
                    if line != -1:
                        dec_message = priv_decrypt(netname, curauth[3])
                        splitmes = dec_message.split("#")
                        logging.info("auth: checking challenge")
                        if splitmes[0] == "":
                            if splitmes[1] == str(authlist[line][2]):
                                timeoutfifo.put(["add", curauth[1], curauth[2]])
                                del authlist[line]
                                logging.info("auth: Stage3 checked, sending now to timeout")
                            else: logging.error("auth: challenge checking failed")
                        else: logging.error("auth: decryption failed")
    
            else:
                i = 0
                while i < len(authlist):
                    if time.time() - authlist[i][3] > 120:
                        del authlist[i]
                        logging.info("auth: deleting timeoutet auth")
                    else:
                        i += 1
                time.sleep(1)
        except:
            logging.error("auth: thread crashed")

#Program starts here!

parser = OptionParser()
parser.add_option("-n", "--netname", dest="netname", help="the netname of the tinc network")
parser.add_option("-H", "--hostname", dest="hostname", default="default" , help="your nodename, if not given, it will try too read it from tinc.conf")
parser.add_option("-d", "--debug", dest="debug", default="0", help="debug level: 0,1,2,3  if empty debug level=0")
parser.add_option("-g", "--ghost", action="store_true", dest="ghost", default=False, help="deactivates active sending, keeps you anonymous in the public network")
(option, args) = parser.parse_args()

if option.netname == None:
    parser.error("Netname is required, use -h for help!")
if option.hostname == "default":
    option.hostname = getHostname(option.netname)

hostname = option.hostname
netname = option.netname


#Logging stuff
LEVELS = {'3' : logging.DEBUG,
          '2' : logging.INFO,
          '1' : logging.ERROR,
          '0' : logging.CRITICAL}

level_name = option.debug
level = LEVELS.get(level_name, logging.NOTSET)
logging.basicConfig(level=level)

get_hostfiles(netname, "http://vpn.miefda.org/hosts.tar.gz", "http://vpn.miefda.org/hosts.md5")

tar = subprocess.call(["tar -xzf /etc/tinc/" + netname + "/hosts/hosts.tar.gz -C /etc/tinc/" + netname + "/hosts/"], shell=True)
start_tincd = subprocess.call(["tincd -n " + netname ],shell=True)

sendfifo = Queue.Queue() #sendtext
authfifo = Queue.Queue() #Stage{1, 2, 3} hostname ip enc_data
timeoutfifo = Queue.Queue() #State{tst, add} hostname ip

thread_recv = thread.start_new_thread(recvthread, (netname, hostname, timeoutfifo, authfifo))
thread_send = thread.start_new_thread(sendthread, (netname, hostname, sendfifo, option.ghost))
thread_timeout = thread.start_new_thread(timeoutthread, (netname, timeoutfifo, authfifo))
thread_auth = thread.start_new_thread(auththread, (netname, hostname, authfifo, sendfifo, timeoutfifo))

##dirty while function, SHOULD BE IMPROVED
while True:
    time.sleep(10)
