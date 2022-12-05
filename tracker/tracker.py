import socket
import threading
import jsonUtils
import traceback

IP = socket.gethostbyname(socket.gethostname())
PORT = 3000
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

# ALL,OK,ERROR,RLIST,RUPDATE


def handle_client(conn, addr, jsonUtil):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the File Server.".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
        print(cmd)

        if cmd == "LIST":
            try:
                data = "RLIST@"
                data += jsonUtil.sendJsonFileData()
                conn.send(data.encode(FORMAT))
            except:
                traceback.print_exc()
                conn.send("ERROR@List FAILED, TRY AGAIN".encode(FORMAT))

        elif cmd == "UPDATE":
            try:
                toShareFolderJson = data[1]
                jsonUtil.updateJsonFile(addr, toShareFolderJson)
                conn.send("RUPDATE@UPDATE SUCCESS!".encode(FORMAT))
            except:
                traceback.print_exc()
                conn.send("ERROR@UPDATE FAILED, TRY AGAIN".encode(FORMAT))

        elif cmd == "C":
            try:
                jsonUtil.updateJsonFile(addr, None)
            except:
                traceback.print_exc()
            break

        else:
            data = "ALL@"
            data += "LIST: List all the files from the server.\n"
            data += "UPDATE: UPDATE your records in the toShare folder, use only when you changed something in the toShare folder.\n"
            data += "C: Disconnect from the server.\n"
            data += "GET <ip> <port> <path to folder(space seperated)>"

            conn.send(data.encode(FORMAT))

    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()


def main():
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")
    jsonUtil = jsonUtils.RecordsStructure()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(
            target=handle_client, args=(conn, addr, jsonUtil))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


if __name__ == "__main__":
    main()
