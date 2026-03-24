
# import pop
# from pop import delay

# # ... (기존 초기화 동일)

# # 1) 메뉴 동작 함수(여기에 실제 기능 연결)
# def sw0_env(): print("SW0 -> ENV")
# def sw0_battery(): print("SW0 -> Battery")
# def sw0_stopwatch(): print("SW0 -> StopWatch")
# def sw0_timer(): print("SW0 -> Timer")
# def sw0_night(): print("SW0 -> Night")
# def sw0_exit(): print("SW0 -> Exit")

# def sw1_env(): print("SW1 -> ENV Back")
# def sw1_battery(): print("SW1 -> Battery Back")
# def sw1_stopwatch(): print("SW1 -> StopWatch Back")
# def sw1_timer(): print("SW1 -> Timer Back")
# def sw1_night(): print("SW1 -> Night Back")
# def sw1_exit(): print("SW1 -> Exit Back")

# # 2) 버튼/레벨별 액션 테이블
# SW0_ACTIONS = {
#     1: sw0_env,
#     2: sw0_battery,
#     3: sw0_stopwatch,
#     4: sw0_timer,
#     5: sw0_night,
#     6: sw0_exit,
# }
# SW1_ACTIONS = {
#     1: sw1_env,
#     2: sw1_battery,
#     3: sw1_stopwatch,
#     4: sw1_timer,
#     5: sw1_night,
#     6: sw1_exit,
# }

# def run_action(action_table, level):
#     fn = action_table.get(level)
#     if fn is not None:
#         fn()

# menu_y = [8, 16, 24, 32, 40, 48]
# prev_level = None
# prev_btn0 = True
# prev_btn1 = True

# while True:
#     btn_0 = btn[0].read()   # 눌림=False
#     btn_1 = btn[1].read()

#     raw = poten.read()
#     level = (raw * 6) // 4096 + 1
#     if level < 1:
#         level = 1
#     elif level > 6:
#         level = 6

#     # 화면은 level 변경 시에만 다시 그림
#     if level != prev_level:
#         display.clearDisplay()
#         display.setCursor(0, 5)
#         display.setTextSize(1)
#         display.print("1.ENV check\n2.Battery\n3.StopWatch\n4.Timer\n5.Night\n6.Exit")

#         for i, y in enumerate(menu_y, start=1):
#             if i == level:
#                 display.fillCircle(100, y, 4, display.WHITE)
#             else:
#                 display.drawCircle(100, y, 4, display.WHITE)

#         display.display()
#         prev_level = level

#     # 버튼 1회 클릭(에지 감지)
#     if prev_btn0 and (not btn_0):
#         run_action(SW0_ACTIONS, level)

#     if prev_btn1 and (not btn_1):
#         run_action(SW1_ACTIONS, level)

#     # 중요: 이전 상태 갱신 (없으면 꾹 눌렀을 때 반복 인식됨)
#     prev_btn0 = btn_0
#     prev_btn1 = btn_1

#     delay(30)






from time import time

def read_level():
    raw = poten.read()
    level = (raw * 6) // 4096 + 1
    if level < 1:
        level = 1
    elif level > 6:
        level = 6
    return level

def draw_main_static():
    display.clearDisplay()
    display.setTextSize(1)
    display.setCursor(0, 5)
    display.print("1.ENV check\n2.Battery\n3.StopWatch\n4.Timer\n5.Night\n6.Exit")
    for y in menu_y:
        display.drawCircle(100, y, 4, display.WHITE)  # 비선택 원
    display.display()

def draw_cursor(old_level, new_level):
    # 이전 선택 원 -> 비선택 원으로 복구
    if old_level is not None:
        y_old = menu_y[old_level - 1]
        display.fillCircle(100, y_old, 3, display.BLACK)
        display.drawCircle(100, y_old, 4, display.WHITE)

    # 새 선택 원 -> 채움
    y_new = menu_y[new_level - 1]
    display.fillCircle(100, y_new, 4, display.WHITE)
    display.display()

def settle_level(first_level, settle_sec=0.3):
    # 0.3초 동안 값이 바뀌면 타이머 리셋 -> 최종 안정값 선택
    stable = first_level
    deadline = time() + settle_sec

    while time() < deadline:
        v = read_level()
        if v != stable:
            stable = v
            deadline = time() + settle_sec
        delay(20)

    return stable

def main():
    prev_btn0 = True
    prev_btn1 = True

    draw_main_static()
    level = read_level()
    draw_cursor(None, level)

    while True:
        btn_0 = btn[0].read()
        btn_1 = btn[1].read()

        now_level = read_level()

        # poten 값 변동 시: 0.3초 안정화 후 원만 갱신
        if now_level != level:
            new_level = settle_level(now_level, 0.3)
            if new_level != level:
                draw_cursor(level, new_level)
                level = new_level

            # 안정화 중 눌린 버튼 입력은 무시
            prev_btn0 = btn[0].read()
            prev_btn1 = btn[1].read()
            delay(500)   # 요청하신 0.5초 주기
            continue

        # 버튼 1회 입력(에지)
        if prev_btn0 and (not btn_0):
            run_action(SW0_ACTIONS, level)
            draw_main_static()
            draw_cursor(None, level)
            prev_btn0 = btn[0].read()
            prev_btn1 = btn[1].read()

        elif prev_btn1 and (not btn_1):
            run_action(SW1_ACTIONS, level)
            draw_main_static()
            draw_cursor(None, level)
            prev_btn0 = btn[0].read()
            prev_btn1 = btn[1].read()

        else:
            prev_btn0 = btn_0
            prev_btn1 = btn_1

        delay(500)  # 요청하신 0.5초 주기

