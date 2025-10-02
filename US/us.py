from flask import Flask, request, abort
import socket, requests, re

app = Flask(__name__)

def udp_query(as_ip, as_port, hostname):
    msg=f"TYPE=A\nNAME={hostname}\n"
    sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.sendto(msg.encode(),(as_ip,int(as_port)))
    data,_=sock.recvfrom(4096)
    txt=data.decode()
    m=re.search(r"VALUE=([0-9\.]+)",txt)
    return m.group(1) if m else None

@app.get("/fibonacci")
def fibo():
    hostname=request.args.get("hostname")
    fs_port=request.args.get("fs_port")
    number=request.args.get("number")
    as_ip=request.args.get("as_ip")
    as_port=request.args.get("as_port")
    if not all([hostname,fs_port,number,as_ip,as_port]):
        abort(400,"missing params")

    fs_ip=udp_query(as_ip,as_port,hostname)
    if not fs_ip:
        abort(400,"dns not found")

    r=requests.get(f"http://{fs_ip}:{fs_port}/fibonacci",params={"number":number})
    return (r.text,r.status_code,{"Content-Type":r.headers.get("Content-Type","text/plain")})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8080)