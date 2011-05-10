#!/usr/bin/python2
import sqlite3
import os, sys

def create_db(netname):
    conn = sqlite3.connect("/etc/tinc/"+ netname + "/hosts.sqlite")
    db = conn.cursor()
    db.execute('''create table hosts(hostname text, subnet text, address text, port text, r_pub text, t_pub text)''')
    conn.commit()
    db.close()

def PubInDb(netname, hostname):
    pubfile = open("/etc/tinc/" + netname + "/hosts/.pubkeys/" + hostname, "r")
    publines = pubfile.readlines()
    pubfile.close()
    pubkey = ""
    for i in range(len(publines)):
        pubkey += publines[i]
    print(pubkey)
    conn = sqlite3.connect("/etc/tinc/" + netname + "/hosts.sqlite")
    c = conn.cursor()
    tupel = [pubkey, hostname]
    c.execute('UPDATE hosts SET r_pub=? WHERE hostname=?', tupel)
    conn.commit()
    c.close()     

def HostInDb(netname, hostname):
    hostFile = open("/etc/tinc/"+ netname + "/hosts/" + hostname, "r")
    hostlines = hostFile.readlines()
    hostFile.close()
    conn = sqlite3.connect("/etc/tinc/"+ netname + "/hosts.sqlite")
    db = conn.cursor()

    lines = 0
    Subnet = ""
    Tinc_pub_key = ""
    Address = "#Address = none\n"
    Port = "Port =  655\n"
    while lines < len(hostlines):
        if hostlines[lines][0:4] == "Addr":
            Address = hostlines[lines]
            print Address
        if hostlines[lines][0:4] == "Subn":
            Subnet = hostlines[lines]
            print Subnet
        if hostlines[lines][0:4] == "Port":
            Port =  hostlines[lines]
            print Port
        if hostlines[lines][0:10]  == "-----BEGIN":
            Tinc_pub_key_array = hostlines[lines:lines+8]
            line = 0
            Tinc_pub_key = ""
            while line < len(Tinc_pub_key_array):
                Tinc_pub_key += Tinc_pub_key_array[line]
                line += 1
            print Tinc_pub_key
        lines += 1
    if not(Subnet == "" or Tinc_pub_key == ""):
        tupel = (hostname, Subnet, Address, Port, Tinc_pub_key )
        conn = sqlite3.connect("/etc/tinc/"+ netname + "/hosts.sqlite")
        db = conn.cursor()
        db.execute('insert into hosts values(?,?,?,?,"none",?)', tupel)
        conn.commit()
        db.close()
    
def ShowDb(netname):
    conn = sqlite3.connect("/etc/tinc/" + netname + "/hosts.sqlite")
    db = conn.cursor()
    db.execute("select * from hosts")
    for hosts in db:
        for i in range(len(hosts)):
            print hosts[i]
    db.close

def DirInDb(netname):
    #the normal tinc files are read into the sqlite
    files = os.listdir("/etc/tinc/" + netname + "/hosts/")
    file_n = 0
    while file_n < len(files):
        if files[file_n][0] == ".":
            files.remove(files[file_n])
            file_n -= 1
        file_n += 1
    for filename in files:
        HostInDb(netname, filename)
    #the pubkeys are included into the sqlite
    pubfiles = os.listdir("/etc/tinc/" + netname + "/hosts/.pubkeys/")
    for pubname in pubfiles:
        PubInDb(netname, pubname)


#Program start here
netname = sys.argv[1]

try: 
    os.remove("/etc/tinc/" + netname + "/hosts.sqlite")
except: 
    print("no hosts.sqlite found")

create_db(netname)
DirInDb(netname)
