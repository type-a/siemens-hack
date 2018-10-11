from flask import Flask, request, send_file
import os
import time
import threading
import requests
import wget
import requests, zipfile, io
from datetime import datetime
from werkzeug import secure_filename


app = Flask(__name__)

neighbours = []
device_id = os.environ["ID"]
port = 5000 + int(device_id)

@app.route("/add_neighbour", methods=["GET"])
def add_neighbour():
    neighbour = request.args.get("neighbour", type=str)
    neighbours.append(neighbour)
    return "done"

@app.route("/get_latest_time", methods=["GET"])
def get_latest_time():
    time = 0
    for files in os.listdir("files"):
        if int(files.split(".")[0]) > int(time):
            time = files.split(".")[0]
    return time

@app.route("/get_latest_code", methods=["GET"])
def get_latest_code():
    time = get_latest_time()
    return send_file(os.path.join("files",time + ".zip"), as_attachment=True)

@app.route("/get_code", methods=["GET"])
def get_code(time_n):
    return send_file(os.path.join("http://" + host + "files", time_n + ".zip"), as_attachment=True)

@app.route("/upload_code", methods=["POST"])
def upload_code():
    f = request.files['file']
    f.save(secure_filename("files/"+str(int(datetime.now().timestamp()))+".zip"))
    
def stop_software():
    os.system("killall -9 code")

def start_software():
    os.system("cd current; ./code &")

def restart_software():
    stop_software()
    os.system("rm -rf current/*")
    z = zipfile.ZipFile("files/"+get_latest_time()+".zip", 'r')
    z.extractall("current")
    z.close()
    os.system("chmod 777 current/code")
    start_software()

def notify_master():
    requests.get("http://thealgo-pc:3000/addDevice?id="+str(device_id)+"&port="+str(port))

def tick():
    notify_master()
    time_ours = get_latest_time() ## get latest time
    time_neighbours = [int(requests.get("http://" + n + "/get_latest_time").text) for n in neighbours]
    lis = []
    for n in neighbours:
        lis.append([int(requests.get("http://" + n + "/get_latest_time").text), n])
    time = 0
    host = "0"
    for dat in lis:
        if dat[0] > time:
            host = dat[1]
            time = dat[0]
    print(host)
    if int(time_ours) < int(time):
        os.chdir("files")
        wget.download("http://" + host + "/get_latest_code")
        os.chdir("..")
        restart_software()
    threading.Timer(2, tick).start()
    


tick()
restart_software()

if __name__ == '__main__':
    app.run(port = port, host= "0.0.0.0")
