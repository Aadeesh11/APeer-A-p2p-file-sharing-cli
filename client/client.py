import os
import threading
import sys
import debug
import jsonUtils
import socket
import traceback
import time

if sys.argv[1] == None or sys.argv[2] == None or sys.argv[3] == None:
    print("Usage: python client.py <tracker ip> <tracker port> <your port>")
    exit()

IP_OF_TRACKER = sys.argv[1]
PORT_OF_TRACKER = int(sys.argv[2])
TRACKER_ADDR = (IP_OF_TRACKER, PORT_OF_TRACKER)
FORMAT = "utf-8"
SIZE = 2048

MY_IP = '127.0.0.1'

MY_PORT = sys.argv[3]
MY_ADDR = (MY_IP, int(MY_PORT))
CLIENT_TO_SHARE = 'toShare'


def handlePeerConn(conn: socket.socket, addr):

    print(f"[NEW CONNECTION] {addr} connected.")
    debug.pr('started')

    # TODO: Locate the file/Folder and get path
    requestedPath = conn.recv(SIZE).decode()

    if (not os.path.exists(requestedPath)):
        conn.send("ERROR:No such path exits, try to fetch the list again".encode())

    if (os.path.isdir(requestedPath)):
        # its a folder transfer all its contents
        # start the walk from the requestedPath.
        requestedFolderName = requestedPath
        for rootSePath, _, files in os.walk(requestedFolderName):

            # send file Name: NAME:rootSePath join fileName
            # then keep sending data
            for file in files:
                fileName = os.path.join(rootSePath, file)
                relPath = os.path.relpath(fileName, CLIENT_TO_SHARE)
                fileSize = os.path.getsize(fileName)

                print(f'sending {relPath}')

                with open(fileName, 'rb') as f:
                    conn.sendall(relPath.encode() + b'\n')
                    conn.sendall(str(fileSize).encode() + b'\n')

                    while True:
                        data = f.read(SIZE)
                        if not data:
                            break
                        conn.sendall(data)
    else:
        # its a file
        relPath = os.path.relpath(requestedPath, CLIENT_TO_SHARE)
        fileSize = os.path.getsize(requestedPath)

        print(f'sending {relPath}')

        with open(requestedPath, 'rb') as f:
            conn.sendall(relPath.encode() + b'\n')
            conn.sendall(str(fileSize).encode() + b'\n')

            while True:
                data = f.read(SIZE)
                if not data:
                    break
                conn.sendall(data)

    print('Done')
    conn.close()
    return


def mainLoop():
    # create a socket to listen for incoming file requests
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind
    sock.bind(MY_ADDR)
    # listen
    sock.listen()

    debug.pr(f'My file Server started: {MY_ADDR}')

    shutdown = False
    # start while loop
    while not shutdown:
        try:
            debug.pr("Listening for connections")
            # accept connections
            clientSock, clientAddr = sock.accept()
            # None, puts in blocking mode
            clientSock.settimeout(None)

            # delegate the request to handlePeerConn on a new thread nd start it
            trd = threading.Thread(
                target=handlePeerConn, args=[clientSock, clientAddr])
            trd.start()
        except KeyboardInterrupt:
            # this allows ctrl+C to stop the program
            print('shutting main loop ctrl+C')
            shutdown = True
            continue
        except:
            traceback.print_exc()
            continue
    # end while loop

    debug.pr('Main loop exiting')

    # close the socket
    sock.close()
    return


def getFFromPeer(host: str, port: int, folderOrFilePath: str, x: str):

    # send the path to peer
    # for file: <path root childDir file>
    # for folder: <path root childDir

    pathTofolder = os.path.join('recv', host + str(port), x)
    os.makedirs(pathTofolder, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.send(folderOrFilePath.encode())
    with sock, sock.makefile('rb') as clientfile:
        while True:
            raw = clientfile.readline()

            # No more files. Break!
            if not raw:
                break

            filename = raw.strip().decode()
            length = int(clientfile.readline())
            print(
                f'Downloading {filename}...\n  Expecting {length:,} bytes...', end='', flush=True)

            # make the neccessary directory for the file to live in
            path = os.path.join(pathTofolder, filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Read the data in chunks to handle large files.
            with open(path, 'wb') as f:
                while length:
                    chunk = min(length, SIZE)
                    data = clientfile.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    length -= len(data)
                else:  # only runs if while doesn't break and length==0
                    print('Complete')
                    continue

            # some error causesd socket to close early.
            print('Incomplete')
            break
    return


def main():

    peerConnThread = threading.Thread(target=mainLoop, args=[])
    peerConnThread.start()

    # Socket for talking to the tracker and getting files metadata.
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(TRACKER_ADDR)

    # is disconnected from the tracker.
    disCon = False

    while True:
        try:
            data = client.recv(SIZE).decode(FORMAT)
            cmd, msg = data.split("@")
            if cmd == "ALL":
                print(f"[Commands available]:\n{msg}\n")
            elif cmd == "OK":
                print(f"{msg}")
            elif cmd == "ERROR":
                print(f'{msg}')
            elif cmd == 'RUPDATE':
                print(f'{msg}')
            elif cmd == 'RLIST':
                jsonUtils.strToClientJson(msg)
                print('Available hosts: Folders')
                jsonUtils.printTreeOnScreen()
                print(f'\nList fetched\nCheck client.json file and provide the "copy_Paste_This" field of the folder/file you want to download as well as the IP:Port of the host to the GET command')
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
                cmd += '@' + str(MY_PORT)
                client.send(cmd.encode(FORMAT))
                disCon = True
                break
            elif (x == "LIST"):
                client.send(cmd.encode(FORMAT))
                break
            elif (x == "UPDATE"):
                cmd += '@' + str(MY_PORT) + '@'
                cmd += jsonUtils.tree_to_json()
                client.send(cmd.encode(FORMAT))
                break
            elif x == '':
                client.send('CMDLIST@'.encode(FORMAT))
                break
            else:
                x = x.split(" ")
                if (len(x) < 4 or x[0] != "GET"):
                    print("Invalid usage")
                else:
                    nameOfFolder = input(
                        "What do you want to name the folder\nIt will be created in recv/<host><port>/<folderName>\n>").strip()
                    targetFolder = ''
                    for i in range(3, len(x) - 1):
                        targetFolder += x[i] + ' '
                    targetFolder += x[len(x) - 1]
                    threading.Thread(target=getFFromPeer, args=[
                                     x[1], int(x[2]), targetFolder, nameOfFolder]).start()
                    print("you can send other GETs as well since this is multithreaded, or press C, to disconnect from server and let the download continue in background")
                    break

        if disCon:
            break

    debug.pr('Server disconnected')
    client.close()


if __name__ == '__main__':
    main()
