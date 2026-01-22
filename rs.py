import socket, sys
# TODO: Add any helper functions if you need
def loadlsd():
    with open('lsdatabase.txt', 'r') as fd:
        lines = [line.strip().lower() for line in fd.readlines()]
        lsd = {
            "ts1_tld": lines[0], 
            "ts2_tld": lines[1],
            "rs_host": lines[2],
            "ts1_host": lines[3],
            "ts2_host": lines[4],
            "as_host": lines[5],
        }
        return lsd
    
def loadrsd():
    rs_database = {}
    with open('rsdatabase.txt', 'r') as fd:
        for line in fd:
            parts = line.strip().split()
            if len(parts) == 2:
                domain, ip = parts
                rs_database[domain] = ip
    return rs_database

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
    with open('rsresponses.txt', 'a') as fd:
        fd.write(message + "\n")


def rs(rudns_port):
    # TODO: Write your code here
    rsd = loadrsd()
    lsd = loadlsd()
    port = int(rudns_port)
    host = ""
    with open('rsresponses.txt', 'w') as fd:
        pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"[RS] listening on {host}:{port}")
        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"[RS] Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    req = parse_request(data.decode())
                    domain = req["domain"]
                    id = req["id"]
                    print(f"[RS] Got request for {domain} {id}")
                    
                    if domain in rsd:
                        ip = rsd[domain]
                        response = make_response(domain, ip, id, "aa")
                        conn.send(response.encode())
                        print(f"[RS] Sent aa response for {domain} {id} {ip}")
                        log_response(response)
                        break
                    else:
                        tld = domain.split('.')[-1]
                        print(f"[RS] TLD extracted: {tld}")
                        if tld == lsd["ts1_tld"] or tld == lsd["ts2_tld"]:
                            if tld == lsd["ts1_tld"]:
                                ip = lsd["ts1_host"]
                            else:
                                ip = lsd["ts2_host"]
                            response = make_response(domain, ip, id, "ns")
                            conn.send(response.encode())
                            print(f"[RS] Sent ns response for {domain} {id}")
                            log_response(response)
                            break
                        else:
                            response = make_response(domain, "0.0.0.0", id, "nx")
                            conn.send(response.encode())
                            print(f"[RS] Sent nx response for {domain} {id}")
                            log_response(response)
                            break
                print("[RS] Connection to LS closed.")
                conn.close()
if __name__ == '__main__':
    args = sys.argv
    rs(args[1])