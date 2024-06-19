import pickle
import struct
import socket
import threading
import senser
import time
import signal
import sys


class socket_p:
    def __init__(self, ip, port):
        # 서버의 IP 주소와 포트 번호
        self.host_ip = ip
        self.port = port
        self.lock = threading.Lock()

        self.A_senser = senser.Sensor()
        self.RECV_TH_KEY = True # 소켓 통신 제어
        self.SENSER_SHZ = False # 적외선 센서 제어
        self.PreState = False # 0 에서 1로 될 때 감지
        self.A_senser.RAIL_OFF()

        self.modify_value = 90
        self.sener_count = 0 

    def server_p(self):
        # 소켓 생성
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 소켓과 IP, 포트를 바인딩
        server_socket.bind((self.host_ip, self.port))

        # 클라이언트로부터의 연결을 대기
        server_socket.listen(10)  # 최대 연결 수
        print(f"서버가 {self.host_ip}:{self.port} 에서 실행 중입니다.")

        while True:
            # 클라이언트로부터 연결 요청이 들어올 때까지 대기
            client_socket, client_address = server_socket.accept()
            print(f"{client_address} 클라이언트가 연결되었습니다.")
            self.RECV_TH_KEY = True
            recv_th = threading.Thread(target=self.server_recv, args=(client_socket, client_address))
            recv_th.start()

            try:
                while self.RECV_TH_KEY:
                    # 이곳에 센서 감지 및 송신
                    self.SZH_Info(client_socket, client_address)

            except:
                self.socketend(client_socket, client_address)
                client_socket.close()
                return

            client_socket.close()
            self.RECV_TH_KEY = False
            recv_th.join()

    # 적외선 센서로 물체 감지
    def SZH_Info(self, client_socket, client_address):
        
        
        self.SENSER_SHZ = self.A_senser.SZH_SSBH002()  # 물체 감지

        if self.PreState is False and self.SENSER_SHZ:
            self.senser_count = 0
            self.server_send(client_socket, client_address, "ST/PROC:GRAB/END")
            self.A_senser.RAIL_OFF()
            print("센서 감지")         
            time.sleep(3)

        elif(self.PreState and self.SENSER_SHZ is False):
            self.sener_count = self.sener_count + 1

        else:
            self.senser_count = 0

        # elif self.A_senser.SZH_SSBH002():
        #     self.A_senser.RAIL_OFF()

        self.PreState = self.SENSER_SHZ

        if(self.sener_count < 5):
            self.PreState = True

    # 클라이언트에게 메시지 수신 (기계 제어용 수신)
    def server_recv(self, client_socket, client_address):
        client_socket.settimeout(3)
        while self.RECV_TH_KEY:
            try:
                data_decoding = client_socket.recv(1024)
                data = data_decoding.decode('utf-16')
                print("수신:",data)

                self.robot(client_socket, client_address, data)  # 여기서 명령 작성

            except socket.timeout:
                pass
            except Exception as err:  # 예외 발생 시
                self.socketend(client_socket, client_address)
                return

    # 클라이언트에게 메시지 전송
    def server_send(self, client_socket, client_address, message):
        # 이곳에 보낼 메시지 코딩
        try:
            client_socket.sendall(message.encode())
        except Exception as err:
            print("Error : server_send Exception")
            return
        
    # 소켓 종료시킬 때 사용
    def socketend(self, client_socket, client_address):
        self.RECV_TH_KEY = False
        self.server_send(client_socket, client_address, "END")

        print(f"{client_address} 클라이언트와의 연결이 종료되었습니다.")
        return

    # 로봇 제어에 사용
    # 받는 신호
    def robot(self, client_socket, client_address, Message):
        result = []

        if Message == "END":
            self.socketend(client_socket, client_address)
            return

        elif Message == "START":
            self.A_senser.home_pos()
            self.A_senser.RAIL_ON()
            self.SENSER_SHZ = True
            # self.START_LOOP = True
            
        elif Message == "STOP":
            self.A_senser.safe_pos()
            self.A_senser.RAIL_OFF()
            self.SENSER_SHZ = False

        elif '/' in Message:
            Message_s = Message.split('/')

            # 각 부분을 ':' 기준으로 다시 분할
            for part in Message_s:
                if ':' in part:
                    sub_parts = part.split(':')
                    result.append(sub_parts)

                    if 'GREEN' in Message:
                        self.A_senser.BEGIN1()
                        self.server_send(client_socket, client_address, "ST/PROC:DONE/END")
                        print("ST/PROC:DONE/END")
                    
                    elif 'RED' in Message:
                        self.A_senser.BEGIN2()
                        self.server_send(client_socket, client_address, "ST/PROC:DONE/END")
                        print("ST/PROC:DONE/END")

                    elif 'YELLOW' in Message:
                        self.A_senser.BEGIN3()
                        self.server_send(client_socket, client_address, "ST/PROC:DONE/END")
                        print("ST/PROC:DONE/END")

                    elif 'FAIL' in Message:
                        self.A_senser.BEGIN4() #RAIL OFF
                        self.server_send(client_socket, client_address, "ST/PROC:DONE/END")
                        self.SENSER_SHZ = True
                        print("ST/PROC:DONE/END")

                    elif 'RETRY' in Message:
                        self.server_send(client_socket, client_address, "ST/PROC:RETRY/END")
                        print("ST/PROC:RETRY/END")

                    else :
                        self.A_senser.RAIL_ON()
                        self.SENSER_SHZ = True

                else:
                    result.append(part)             

        else:
            
            if ':' in Message:
                sub_parts = Message.split(':')
                result.append(sub_parts)
            else:
                result.append(Message)

        # 분할된 메시지에서 명령어를 찾음
        for i in result:
            if isinstance(i, list):
                if "HOME" in i:
                    self.modify_value = 90
                    print("yes")
                    self.A_senser.home_pos()

                elif "M1_P10" in i:
                    print("Move M1 +10")
                    self.modify_value += 10
                    self.A_senser.setServoPos(self.modify_value, 0)
                
                elif "M2_P10" in i:
                    print("Move M2 +10")
                    self.modify_value += 10
                    self.A_senser.setServoPos(self.modify_value,1)

                elif "M3_P10" in i:
                    print("Move M3 +10")
                    self.modify_value += 10
                    self.A_senser.setServoPos(self.modify_value,2)

                elif "M4_P10" in i :
                    print("Move M4 +10")
                    self.modify_value += 10
                    self.A_senser.setServoPos(self.modify_value,3)


                elif "M1_M10" in i:
                    print("Move M1 -10")
                    self.modify_value -= 10
                    self.A_senser.setServoPos(self.modify_value,0)

                elif "M2_M10" in i:
                    print("Move M2 -10")
                    self.modify_value -= 10
                    self.A_senser.setServoPos(self.modify_value,1)

                elif "M3_M10" in i:
                    print("Move M3 -5")
                    self.modify_value -= 10
                    self.A_senser.setServoPos(self.modify_value,2)

                elif "M4_M10" in i:
                    print("Move M4 -5")
                    self.modify_value -= 10
                    self.A_senser.setServoPos(self.modify_value,3)


                elif "RAIL_ON" in i:
                    print("RAIL ON")
                    self.A_senser.RAIL_ON()
                
                elif "RAIL_OFF" in i:
                    print("RAIL OFF")
                    self.A_senser.RAIL_OFF()
                    


        