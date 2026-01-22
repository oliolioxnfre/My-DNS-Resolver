import socket, sys
# TODO: Add any helper functions if you need

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

def make_request(domain, ident):
    return f"0 {domain} {ident}"

def log_response(message):
    with open('resolved.txt', 'a') as fd:
        newMessage = (f"{message['type']} {message['domain']} {message['ip']} {message['id']} {message['flag']}")
        fd.write(newMessage + "\n")


def client(ls_hostname, rudns_port):
    host = ls_hostname
    port = int(rudns_port)
    
    # Clear resolved.txt at start
    with open('resolved.txt', 'w') as fd:
        pass
    
    # Read database
    with open('hostnames.txt', 'r') as fd:
        requests = list(map(lambda l: l.strip().lower(), fd.readlines()))

    # TODO: Write your code here

    request_id = 1
    for domain in requests:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            print(f"[CLIENT] Connected to LS at {host}:{port}")
            msg = make_request(domain, request_id)
            client_socket.send(msg.encode())
            print(f"[CLIENT] Sent request {msg}")
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                response = parse_response(data.decode())
                if response["flag"] == "ns":
                    #log_response(response)
                    continue
                elif response["flag"] == "nx":
                    print(f"[CLIENT] Got NX response: {domain} - Host not found")
                    log_response(response)
                    break
                else:
                    print(f"[CLIENT] Got AA response: {response}")
                    log_response(response)
                    break
            request_id += 1

    print("[CLIENT] Done sending all requests.")            




if __name__ == '__main__':
    args = sys.argv
    client(args[1], args[2])