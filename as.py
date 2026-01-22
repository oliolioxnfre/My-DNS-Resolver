import socket, sys
# TODO: Add any helper functions if you need
def loadAsd(): 
    as_database = {}
    with open('asdatabase.txt', 'r') as fd:
        for line in fd:
            parts = line.strip().split()
            if len(parts) == 2:
                domain, ip = parts
                as_database[domain] = ip
    return as_database
# `as` is a keyword, so this function is called a_s

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
    with open('asresponses.txt', 'a') as fd:
        fd.write(message + "\n")

def a_s(rudns_port):
    # TODO: Write your code here
    asd = loadAsd()
    port = int(rudns_port)
    host = ""
    with open('asresponses.txt', 'w') as fd:
        pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"[AS] listening on {host}:{port}")
        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"[AS] Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    req = parse_request(data.decode())
                    domain = req["domain"]
                    id = req["id"]
                    print(f"[AS] Got request for {domain} {id}")
                    if domain in asd:
                        ip = asd[domain]
                        response = make_response(domain, ip, id, "aa")
                        conn.send(response.encode())
                        print(f"[AS] Sent aa response for {domain} {id}")
                        log_response(response)
                        break
                    else:
                        response = make_response(domain, "0.0.0.0", id, "nx")
                        conn.send(response.encode())
                        print(f"[AS] Sent nx response for {domain} {id}")
                        log_response(response)
                        break
                print("[AS] Connection to client closed.")
                conn.close()

if __name__ == '__main__':
    args = sys.argv
    a_s(args[1])