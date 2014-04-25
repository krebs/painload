#!/usr/bin/env python
import json
def load_db(f):
    try:
        with open(f) as fl:
            return json.load(fl)
    except:
        #default db is []
        return []

def title_in_db(t,d):
    for index,entry in enumerate(d):
        if t == entry['title']:
            print("Title is already in list.")
            print("To vote for this type '.up %d'" %index)
            return True
    return False
def save_db(f,db):
    with open(f,"w") as x:
        json.dump(db,x)

def sort_by_votes(db):
    return sorted(db,key=lambda entry:sum(entry['votes'].values()),reverse=True)
