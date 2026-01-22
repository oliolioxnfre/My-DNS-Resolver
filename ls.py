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
    
def make_request(domain, ident):
    return f"0 {domain} {ident}"

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

def parse_response(message):
    parts = message.strip().split()
    if len(parts) != 5 or parts[0] != "1":
        raise ValueError(f"Invalid RU-DNS response format: {message}")
    return {
        "type": parts[0],
        "domain": parts[1],
        "ip": parts[2],
        "id": parts[3],
        "flag": parts[4]
    }

def log_response(message):
    with open('lsresponses.txt', 'a') as fd:
        fd.write(message + "\n")

def ls(rudns_port):
    # TODO: Write your code here
    cache = {}
    query_count = {}  # Track how many times each domain has been queried
    lsd = loadlsd()
    port = int(rudns_port)
    host = ""  # Bind to all network interfaces (allows remote connections)
    # Clear lsresponses.txt at start
    with open('lsresponses.txt', 'w') as fd:
        pass
    # Clear cache.txt at start
    with open('cache.txt', 'w') as fd:
        pass

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"[LS] Listening on {host}:{port}")
        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"[LS] Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    req = parse_request(data.decode())
                    domain = req["domain"]
                    id = req["id"]
                    print(f"[LS] Got request for {domain} {id}")
                    
                    # Increment query count for this domain
                    query_count[domain] = query_count.get(domain, 0) + 1
                    print(f"[LS] Query count for {domain}: {query_count[domain]}")

                    if domain in cache:
                        ip = cache[domain]
                        response = make_response(domain, ip, id, "aa")
                        conn.send(response.encode())
                        print(f"[LS] Sent cache response to client for {domain} {id}")
                        log_response(response)
                        break
                    else:
                        rs_host = lsd["rs_host"]
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                            client_socket.connect((rs_host, port))
                            print(f"[LS] Connected to RS at {rs_host}:{port}")
                            msg = make_request(domain, id)
                            client_socket.send(msg.encode())
                            print(f"[LS] Sent request to RS for {domain} {id}")

                            #receive RS message
                            rs_response = client_socket.recv(1024)
                            rs_resp = parse_response(rs_response.decode())
                            flag = rs_resp["flag"]
                            ip = rs_resp["ip"]
                            if flag == "aa": #if authoritative answer received cache it and respond to client
                                # Only cache after 3rd query
                                if query_count[domain] >= 3:
                                    cache[domain] = ip
                                    print(f"[LS] Cached {domain} -> {ip}")
                                response = make_response(domain, ip, id, flag)
                                conn.send(response.encode())
                                log_response(response)
                                print(f"[LS] Sent response to client for {domain} {id}")
                                break
                            elif flag == "ns": #if RS sent ns LS, send it to TS1/TS2/AS
                                
                                #above is the forced log bs


                                tld_server = rs_resp["ip"]
                                serverType = tld_server
                                print(f"TLD TLD TLD SERVER: {tld_server}")
                            
                                serverType = tld_server

                                dummyresponse = make_response(domain, tld_server, id, flag)
                                conn.send(dummyresponse.encode())



                                print(f"[LS] Forwarding connection request to {serverType} at {tld_server}:{port}")
                                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ts_socket:
                                    ts_socket.connect((tld_server, port))
                                    print(f"[LS] Connected to {serverType} at {tld_server}:{port}")
                                    ts_socket.send(make_request(domain, id).encode())
                                    print(f"[LS] Sent request to {serverType} for {domain} {id}")
                                    ts_response = ts_socket.recv(1024)
                                    ts_resp = parse_response(ts_response.decode())
                                    flag = ts_resp["flag"]
                                    ip = ts_resp["ip"]
                                    if flag == "aa":
                                        # Only cache after queries > 3
                                        if query_count[domain] > 3:
                                            cache[domain] = ip
                                            print(f"[LS] Cached {domain} -> {ip}")
                                            with open('cache.txt', 'a') as fd:
                                                fd.write(f"{domain} {ip}\n")
                                        response = make_response(domain, ip, id, flag)
                                        conn.send(response.encode())
                                        log_response(response)
                                        break
                                    elif flag == "ns" or flag == "nx":
                                        as_server = lsd["as_host"]
                                        print(f"[LS] Forwarding connection request to AS at {as_server}:{port}")
                                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as as_socket:
                                            as_socket.connect((as_server, port))
                                            print(f"[LS] Connected to AS at {as_server}:{port}")
                                            as_socket.send(make_request(domain, id).encode())
                                            print(f"[LS] Sent request to AS for {domain} {id}")
                                            as_response = as_socket.recv(1024)
                                            as_resp = parse_response(as_response.decode())
                                            flag = as_resp["flag"]
                                            ip = as_resp["ip"]
                                            if flag == "aa":
                                                # Only cache after 3rd query
                                                if query_count[domain] >= 3:
                                                    cache[domain] = ip
                                                    print(f"[LS] Cached {domain} -> {ip}")
                                            response = make_response(domain, ip, id, flag)
                                            conn.send(response.encode())
                                            log_response(response)
                                            break
                                    elif flag == "nx": #if non-existent domain respond with nx
                                        response = make_response(domain, "0.0.0.0", id, flag)
                                        conn.send(response.encode())
                                        log_response(response)
                                        print(f"[LS] Sent nx response to client for {domain} {id}")
                                        break

                                    
                            elif flag == "nx": #if non-existent domain respond with nx
                                response = make_response(domain, "0.0.0.0", id, flag)
                                conn.send(response.encode())
                                log_response(response)
                                print(f"[LS] Sent nx response to client for {domain} {id}")
                                break
                print("[LS] Connection to client closed.")
                conn.close()

                    
if __name__ == '__main__':
    args = sys.argv
    ls(args[1])