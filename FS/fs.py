from flask import Flask, request, jsonify, abort
import socket, json

app = Flask(__name__)

def send_udp(as_ip, as_port, msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg.encode(), (as_ip, int(as_port)))
    sock.settimeout(2)
    try:
        data,_ = sock.recvfrom(4096)
    except:
        data=b""
    return data.decode(errors="ignore")

def fib(n:int)->int:
    a,b=0,1
    for _ in range(n):
        a,b=b,a+b
    return a

@app.put("/register")
def register():
    try:
        body = request.get_json(force=True)
        hostname,ip,as_ip,as_port = body["hostname"],body["ip"],body["as_ip"],body["as_port"]
    except:
        abort(400,"bad json")
    msg = f"TYPE=A\nNAME={hostname} VALUE={ip} TTL=10\n"
    send_udp(as_ip, as_port, msg)
    return ("",201)

@app.get("/fibonacci")
def fibonacci():
    num = request.args.get("number")
    if not (num and num.isdigit()):
        abort(400,"bad format")
    return jsonify({"result": fib(int(num))}),200

if __name__=="__main__":
    app.run(host="0.0.0.0",port=9090)