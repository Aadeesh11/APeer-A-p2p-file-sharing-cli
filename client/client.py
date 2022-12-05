import os
import threading
import sys
import debug
import jsonUtils
import socket
import traceback
import time

IP_OF_TRACKER = socket.gethostbyname(socket.gethostname())
PORT_OF_TRACKER = 3000
TRACKER_ADDR = (IP_OF_TRACKER, PORT_OF_TRACKER)
FORMAT = "utf-8"
SIZE = 1024

MY_IP = socket.gethostbyname(socket.gethostname())
MY_PORT = sys.argv[1]
MY_ADDR = (MY_IP, MY_PORT)


def handlePeerConn(addr):
    pass


def mainLoop():
    pass


def getFFromPeer(host: str, port: int, folderOrFilePathArray: list):
    for i in range(1, 10):
        time.sleep(2)
        print('HELL YEAH')


def main():

    # peerConnThread = threading.Thread(target=mainLoop, args=[])
    # peerConnThread.start()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(TRACKER_ADDR)

    disCon = False

    while True:
        try:
            data = client.recv(SIZE).decode(FORMAT)
            cmd, msg = data.split("@")
            if cmd == "ALL":
                print(f"[SERVER]: {msg}")
            elif cmd == "OK":
                print(f"{msg}")
            elif cmd == "ERROR":
                print(f'{msg}')
            elif cmd == 'RUPDATE':
                print(f'{msg}')
            elif cmd == 'RLIST':
                jsonUtils.strToClientJson(msg)
                print(f'List fetched, check client.json file and provide the exact folder name/ file name you want to download as well as the IP:Port of the host')
            else:
                print("KUCH GADBAD")
        except:
            traceback.print_exc()

        while True:
            x = input(
                ">Type your command or press enter to know all commands or C to exit\n>")
            debug.pr(f'{x} pressed')
            cmd = x
            if x == 'C':
                client.send(cmd.encode(FORMAT))
                disCon = True
                break
            elif (x == "LIST"):
                client.send(cmd.encode(FORMAT))
                break
            elif (x == "UPDATE"):
                cmd += '@' + jsonUtils.path_string()
                client.send(cmd.encode(FORMAT))
                break
            elif x == '':
                client.send('CMDLIST@'.encode(FORMAT))
                break
            else:
                x = x.split(" ")
                if (len(x) < 4):
                    print("Invalid usage")
                else:
                    threading.Thread(target=getFFromPeer, args=[
                        x[1], int(x[2]), [i for i in range(3, len(x))]]).start()

        if disCon:
            break

    debug.pr('Server disconnected')
    client.close()


if __name__ == '__main__':
    main()
