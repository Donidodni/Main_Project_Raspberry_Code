import socket_p

# 서버의 IP 주소와 포트 번호
host_ip = '192.168.0.215'
port = 6667

if __name__ == "__main__":
    a = socket_p.socket_p(host_ip, port)
    a.server_p()

