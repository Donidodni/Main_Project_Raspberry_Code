import time
import RPi.GPIO as GPIO


class Sensor:
    def __init__(self): # 센서 클래스 선언 및 변수 선언 
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.SZH_SENSOR = 15  # 적외선 센서 GPIO 포트 번호
        GPIO.setup(self.SZH_SENSOR, GPIO.IN)

        self.SERVOPINS = [21, 16, 20, 26]  # 21 : 어깨(좌우) / 16 : 어깨 / 20 : 팔꿈치 / 26 : 집게
        self.SERVO_MAX_DUTY = 12  # 서보 최대 180도 위치 주기
        self.SERVO_MIN_DUTY = 3  # 서보 최소 0도 위치 주기
        self.servo = []

        self.RAIL_RELAY = 14  # 레일 릴레이 
        GPIO.setup(self.RAIL_RELAY, GPIO.OUT) # 레일 릴레이 아웃풋 설정


        for i, servopin in enumerate(self.SERVOPINS):
            GPIO.setup(servopin, GPIO.OUT)
            self.servo.append(GPIO.PWM(servopin, 50))
            self.servo[i].start(0)

    

    def SZH_SSBH002(self):
        # 1이면 물체 감지, 0이면 감지 안함
        return not GPIO.input(self.SZH_SENSOR)


    def setServoPos(self, degree, num):
    
        

        if degree > 180: 
            degree = 180
        elif degree < 0:
            degree = 0 

        duty = self.SERVO_MIN_DUTY + (
            degree * (self.SERVO_MAX_DUTY - self.SERVO_MIN_DUTY) / 180.0
        )

        #print("Degree: {} to {}(Duty), Motor Number = {}".format(degree, duty, num))


        for spin in self.servo:
            self.servo[num].ChangeDutyCycle(duty)



    """안전을 위한 홈 포지션 위치 """

    def home_pos(self): # 홈 포즈
        self.setServoPos(97,0) # 컨베이어 방향 이동
        self.setServoPos(90,1) # 어깨 직각 방향 이동
        self.setServoPos(0,2)
        time.sleep(1) # 팔꿈치 최대 앞으로 이동


    def safe_pos(self): # 세이프 포즈 
        self.setServoPos(0,0)
        self.setServoPos(40,1)
        self.setServoPos(0,2)


    """ 컨베이어에서 잡아서 로봇 기준 왼쪽으로 옮기기"""

    def grab_left(self):
        self.setServoPos(0,3)  # 집게 벌리기  # 박수 위치: 컨베이어
        time.sleep(0.5)

        self.setServoPos(150,1) # 팔 내리기
        time.sleep(0.5)
       
        self.setServoPos(180,3) # 집게로 집기  
        time.sleep(1.0)
       
        self.setServoPos(90,1) # 팔 올리기  # 박스 위치: 로봇팔 
        time.sleep(0.5)

        self.setServoPos(180,0) # 어깨 돌리기 (왼쪽으로)
        time.sleep(0.5)

        self.setServoPos(160,1) # 팔 내리기
        time.sleep(0.5)

        self.setServoPos(0,3) # 집게 벌리기   # 박스 위치 : 저장소
        time.sleep(1.0)

        self.setServoPos(60,1) # 팔 올리기
        time.sleep(0.5)

        self.home_pos()


    """ 컨베이어에서 잡아서 반대편으로 넘기기"""

    def grab_side(self):
        self.setServoPos(0,3)  # 집게 벌리기  # 박수 위치: 컨베이어
        time.sleep(0.5)

        self.setServoPos(15,2) # 팔 내리기 
        self.setServoPos(165,1) 
        time.sleep(0.5)
       
        self.setServoPos(180,3) # 집게로 집기  
        time.sleep(1.0)

        self.setServoPos(30,1) # 반대편으로 넘기기 :  어깨
        time.sleep(1)

        self.setServoPos(120,2) # 반대편으로 넘기기 :  팔꿈치
        time.sleep(1)

        self.setServoPos(0,3) # 집게 벌리기   # 박스 위치 : 저장소
        time.sleep(1.0)

        self.home_pos()

    """ 컨베이어에서 잡아서 왼쪽 반대편 으로 넘기기"""

    def grab_side_left(self):

        self.setServoPos(0,3)  # 집게 벌리기  # 박수 위치: 컨베이어
        time.sleep(0.4)

        self.setServoPos(150,1) # 팔 내리기
        time.sleep(0.4)
       
        self.setServoPos(170,3) # 집게로 집기  
        time.sleep(1.0)

        self.setServoPos(90,1) # 팔 올리기  # 박스 위치: 로봇팔
        self.setServoPos(0,2)  
        time.sleep(0.4)

        self.setServoPos(40,0) # 어깨 돌리기 (오른쪽 대각선으로)
        time.sleep(0.5)

        self.setServoPos(30,1) # 반대편으로 넘기기 :  어깨
        time.sleep(0.4)

        self.setServoPos(120,2) # 반대편으로 넘기기 :  팔꿈치
        time.sleep(0.4)

        self.setServoPos(0,3) # 집게 벌리기   # 박스 위치 : 저장소
        time.sleep(1.0)

        self.setServoPos(0,2) # 반대편으로 넘기기 :  팔꿈치
        time.sleep(0.4)

        self.setServoPos(90,1) # 반대편으로 넘기기 :  팔꿈치
        time.sleep(0.4)

        self.home_pos()


    """ 컨베이어에서 잡아서 로봇 기준 오른쪽으로 옮기기"""

    def grab_right(self):
        self.setServoPos(0,3)  # 집게 벌리기  # 박수 위치: 컨베이어
        time.sleep(0.5)

        self.setServoPos(155,1) # 팔 내리기
        time.sleep(0.5)
       
        self.setServoPos(180,3) # 집게로 집기  
        time.sleep(1.0)
       
        self.setServoPos(90,1) # 팔 올리기  # 박스 위치: 로봇팔 
        time.sleep(0.5)

        self.setServoPos(0,0) # 어깨 돌리기 (오른쪽으로)
        time.sleep(0.7)

        self.setServoPos(160,1) # 팔 내리기
        time.sleep(0.5)

        self.setServoPos(0,3) # 집게 벌리기   # 박스 위치 : 저장소
        time.sleep(1.0)

        self.setServoPos(60,1) # 팔 올리기
        time.sleep(0.5)

        self.home_pos()
   
    """전체 모터 가동범위 확인하기"""
       
    def test_motors(self):

        for i in range(0,3):  # 초기 자세 유지
            self.setServoPos(90,i)


        # 어깨 좌우 방향 이동 테스트

        self.setServoPos(0,0)  # 시계방향 시작
        time.sleep(1)

        self.setServoPos(180,0) # 반시계 방향으로 이동
        time.sleep(1)

        # 어깨 앞뒤 방향 이동 테스트

        self.setServoPos(50,1) # 뒤로 넘어가기 : 0 이 뒤로 최대
        time.sleep(1)

        self.setServoPos(180,1) # 앞으로 넘어가기
        time.sleep(1)

        self.setServoPos(90,1) # 직각 서기
        time.sleep(1)


        # 팔꿈치 앞뒤 방향 이동 테스트

        self.setServoPos(0,2) # 앞으로 넘어가기
        time.sleep(1)

        self.setServoPos(180,2) # 뒤로 넘어가기
        time.sleep(1)


        # 집게 그랩 테스트

        self.setServoPos(0,3) # 집게 벌리기
        time.sleep(1)

        self.setServoPos(180,3) # 집게 잡기
        time.sleep(1)
       

    """컨베이어 릴레이 (레일 ON/OFF) 컨트롤"""

    def RAIL_ON(self):
        GPIO.output(self.RAIL_RELAY,1)

    def RAIL_OFF(self):
        GPIO.output(self.RAIL_RELAY,0)


    def BEGIN1(self): # BEGIN1 을 받았을 때 작동되는 분류 시퀀스 

        self.RAIL_OFF()
        time.sleep(0.5)

        self.grab_left()

        self.home_pos()
        time.sleep(0.5)

    def BEGIN2(self): # BEGIN2 을 받았을 때 작동되는 분류 시퀀스

        self.RAIL_OFF()
        time.sleep(0.5)

        self.grab_right()

        self.home_pos()
        time.sleep(0.5)

    def BEGIN3(self): # BEGIN1 을 받았을 때 작동되는 분류 시퀀스 (빨간색)

        self.RAIL_OFF()
        time.sleep(0.5)

        self.grab_side_left()

        self.home_pos()
        time.sleep(0.5)

    def BEGIN4(self):
        self.RAIL_OFF()
        time.sleep(0.5)



# ass = Sensor()
# ass.home_pos()
# ass.grab_left()


# while(1):
#     ass.setServoPos(10,3) # 집게 벌리기
#     time.sleep(1)

#     ass.setServoPos(100,3) # 집게 잡기
#     time.sleep(1)