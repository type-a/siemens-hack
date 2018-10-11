from flask import Flask, request, send_file
import os
import time
import threading
import requests
import wget
import requests, zipfile, io
app = Flask(__name__)

neighbours = []
device_id = os.environ["ID"]

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
    
def stop_software():
    os.system("killall -9 code")

def start_software():
    os.system("cd current; ./code &")

def restart():
    stop_software()
    os.system("rm -rf current/*")
    z = zipfile.ZipFile("files/"+get_latest_time()+".zip", 'r')
    z.extractall("current")
    z.close()
    start_software()

def tick():
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
        restart()
    threading.Timer(2, tick).start()
    


tick()
start_software()

if __name__ == '__main__':
    port = 5000 + int(device_id)
    app.run(port = port, host= "0.0.0.0")
