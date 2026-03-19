from pop import Switches, Leds, delay

# --- 변수 지정 ---
led = Leds()
switch = Switches()

# --- 함수 지정 ---
def wait_sec(n):
    delay(n * 1000)

# ----------------
# led 껐다 키기
led.allOn()
wait_sec(2)
led.allOff()
wait_sec(2)

# led 차례로 켜기
for i in range(0, 8):
    led[i].on()
    wait_sec(1)

# led 역순으로 끄기
for i in range(7, -1, -1):
    led[i].off()
    wait_sec(1)

led.allOff()

# switch 상태 확인
data = switch[0].read()
print(data)

while True:
    btn_state1 = switch[0].read()
    btn_state2 = switch[1].read()

    if not btn_state1:
        for i in range(0, 8, 2):
            led[i].on()
        for i in range(1, 8, 2):
            led[i].off()

    elif not btn_state2:
        for i in range(0, 8, 2):
            led[i].off()
        for i in range(1, 8, 2):
            led[i].on()

    else:
        led.allOff()

    delay(100)