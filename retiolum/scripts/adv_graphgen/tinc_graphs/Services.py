import os,sys
services_dir=os.environ.get("SERIVCES_DIR","/home/reaktor/nag.services")
def add_services(nodes):
    for k,v in nodes.items():
        n = nodes[k]
        try:
            with open("{0}/{1}".format(services_dir,k)) as f:
                n["services"] = []
                for line in f.readlines():
                    n["services"].append(line.strip())
        except Exception as e:
            n["services"] = ["Error: No Service File!"]
    return nodes
def main():
    import json,sys
    try:
        nodes = add_services(json.load(sys.stdin))
        print (json.dumps(nodes,indent=4))
    except:
        print("unable to parse json data from stdin")
        sys.exit(1)

if __name__ == "__main__":
    main()
# vim: set expandtab:ts=4:sw=4
