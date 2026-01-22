This is a custom DNS Resolver written in Python. I created it to understand the inner workings of Domain Name Resolution.
This DNS Resolver works on Local Networks with multiple machines, using sockets and TCP communication in order to connect multiple DNS to each other and resolve recursively map a Domain name to an IP
Client -> Local Server -> Root Server -> TLD1 -> TLD2 -> Authoritative server
