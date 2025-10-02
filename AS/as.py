import socket, os, re

DB_FILE = "db.txt"
HOST, PORT = "0.0.0.0", 53533

def load_db():
    m = {}
    if os.path.exists(DB_FILE):
        for line in open(DB_FILE):
            parts = line.strip().split(",")
            if len(parts) == 3:
                m[parts[0]] = (parts[1], int(parts[2]))
    return m

def save_db(m):
    with open(DB_FILE,"w") as f:
        for k,(ip,ttl) in m.items():
            f.write(f"{k},{ip},{ttl}\n")

def parse(msg):
    kv = {}
    for ln in msg.strip().splitlines():
        if "=" in ln:
            k,v = ln.split("=",1)
            kv[k.strip().upper()] = v.strip()
    return kv

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[AS] UDP listening {PORT}")
    db = load_db()
    while True:
        data, addr = sock.recvfrom(4096)
        txt = data.decode()
        kv = parse(txt)
        if "VALUE" in kv:  # Registration
            db[kv["NAME"]] = (kv["VALUE"], int(kv.get("TTL","10")))
            save_db(db)
            resp = f"TYPE=A\nNAME={kv['NAME']} VALUE={kv['VALUE']} TTL=10\n"
            sock.sendto(resp.encode(), addr)
        else:  # Query
            name = kv.get("NAME")
            if name in db:
                ip,ttl = db[name]
                resp = f"TYPE=A\nNAME={name} VALUE={ip} TTL={ttl}\n"
            else:
                resp = f"TYPE=A\nNAME={name} VALUE=\n"
            sock.sendto(resp.encode(), addr)

if __name__ == "__main__":
    main()