import socket, sys
# TODO: Add any helper functions if you need
def loadtsd1():
    ts1_database = {}
    with open('ts1database.txt', 'r') as fd:
        for line in fd:
            parts = line.strip().split()
            if len(parts) == 2: 
                domain, ip = parts
                ts1_database[domain] = ip
    return ts1_database

def parse_request(message):
    parts = message.strip().split()
    if len(parts) != 3 or parts[0] != "0":
        raise ValueError(f"Invalid RU-DNS request format: {message}")
    return {
        "type": parts[0],
        "domain": parts[1],
        "id": parts[2]
    }

def make_response(domain, ip, ident, flag):
    return f"1 {domain} {ip} {ident} {flag}"

def log_response(message):
    with open('ts1responses.txt', 'a') as fd:
        fd.write(message + "\n")

def ts1(rudns_port):
    # TODO: Write your code here
    ts1d = loadtsd1()
    port = int(rudns_port)
    host = ""
    with open('ts1responses.txt', 'w') as fd:
        pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"[TS1] listening on {host}:{port}")
        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"[TS1] Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    req = parse_request(data.decode())
                    domain = req["domain"]
                    id = req["id"]
                    print(f"[TS1] Got request for {domain} {id}")
                    if domain in ts1d:
                        ip = ts1d[domain]
                        response = make_response(domain, ip, id, "aa")
                        conn.send(response.encode())
                        print(f"[TS1] Sent aa response for {domain} {id}")
                        log_response(response)
                        break
                    else:
                        response = make_response(domain, "0.0.0.0", id, "nx")
                        conn.send(response.encode())
                        print(f"[TS1] Sent nx response for {domain} {id}")
                        log_response(response)
                        break
                print("[TS1] Connection to client closed.")
                conn.close()

if __name__ == '__main__':
    args = sys.argv
    ts1(args[1])