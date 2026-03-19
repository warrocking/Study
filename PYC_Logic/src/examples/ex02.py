# 숫자가 랜덤 숫자로 계속 돌리고 있는데, 버튼을 눌러서 함수가 멈추고, 멈췄을 떄의 숫자가 입력한 숫자와 같다면 종료, 아니라면 재 실행
from pop import Switches, Leds, delay
import random
# --- 변수 지정 ---
led = Leds()
switch = Switches()

# --- 함수 지정 ---
def wait(n):
    delay(n * 1000)

# ----------------
value = int(input("원하는 숫자는 : "))
while True:
    btn_state1 = switch[0].read()
    btn_state2 = switch[1].read()
    randomValue = random.randrange(0, value+1)
    led[0].on()
    delay(10)
    led[0].off()
    if not btn_state1:
        print("종료 버튼 입력")
        break
    elif not btn_state2:
        print(randomValue)
        if randomValue == value:
            break    
    
print("종료")