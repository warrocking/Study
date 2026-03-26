"""
OpenCV 손동작 메뉴 + 과일 터치 게임

[프로그램 목적]
- 카메라 영상의 "움직임"을 입력으로 사용해 메뉴 선택, 게임 진행, 결과 확인을 처리합니다.
- 마우스/키보드 없이 손동작만으로 로그인, 시작, 필터 설정, 데이터 QR 확인, 종료까지 수행합니다.

[메인 실행 흐름]
1) 초기화
- 카메라 해상도 설정, 과일/버튼 이미지 로드, 타겟 풀(TargetPool) 준비, 상태 변수 초기화를 수행합니다.
2) 프레임 입력 + 움직임 마스크 생성
- 프레임 좌우반전 -> 그레이 변환 -> 블러/노이즈 완화 -> 프레임 차분(absdiff) -> threshold -> morphology로
  움직임 마스크를 생성합니다.
3) 로그인 상태(login / login_notice)
- login: QR 로그인 정보(`LOGIN|id|password|nickname`)를 인식/검증합니다.
- login_notice: 로그인 성공 안내를 잠깐 보여준 뒤 menu로 이동합니다.
4) 메뉴 상태(menu)
- START / SETTING / DATA / EXIT 버튼을 ROI 움직임 입력으로 판정합니다(2회 접촉 방식).
5) 카운트다운 상태(countdown)
- 3 -> 2 -> 1 -> Start 애니메이션 후 game 상태로 전환합니다.
6) 게임 상태(game)
- 타겟 활성/재스폰, 원형 ROI 히트 판정, 점수/시간 갱신, 게임 종료 시 last_game_record 갱신을 수행합니다.
7) 결과 상태(result)
- 최종 점수 화면을 일정 시간 보여준 뒤 menu로 복귀합니다.
8) 설정 상태(setting)
- 기본/흑백/가우시안/캐니/샤픈 필터를 버튼으로 선택하고 즉시 menu로 복귀합니다.
9) 데이터 상태(data_prepare / data_qr)
- 현재 로그인 ID의 최신 결과 JSON을 선택(없으면 fallback 생성) -> 결과 텍스트 QR 생성/표시를 수행합니다.
10) 종료
- ESC 입력 또는 EXIT 버튼 선택 시 루프를 종료하고 카메라/창 리소스를 해제합니다.

[적용된 핵심 처리와 목적]
- 프레임 차분(absdiff): 이전 프레임과 현재 프레임의 변화를 추출해 "움직임 후보"를 계산합니다.
- threshold(이진화): 작은 밝기 변화는 제거하고 의미 있는 변화만 0/255 마스크로 남깁니다.
- morphology(open/close): 점 잡음 제거와 끊긴 영역 연결로 움직임 마스크를 안정화합니다.
- 블러(gaussian/median): 조명 깜빡임, 센서 잡음, 미세 떨림을 줄여 오검출을 완화합니다.
- ROI 비율 판정(calc_rectMotion): 전체 화면이 아닌 버튼/타겟 주변만 검사해 입력 정확도를 높입니다.
- 2회 접촉 + 쿨다운: 메뉴/설정/종료 버튼의 우발 입력을 줄이고 의도한 동작만 반영합니다.
- TargetPool(풀링 관리): 타겟을 매번 생성/삭제하지 않고 활성/비활성으로 재사용해 부담을 줄입니다.
- 스폰 가드타임/히트 쿨다운: 스폰 직후 즉시 제거/연속 중복 히트 문제를 완화합니다.
- 알파 블렌딩(draw_spriteCenter): PNG 투명 채널(BGRA)을 유지해 과일/버튼 이미지를 자연스럽게 합성합니다.
- QR 로그인 전처리(AuthTool.detect_loginQr):
  원본/그레이/CLAHE/샤픈/Otsu/Adaptive 후보 영상을 순차 시도해 인식 안정성을 높입니다.
- 표시 필터(MotionTool.apply_displayFilter):
  none, gray, gaussian, canny, sharpen 필터를 설정 화면에서 즉시 전환해 카메라 표시를 변경합니다.
- 결과 데이터 관리(ResultTool + QrTool):
  게임 결과를 JSON으로 저장/조회하고, 최신 결과를 텍스트 QR로 변환해 휴대폰 스캔이 가능하도록 합니다.
- 상태 머신(state_now): 로그인/메뉴/게임/설정/데이터 흐름을 분리해 가독성과 유지보수성을 높입니다.

[핵심 클래스 및 함수]
- Target: 타겟 1개의 위치/활성 상태/재등장 타이밍/점수 정보를 관리합니다.
  - activate_target(...): 랜덤 위치로 타겟을 활성화하고 스폰 가드타임을 설정합니다.
  - deactivate_target(...): 타겟을 비활성화하고 다음 재등장 시간을 예약합니다.
- TargetPool: 여러 Target 객체를 묶어 활성/재스폰을 일괄 관리합니다.
  - spawn_targets(...): 지정 개수만 활성화하고 나머지는 비활성화합니다.
  - list_activeTargets(): 현재 화면 판정 대상(활성 타겟)만 반환합니다.
  - update_respawnTargets(...): 재등장 시간이 지난 타겟을 자동 재활성화합니다.
- ImageTool: 리소스 이미지 로드/채널 통일(BGRA)/fallback 생성 유틸을 제공합니다.
  - convert_rgbaImage(...): 모든 이미지를 BGRA 4채널로 통일합니다.
  - load_fruitAssets(): 과일 리소스를 로드하고 실패 시 fallback 스프라이트를 준비합니다.
  - load_squareAsset(...): 버튼 배경 이미지를 로드하고 실패 시 fallback 버튼을 생성합니다.
- DrawTool: 스프라이트/텍스트 렌더링 보조 유틸입니다.
  - draw_spriteCenter(...): 중심 좌표 기준으로 알파 합성 렌더링합니다.
  - draw_textCenter(...): 텍스트를 중앙 정렬로 그려 UI 가독성을 높입니다.
- MotionTool: 움직임 마스크 생성, ROI 입력 판정, 표시 필터 적용을 담당합니다.
  - build_frameMotion(...): 프레임 기반 움직임 마스크를 생성합니다.
  - calc_rectMotion(...): 사각 ROI의 움직임 비율/픽셀 수를 계산합니다.
  - apply_displayFilter(...): 현재 설정된 카메라 표시 필터를 적용합니다.
- MenuTool: 메뉴/설정/코너 버튼의 터치 상태 초기화를 담당합니다.
  - reset_touchState(...): 접촉 횟수/이전 접촉 플래그를 초기화합니다.
- AuthTool: 로그인 사용자 데이터 로드, QR 파싱/검증, QR 인식 전처리를 담당합니다.
  - load_userData(...): Resource/Data/users.json 계정을 로드합니다.
  - detect_loginQr(...): 다양한 전처리 후보로 로그인 QR 인식을 시도합니다.
  - verify_login(...): 로그인 ID/비밀번호 기준으로 인증합니다.
- QrTool: 결과 텍스트 구성 및 QR 이미지 생성을 담당합니다.
  - compose_resultText(...): Name/PlayTime/Score/Filter를 QR용 문자열로 만듭니다.
  - make_qrImage(...): 텍스트를 QR 이미지(BGR)로 생성합니다.
- ResultTool: 결과 JSON 저장/파일명 정리/최신 기록 조회를 담당합니다.
  - save_gameResult(...): 결과를 개별 JSON 파일로 저장합니다.
  - load_latestResult(...): 로그인 ID 기준 최신 기록 1개를 선택합니다.
- camera_set(...): 요청 해상도를 카메라에 설정하고 실제 적용값을 반환합니다.
- random_position(...): 반지름을 고려해 화면 밖으로 나가지 않는 랜덤 좌표를 생성합니다.
- main(): 전체 상태 머신과 렌더링 루프를 실행하는 프로그램 진입점입니다.
"""

# 경로 처리(리소스 폴더 탐색), 랜덤 값(위치/점수), 시간(쿨다운/경과시간) 계산용 모듈
import os
import random
import time
import json
from datetime import datetime

# OpenCV: 카메라/영상 처리/텍스트·도형 출력
# NumPy: 이미지(배열) 생성·합성 시 데이터 타입/채널 연산
import cv2
import numpy as np
# QR 생성 패키지(qrcode)가 없을 수도 있으므로 안전하게 예외 처리
try:
    import qrcode
except Exception:
    qrcode = None



# 과일 타겟 1개에 대한 "상태 + 동작"을 묶은 클래스
# 여기서 관리하는 값들은 게임 중 계속 바뀌므로 객체 단위로 묶어두면 추적이 쉽다.
class Target:
    def __init__(self, sprite_asset, hit_radius=40, score_gain=10):
        # 화면에 실제로 그릴 스프라이트(RGBA)
        self.sprite_asset = sprite_asset
        # 타겟 충돌 범위(원의 반지름)
        self.hit_radius = hit_radius
        # 이 타겟을 맞췄을 때 얻는 점수
        self.score_gain = score_gain

        # 현재 타겟 중심 좌표(프레임 기준)
        self.pos_x = 0
        self.pos_y = 0

        # 활성 여부: True면 화면에 표시/판정 대상, False면 대기 상태
        self.active_flag = False
        # 비활성 상태에서 다음 재등장 가능 시각
        self.respawn_time = 0.0
        # 마지막으로 히트된 시각(연속 중복 판정 방지)
        self.hit_time_last = 0.0
        # 스폰 직후 보호 종료 시각(바로 사라지는 문제 방지)
        self.guard_time_spawn = 0.0

    def activate_target(self, frame_width, frame_height, now_time=None):
        # 외부에서 시간 전달이 없으면 현재 시각을 사용
        if now_time is None:
            now_time = time.time()

        # 타겟을 화면에 다시 올리는 순간이므로 활성화
        self.active_flag = True
        # 화면 밖으로 나가지 않는 랜덤 위치로 중심 좌표 재배치
        self.pos_x, self.pos_y = random_position(frame_width, frame_height, self.hit_radius)
        # 스폰 직후 약간의 보호 시간 부여(조명 변화 등으로 즉시 히트되는 문제 완화)
        self.guard_time_spawn = now_time + 0.35

    def deactivate_target(self, now_time, time_randomStart = 0.25, time_randomEnd = 0.85):
        # 히트되면 비활성으로 전환하고
        self.active_flag = False
        # 랜덤 지연 뒤 다시 나오게 예약(패턴이 너무 규칙적이지 않게 만듦)
        self.respawn_time = now_time + random.uniform(time_randomStart, time_randomEnd)# 기본지연시간을 0.25~0.85초 사이로 지정


# 타겟 여러 개를 "묶어서" 관리하는 "오브젝트풀링" 클래스
# 생성/삭제 대신 활성/비활성만 바꿔 재사용하는 구조 - 가벼운 풀링 개념 - 유니티에서 사용했던 개념 가져옴
class TargetPool:
    def __init__(self, target_list):
        self.target_list = target_list

    def spawn_targets(self, active_count, frame_width, frame_height, now_time=None):
        # 앞쪽 active_count 갯수만 활성화, 나머지는 비활성화
        # 게임 시작/종료 시점에 전체 타겟 상태를 빠르게 맞추기 위한 함수
        for idx, target_obj in enumerate(self.target_list):#enumerate : "순서번호 + 값"을 같이 꺼내쓰는 함수
            if idx < active_count:
                target_obj.activate_target(frame_width, frame_height, now_time)
            else:
                target_obj.active_flag = False

    def list_activeTargets(self):
        # 현재 활성 타겟만 추려서 반환
        # 메인 루프에서 매 프레임 전체를 검사하지 않고 필요한 타겟만 순회 가능
        return [target_obj for target_obj in self.target_list if target_obj.active_flag]

    def update_respawnTargets(self, now_time, frame_width, frame_height):
        # 비활성 타겟 중에서, 재등장 시간이 지난 타겟만 다시 활성화
        for target_obj in self.target_list:
            if (not target_obj.active_flag) and now_time >= target_obj.respawn_time:
                target_obj.activate_target(frame_width, frame_height, now_time)

class ImageTool:

    @staticmethod
    # 이미지 채널 형식을 BGRA(4채널)로 통일하는 함수
    # 이유 : 
    #   - 이미지보다 채널 수가 다를 수 있어어 통일하는 함수가 필요
    #   - 안하면 합성코드 에러 발생함
    #   - RGB에서 거꾸로 해서 BGR에 알파의 A 까지 합쳐서 BGRA로 변경해야 알파값으로 투명, 반투명 설정 가능함.
    
    def convert_rgbaImage(raw_image):
        # 이미지 로드 실패(None)면 그대로 반환해서 상위 함수가 fallback 처리하도록 함
        if raw_image is None:
            return None

        # 1채널(그레이스케일) 이미지는 BGRA 4채널로 변환
        # -> 이후 합성 루틴이 "항상 4채널"이라고 가정해도 안전해짐
        if raw_image.ndim == 2:
            raw_image = cv2.cvtColor(raw_image, cv2.COLOR_GRAY2BGRA)

        # 3채널(BGR) 이미지는 알파 채널(255)을 붙여 BGRA로 통일
        if raw_image.ndim == 3 and raw_image.shape[2] == 3:
            # 원래 3채널(R, G, B)에 4채널(R, G, B, A)로 바꾸는 코드
            # alpha_layer = 알파 채널의 전용 이미지
            # np.full( ("이미지 정보"), 값 , 속성)
            # dtype=np.uint8 : 배열 안의 숫자 타입 / uint8 -> 0~255 사이 정수타입 / 0 : 완전 투명 & 255 : 완전 불투명
            # 기존 이미지를 투명하게 만들 목적이 아니라, 4채널 형식으로 맞추는 목적이라서 255를 넣는 것
            alpha_layer = np.full((raw_image.shape[0], raw_image.shape[1], 1), 255, dtype=np.uint8)
            # raw_image.shape == (720, 1280, 3) # 1280*720 의 3채널 이미지 생성
            # np.concatenate : 배열 2개를 이어 붙이는 함수 / raw_image와 alpha_layer를 붙임.
            # axis = 축을 의미 / axis=0: 세로(행) / axis=1: 가로(열) / axis=2: 채널 축
            # axis=2로 붙인다는 건
            # 가로/세로는 그대로 두고 채널만 늘리겠다는 뜻
            # (높이, 너비, 3) + (높이, 너비, 1) = (높이, 너비, 4) --> BGR + A = BGRA
            raw_image = np.concatenate([raw_image, alpha_layer], axis=2)

        # 4채널(BGRA) 원본이거나 위에서 3채널->4채널 변환이 끝난 이미지를 반환
        return raw_image

    @staticmethod
    # 리소스 이미지를 안전하게 읽고, 채널 형식과 크기를 통일해서 반환하는 함수
    # file_path : 파일 경로 / image_size : 이미지 출력 크기
    def load_resizedImage(file_path, image_size):
        # 파일을 원본 채널 상태로 읽고(IMREAD_UNCHANGED),
        # 위 convert_rgbaImage로 채널 형식을 통일한다.
        loaded_image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        loaded_image = ImageTool.convert_rgbaImage(loaded_image)
        if loaded_image is None:
            return None

        # image_size는 (width, height)
        # INTER_AREA는 축소 시 품질이 비교적 안정적이라 버튼/과일 아이콘에 적합
        return cv2.resize(loaded_image, image_size, interpolation=cv2.INTER_AREA)

    @staticmethod
    # 이미지 파일 로드에 실패했을 때 대신 보여줄 
    def make_fallbackCircle(sprite_size, color_bgr=(0, 0, 255), text_label="F"):
        # 리소스 이미지가 없을 때도 로직이 멈추지 않게 만들어주는 대체 타겟
        width_size, height_size = sprite_size

        # BGRA 4채널 캔버스(처음은 완전 투명)
        sprite_img = np.zeros((height_size, width_size, 4), dtype=np.uint8)

        # 원이 이미지 경계를 넘지 않도록 최소 변 기준으로 반지름 계산
        circle_radius = int(min(width_size, height_size) * 0.45)

        # (*color_bgr, 255): B,G,R + alpha(불투명)
        cv2.circle(sprite_img, (width_size // 2, height_size // 2), circle_radius, (*color_bgr, 255), -1)

        # fallback 식별용 문자(예: F)를 중앙 근처에 출력
        # putText 파라미터:
        # 1) sprite_img: 그릴 대상 이미지
        # 2) text_label: 출력할 문자열
        # 3) (x, y): 기준 위치(좌하단 기준점)
        # 4) FONT_HERSHEY_SIMPLEX: 폰트 타입
        # 5) 0.8: 글자 크기(scale)
        # 6) (255,255,255,255): 글자 색(B,G,R,A)
        # 7) 2: 두께(thickness)
        cv2.putText(
            sprite_img,
            text_label,
            (width_size // 2 - 14, height_size // 2 + 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255, 255),
            2,
        )
        return sprite_img

    @staticmethod
    def make_fallbackSquare(sprite_size):
        # square.png가 없을 때 메뉴 버튼 베이스로 쓰는 대체 사각형
        width_size, height_size = sprite_size
        sprite_img = np.zeros((height_size, width_size, 4), dtype=np.uint8)

        # 내부 채우기 + 외곽선으로 버튼처럼 보이도록 구성
        cv2.rectangle(sprite_img, (6, 6), (width_size - 6, height_size - 6), (180, 180, 180, 255), -1)
        cv2.rectangle(sprite_img, (6, 6), (width_size - 6, height_size - 6), (90, 90, 90, 255), 3)
        return sprite_img

    @staticmethod
    def load_fruitAssets():
        # 현재 파일(OpenCV/portfolio.py) 기준 상위 폴더(PYC) 계산
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        resource_dir = os.path.join(base_dir, "Resource", "Img")

        file_name_list = ["banana.png", "strawberry.png", "watermelon.png"]
        fruit_assets = []

        # 이미지가 존재하면 (이름, 이미지) 튜플로 적재
        for file_name in file_name_list:
            file_path = os.path.join(resource_dir, file_name)
            image_asset = ImageTool.load_resizedImage(file_path, (80, 80))
            if image_asset is None:
                print(f"[WARN] Image load failed: {file_path}")
                continue
            fruit_assets.append((os.path.splitext(file_name)[0], image_asset))

        # 전부 실패한 경우에도 게임이 시작되게 fallback 1개를 넣는다.
        if not fruit_assets:
            fruit_assets.append(("fallback", ImageTool.make_fallbackCircle((80, 80))))

        return fruit_assets

    @staticmethod
    def load_squareAsset(sprite_size=(240, 130), file_name="square.png"):
        # 버튼 베이스 이미지 로드(기본: square.png, 세팅용: square_blue.png 등)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        file_path = os.path.join(base_dir, "Resource", "Img", file_name)
        square_asset = ImageTool.load_resizedImage(file_path, sprite_size)
        if square_asset is None:
            # 누락 시에도 메뉴 UI 동작 보장을 위해 fallback 반환
            return ImageTool.make_fallbackSquare(sprite_size)
        return square_asset

    @staticmethod
    def tint_squareAsset(square_asset, color_bgr):
        # 같은 버튼 베이스를 색상만 바꿔 3종 버튼으로 재사용
        out_img = square_asset.copy()
        base_rgb = out_img[:, :, :3].astype(np.float32)
        color_layer = np.zeros_like(base_rgb)
        color_layer[:] = np.array(color_bgr, dtype=np.float32)

        # 원본 질감 40% + 지정 색상 60%로 혼합
        mixed_rgb = cv2.addWeighted(base_rgb, 0.40, color_layer, 0.60, 0)
        out_img[:, :, :3] = mixed_rgb.astype(np.uint8)
        return out_img

class DrawTool:

    @staticmethod
    def draw_spriteCenter(frame_img, sprite_asset, center_x, center_y):
        # sprite 크기를 가져와 중심 좌표 기준으로 배치할 박스를 계산
        sprite_h, sprite_w = sprite_asset.shape[:2]

        x1 = int(center_x - sprite_w // 2)
        y1 = int(center_y - sprite_h // 2)
        x2 = x1 + sprite_w
        y2 = y1 + sprite_h

        # 프레임 밖으로 완전히 나간 경우는 그릴 필요가 없으므로 종료
        frame_h, frame_w = frame_img.shape[:2]
        if x2 <= 0 or y2 <= 0 or x1 >= frame_w or y1 >= frame_h:
            return

        # 프레임 경계로 클리핑(일부만 걸친 경우 안전 처리)
        clip_x1 = max(0, x1)
        clip_y1 = max(0, y1)
        clip_x2 = min(frame_w, x2)
        clip_y2 = min(frame_h, y2)

        # 클리핑된 만큼 소스(sprite)에서 잘라낼 좌표 계산
        src_x1 = clip_x1 - x1
        src_y1 = clip_y1 - y1
        src_x2 = src_x1 + (clip_x2 - clip_x1)
        src_y2 = src_y1 + (clip_y2 - clip_y1)

        # 소스/대상 ROI 추출 후 알파 블렌딩 수행
        src_img = sprite_asset[src_y1:src_y2, src_x1:src_x2]
        dst_img = frame_img[clip_y1:clip_y2, clip_x1:clip_x2]

        alpha_mask = (src_img[:, :, 3:4] / 255.0).astype(np.float32)
        src_rgb = src_img[:, :, :3].astype(np.float32)
        dst_rgb = dst_img.astype(np.float32)

        out_rgb = (src_rgb * alpha_mask) + (dst_rgb * (1.0 - alpha_mask))
        frame_img[clip_y1:clip_y2, clip_x1:clip_x2] = out_rgb.astype(np.uint8)

    @staticmethod
    def draw_textCenter(frame_img, text_msg, center_x, center_y, font_scale=0.9, color=(255, 255, 255), thickness=2):
        # 텍스트 크기를 먼저 구해 "중앙 정렬된 좌표"를 계산
        (text_w, text_h), _ = cv2.getTextSize(text_msg, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        text_x = int(center_x - text_w / 2)
        text_y = int(center_y + text_h / 2)

        # 1차 검정 외곽선(가독성 향상), 2차 본문 색상
        # putText 파라미터 공통 설명:
        # 1) frame_img : 출력 대상 프레임
        # 2) text_msg  : 출력 문자열
        # 3) (text_x,text_y) : 좌표(좌하단 기준)
        # 4) FONT_HERSHEY_SIMPLEX : 폰트 종류
        # 5) font_scale : 글자 크기
        # 6) color : 글자 색(B,G,R)
        # 7) thickness : 선 두께
        # 8) LINE_AA : 안티앨리어싱
        cv2.putText(
            frame_img,
            text_msg,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (0, 0, 0),
            thickness + 2,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame_img,
            text_msg,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA,
        )

class MotionTool:

    @staticmethod
    def filter_grayFrame(gray_frame):
        # 가우시안 + 미디언 블러 조합:
        # - GaussianBlur: 전체적으로 부드럽게 만들어 미세 노이즈 완화
        # - medianBlur : 점 형태 노이즈 제거(조명 깜빡임/센서 점 잡음 완화)
        blur_gray = cv2.GaussianBlur(gray_frame, (21, 21), 0)
        blur_gray = cv2.medianBlur(blur_gray, 5)
        return blur_gray

    @staticmethod
    def build_diffMask(curr_filtered, prev_filtered):
        # 프레임 차분으로 움직임 후보를 얻고 threshold로 이진화
        diff_img = cv2.absdiff(prev_filtered, curr_filtered)
        # threshold=25: 이 값보다 작은 변화는 노이즈로 보고 버림
        _, mask_img = cv2.threshold(diff_img, 25, 255, cv2.THRESH_BINARY)
        return mask_img

    @staticmethod
    def build_frameMotion(frame_img, prev_filtered):
        # 현재 프레임을 그레이 변환 후 필터 적용
        gray_frame = cv2.cvtColor(frame_img, cv2.COLOR_BGR2GRAY)
        curr_filtered = MotionTool.filter_grayFrame(gray_frame)

        # 첫 프레임은 비교 기준이 없으므로 현재 프레임을 기준으로 설정
        if prev_filtered is None:
            prev_filtered = curr_filtered.copy()

        # 이전 프레임 대비 움직임 마스크 생성
        motion_mask = MotionTool.build_diffMask(curr_filtered, prev_filtered)

        # 다음 루프에서 사용할 이전 프레임 갱신
        prev_filtered = curr_filtered.copy()
        return motion_mask, prev_filtered

    @staticmethod
    def apply_grayDisplay(frame_img):
        # 화면 표시용 흑백 필터: Gray(1채널)로 바꾼 뒤 BGR(3채널)로 되돌려 그리기 호환 유지
        gray_frame = cv2.cvtColor(frame_img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def apply_gaussianDisplay(frame_img, kernel_size=(15, 15), sigma_x=0):
        # 화면 표시용 가우시안 블러 필터: 커널 크기가 클수록 더 부드럽고 흐려진다.
        return cv2.GaussianBlur(frame_img, kernel_size, sigma_x)

    @staticmethod
    def apply_cannyDisplay(frame_img, low_threshold=20, high_threshold=60):
        # 화면 표시용 캐니 엣지 필터: 경계선만 강조해 윤곽을 확인하기 쉽게 만든다.
        # OpenCV 권장 비율(상한:하한 2~3배)에 맞춰 기본값을 1:3(20/60)로 설정
        gray_frame = cv2.cvtColor(frame_img, cv2.COLOR_BGR2GRAY)
        # 캐니 전에 약한 가우시안 블러를 넣어 점잡음(잔엣지) 완화
        blur_frame = cv2.GaussianBlur(gray_frame, (3, 3), 0)
        edge_frame = cv2.Canny(blur_frame, low_threshold, high_threshold, apertureSize=3, L2gradient=True)
        return cv2.cvtColor(edge_frame, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def apply_sharpenDisplay(frame_img):
        # 화면 표시용 샤픈 필터: 경계와 디테일을 선명하게 강조한다.
        sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        return cv2.filter2D(frame_img, -1, sharpen_kernel)

    @staticmethod
    def apply_displayFilter(frame_img, filter_key):
        # 메뉴/세팅에서 고른 필터를 화면 출력에 반영한다.
        if filter_key == "gray":
            return MotionTool.apply_grayDisplay(frame_img)
        if filter_key == "gaussian":
            return MotionTool.apply_gaussianDisplay(frame_img)
        if filter_key == "canny":
            return MotionTool.apply_cannyDisplay(frame_img)
        if filter_key == "sharpen":
            return MotionTool.apply_sharpenDisplay(frame_img)
        # 기본값: 필터 미적용 원본
        return frame_img.copy()

    @staticmethod
    def calc_rectMotion(mask_img, x1, y1, x2, y2):
        # 관심영역(ROI)만 잘라 계산하면 속도/안정성이 좋아짐
        roi_img = mask_img[y1:y2, x1:x2]
        if roi_img.size == 0:
            # area=1로 반환하는 이유: 분모 0 연산 방지
            return 0.0, 0, 1

        roi_area = (x2 - x1) * (y2 - y1)
        if roi_area <= 0:
            return 0.0, 0, 1

        # 흰색 픽셀(움직임)을 세고 비율 계산
        motion_pixels = cv2.countNonZero(roi_img)
        motion_ratio = motion_pixels / float(roi_area)
        return motion_ratio, motion_pixels, roi_area

class MenuTool:

    @staticmethod
    def reset_touchState(touch_count_map, over_prev_map):
        # 메뉴 전환 시 이전 입력 흔적을 초기화하지 않으면
        # 다음 화면에서 바로 오작동(의도치 않은 선택)이 발생할 수 있다.
        for key_name in touch_count_map:
            touch_count_map[key_name] = 0
        for key_name in over_prev_map:
            over_prev_map[key_name] = False

# Login utility class
# - load user account list
# - parse login QR text
# - multi-preprocess QR detection
# - validate id/password
class AuthTool:

    @staticmethod
    def load_userData(file_name="users.json"):
        # Resource/Data/users.json에서 로그인 계정 목록을 읽는다.
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        file_path = os.path.join(base_dir, "Resource", "Data", file_name)
        if not os.path.exists(file_path):
            print(f"[WARN] Login data file not found: {file_path}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8-sig") as fp:
                raw_data = json.load(fp)
        except Exception as err:
            print(f"[WARN] Failed to read login data: {err}")
            return []

        user_list = []
        if isinstance(raw_data, dict):
            user_list = raw_data.get("users", [])
        elif isinstance(raw_data, list):
            user_list = raw_data

        normalized = []
        for user_obj in user_list:
            if not isinstance(user_obj, dict):
                continue
            id_text = str(user_obj.get("id", "")).strip()
            pw_text = str(user_obj.get("password", "")).strip()
            nick_text = str(user_obj.get("nickname", "")).strip() or id_text
            if id_text and pw_text:
                normalized.append({"id": id_text, "password": pw_text, "nickname": nick_text})
        return normalized

    @staticmethod
    def parse_loginQr(qr_text):
        # Supported formats (nickname optional):
        # 1) LOGIN|id|password|nickname
        # 2) LOGIN|id|password
        # 3) id|password|nickname
        # 4) id|password
        # 5) {"id":"...", "password":"...", "nickname":"..."}
        if not qr_text:
            return None

        text_now = qr_text.strip()

        # 1st try: JSON format
        if text_now.startswith("{") and text_now.endswith("}"):
            try:
                json_obj = json.loads(text_now)
                id_text = str(json_obj.get("id", "")).strip()
                pw_text = str(json_obj.get("password", "")).strip()
                nick_text = str(json_obj.get("nickname", "")).strip()
                if not id_text or not pw_text:
                    return None
                return {"id": id_text, "password": pw_text, "nickname": nick_text}
            except Exception:
                return None

        # 2nd try: '|' separated text format
        parts = [part.strip() for part in text_now.split("|")]
        if parts and parts[0].upper() == "LOGIN":
            # Remove LOGIN prefix before reading id/password
            parts = parts[1:]

        if len(parts) < 2:
            return None

        id_text = parts[0]
        pw_text = parts[1]
        nick_text = parts[2] if len(parts) >= 3 else ""

        if not id_text or not pw_text:
            return None

        return {"id": id_text, "password": pw_text, "nickname": nick_text}

    @staticmethod
    def detect_loginQr(detector, frame_img):
        # 조명 반사/과노출 상황에서도 인식률을 높이기 위해 여러 전처리 버전으로 순차 시도
        gray_img = cv2.cvtColor(frame_img, cv2.COLOR_BGR2GRAY)

        clahe_obj = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
        clahe_img = clahe_obj.apply(gray_img)

        blur_img = cv2.GaussianBlur(clahe_img, (0, 0), 1.0)
        sharpen_img = cv2.addWeighted(clahe_img, 1.55, blur_img, -0.55, 0)

        _, otsu_img = cv2.threshold(sharpen_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        adapt_img = cv2.adaptiveThreshold(
            sharpen_img,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            3,
        )

        candidate_list = [
            # raw: original frame
            ("raw", frame_img),
            # gray: grayscale frame
            ("gray", gray_img),
            # clahe: local contrast enhanced frame
            ("clahe", clahe_img),
            # sharp: sharpened frame
            ("sharp", sharpen_img),
            # otsu: global-threshold binary frame
            ("otsu", otsu_img),
            # adapt: adaptive-threshold binary frame
            ("adapt", adapt_img),
        ]

        for mode_name, candidate_img in candidate_list:
            qr_text, qr_points, _ = detector.detectAndDecode(candidate_img)
            if qr_text:
                return qr_text, qr_points, mode_name

        return "", None, "none"
    @staticmethod
    def verify_login(login_info, user_list):
        # Validation policy:
        # - compare id/password with users.json
        # - nickname is display/save data, not auth key
        if not login_info:
            return None
        id_text = str(login_info.get("id", "")).strip()
        pw_text = str(login_info.get("password", "")).strip()

        if not id_text or not pw_text:
            return None

        for user_obj in user_list:
            if user_obj.get("id") == id_text and user_obj.get("password") == pw_text:
                return user_obj
        return None

# Utility class for converting result text to QR image
class QrTool:

    @staticmethod
    def make_qrImage(text_data, image_size=360):
        # Return None when qrcode package is missing or text is empty.
        if not text_data or qrcode is None:
            return None

        # ERROR_CORRECT_M balances scan stability and payload size.
        qr_obj = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr_obj.add_data(text_data)
        qr_obj.make(fit=True)

        # Convert qrcode(PIL) image to OpenCV BGR format.
        pil_img = qr_obj.make_image(fill_color="black", back_color="white").convert("RGB")
        rgb_img = np.array(pil_img)
        bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
        # INTER_NEAREST keeps QR edges sharp for better scanning.
        return cv2.resize(bgr_img, (image_size, image_size), interpolation=cv2.INTER_NEAREST)

    @staticmethod
    def compose_resultText(nickname, play_time_text, score_now, filter_name):
        # 휴대폰 스캔 시 메모장/텍스트 앱에서 읽기 쉽게 줄바꿈 텍스트로 구성
        return (
            f"Name: {nickname}\n"
            f"PlayTime: {play_time_text}\n"
            f"Score: {score_now}\n"
            f"Filter: {filter_name}"
        )


# Utility class for saving/loading game result JSON files
class ResultTool:

    @staticmethod
    def get_resultDir():
        # Ensure result directory exists and return its path.
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        result_dir = os.path.join(base_dir, "Resource", "Data", "GameResult")
        os.makedirs(result_dir, exist_ok=True)
        return result_dir

    @staticmethod
    def sanitize_filePart(text_data):
        # Replace unsafe filename characters with safe separators.
        text_now = str(text_data).strip()
        if not text_now:
            return "unknown"

        invalid_chars = '<>:"/\\|?*'
        for bad_char in invalid_chars:
            text_now = text_now.replace(bad_char, "_")

        text_now = text_now.replace("\n", "_").replace("\r", "_").replace("\t", "_")
        text_now = text_now.replace(" ", "_")
        while "__" in text_now:
            text_now = text_now.replace("__", "_")

        text_now = text_now.strip("._")
        return text_now or "unknown"

    @staticmethod
    def normalize_playTime(play_time_text):
        # Normalize play time string for safe filename usage.
        play_text = str(play_time_text).strip()
        if (not play_text) or (play_text.upper() == "N/A"):
            play_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 파일명에 쓸 수 없는 ':' 제거
        play_text = play_text.replace(":", "-").replace(" ", "_")
        return ResultTool.sanitize_filePart(play_text)

    @staticmethod
    def save_gameResult(player_name, play_time_text, score_now, filter_name, login_id=""):
        # Build standardized result object for save and reuse.
        result_obj = {
            "Name": str(player_name),
            "PlayTime": str(play_time_text),
            "Score": int(score_now),
            "Filter": str(filter_name),
            "LoginID": str(login_id).strip(),
        }

        # Base filename: name_time. Add suffix when duplicate exists.
        result_dir = ResultTool.get_resultDir()
        name_part = ResultTool.sanitize_filePart(player_name)
        time_part = ResultTool.normalize_playTime(play_time_text)
        base_name = f"{name_part}_{time_part}"

        file_path = os.path.join(result_dir, f"{base_name}.json")
        suffix_idx = 1
        while os.path.exists(file_path):
            file_path = os.path.join(result_dir, f"{base_name}_{suffix_idx}.json")
            suffix_idx += 1

        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(result_obj, fp, ensure_ascii=False, indent=2)

        return file_path, result_obj

    @staticmethod
    def parse_playTime(play_time_text):
        # Parse play time string to datetime for latest sort.
        try:
            return datetime.strptime(str(play_time_text).strip(), "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None

    @staticmethod
    def load_latestResult(login_id):
        # Find one latest result matched to current login id.
        # Sort key: PlayTime first, file modified time second.
        result_dir = ResultTool.get_resultDir()
        login_text = str(login_id).strip()

        latest_obj = None
        latest_path = ""
        latest_key = None

        for file_name in os.listdir(result_dir):
            if not str(file_name).lower().endswith(".json"):
                continue

            file_path = os.path.join(result_dir, file_name)
            try:
                with open(file_path, "r", encoding="utf-8-sig") as fp:
                    result_obj = json.load(fp)
            except Exception:
                continue

            if not isinstance(result_obj, dict):
                continue

            record_id = str(result_obj.get("LoginID", "")).strip()
            record_name = str(result_obj.get("Name", "")).strip()

            # If login id is provided, keep only matching records.
            if login_text and (record_id != login_text and record_name != login_text):
                continue

            play_dt = ResultTool.parse_playTime(result_obj.get("PlayTime", ""))
            play_ts = play_dt.timestamp() if play_dt is not None else -1.0
            mod_ts = os.path.getmtime(file_path)
            sort_key = (play_ts, mod_ts)

            if latest_key is None or sort_key > latest_key:
                latest_key = sort_key
                latest_obj = result_obj
                latest_path = file_path

        return latest_obj, latest_path

def camera_set(cap_obj, frame_width=1280, frame_height=720):
    # 카메라에 "요청" 해상도를 설정하고
    cap_obj.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap_obj.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    # 장치가 실제로 적용한 해상도를 다시 읽는다.
    # (장치에 따라 요청값과 다를 수 있음)
    real_width = int(cap_obj.get(cv2.CAP_PROP_FRAME_WIDTH))
    real_height = int(cap_obj.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return real_width, real_height

def random_position(frame_width, frame_height, hit_radius):
    # 타겟 중심 좌표를 생성할 때 반지름만큼 여유를 둬서
    # 원형 판정이 프레임 밖으로 나가지 않게 한다.
    pos_x = random.randint(hit_radius, frame_width - hit_radius)
    pos_y = random.randint(hit_radius, frame_height - hit_radius)
    return pos_x, pos_y

def main() -> None:
    # 기본 웹캠(인덱스 0) 열기
    cap_obj = cv2.VideoCapture(0)
    if not cap_obj.isOpened():
        print("Webcam is not available")
        return

    # 카메라 해상도 요청/적용
    frame_width, frame_height = camera_set(cap_obj, 1280, 720)
    print(frame_width, frame_height)

    # 로그인 사용자 데이터 로드 + QR 디코더 준비
    user_list = AuthTool.load_userData("users.json")
    qr_detector = cv2.QRCodeDetector()

    # 로그인/게임 결과 데이터 상태
    login_user = None
    login_nickname = "GUEST"
    login_fail_until = 0.0
    login_decode_time_last = 0.0
    login_decode_cooldown = 0.8
    login_notice_sec = 1.2
    login_notice_start = 0.0
    last_game_record = {
        "play_time": "N/A",
        "score": 0,
        "filter": "BASIC",
    }

    # 데이터 QR 출력 상태
    data_prepare_sec = 5
    data_prepare_start_time = 0.0
    data_selected_result = {}
    data_qr_sec = 30
    data_qr_start_time = 0.0
    data_qr_image = None
    data_qr_text = ""

    # 우상단 EXIT 버튼(로그인/데이터 화면 공통)
    corner_exit_w = 170
    corner_exit_h = 80
    corner_exit_count = 0
    corner_exit_prev = False
    corner_exit_time = 0.0

    fruit_assets = ImageTool.load_fruitAssets()
    target_count = 6
    # 1) 각 종류 1개씩 먼저 보장
    picked_assets = fruit_assets[:]   # banana, strawberry, watermelon

    # 2) 남은 칸은 랜덤 중복 허용
    while len(picked_assets) < target_count:
        picked_assets.append(random.choice(fruit_assets))

    # 3) 순서 랜덤 섞기
    random.shuffle(picked_assets)
    # 4) 타겟 생성
    target_list = []
    picked_assets = picked_assets[:target_count]
    for _, sprite_asset in picked_assets:
        score_gain = random.choice([10, 15, 20])
        target_list.append(Target(sprite_asset, hit_radius=40, score_gain=score_gain))
    # # 과일 에셋 로드 후 타겟 객체 6개 생성(풀링용)
    
    # for _ in range(6):
    #     # 과일 이미지는 랜덤 선택
    #     _, sprite_asset = random.choice(fruit_assets)
    #     # 점수도 랜덤으로 줘서 타겟 가치에 변화를 둠
    #     score_gain = random.choice([10, 15, 20])
    #     target_list.append(Target(sprite_asset, hit_radius=40, score_gain=score_gain))

    target_pool = TargetPool(target_list)
    # 메뉴 진입 상태에서는 타겟 비활성(0개)
    target_pool.spawn_targets(active_count=0, frame_width=frame_width, frame_height=frame_height)

    # 메뉴 버튼 베이스 이미지 로드
    square_asset = ImageTool.load_squareAsset((240, 130))
    # 세팅 버튼은 1행 5개 배치를 위해 전용 크기를 사용
    setting_button_w, setting_button_h = 200, 110
    setting_gap_w = 20
    # 세팅 버튼 베이스는 요청대로 square_blue.png 사용
    setting_square_asset = ImageTool.load_squareAsset((setting_button_w, setting_button_h), "square_blue.png")

    color_list = [
        (235, 206, 135),  # START: sky blue (BGR)
        (255, 0, 0),      # SETTING: blue (BGR)
        (0, 200, 0),      # DATA: green (BGR)
        (0, 165, 255),    # EXIT: orange (BGR)
    ]
    menu_spec_list = [
        ("START", "start"),
        ("SETTING", "mode"),
        ("DATA", "data"),
        ("EXIT", "exit"),
    ]

    # 버튼 레이아웃 계산(4개 버튼을 상단 중앙 정렬)
    button_w, button_h = 240, 130
    gap_w = 40
    total_w = button_w * len(menu_spec_list) + gap_w * (len(menu_spec_list) - 1)
    start_x = max(0, (frame_width - total_w) // 2)
    center_y = 20 + (button_h // 2)

    button_list = []
    for idx, (label_text, action_key) in enumerate(menu_spec_list):
        center_x = start_x + idx * (button_w + gap_w) + (button_w // 2)
        # 같은 square 베이스에 색만 바꿔 버튼별 시각 구분
        tint_sprite = ImageTool.tint_squareAsset(square_asset, color_list[idx])
        button_list.append(
            {
                "label": label_text,
                "action": action_key,
                "sprite": tint_sprite,
                "center_x": center_x,
                "center_y": center_y,
                "width": button_w,
                "height": button_h,
            }
        )

    # 세팅 화면 필터 버튼(총 5개): 1행 일자 배치
    filter_spec_list = [
        ("BASIC", "none"),
        ("GRAY", "gray"),
        ("GAUSS", "gaussian"),
        ("CANNY", "canny"),
        ("SHARP", "sharpen"),
    ]

    setting_total_w = setting_button_w * len(filter_spec_list) + setting_gap_w * (len(filter_spec_list) - 1)
    setting_start_x = max(0, (frame_width - setting_total_w) // 2)
    setting_center_y = 20 + (setting_button_h // 2)

    setting_button_list = []
    for idx, (label_text, action_key) in enumerate(filter_spec_list):
        center_x = setting_start_x + idx * (setting_button_w + setting_gap_w) + (setting_button_w // 2)

        setting_button_list.append(
            {
                "label": label_text,
                "action": action_key,
                "sprite": setting_square_asset,
                "center_x": center_x,
                "center_y": setting_center_y,
                "width": setting_button_w,
                "height": setting_button_h,
            }
        )

    # 상태머신 상수: 문자열 오타를 줄이기 위해 상수로 정의
    state_login = "login"
    state_login_notice = "login_notice"
    state_menu = "menu"
    state_countdown = "countdown"
    state_game = "game"
    state_result = "result"
    state_setting = "setting"
    state_data_prepare = "data_prepare"
    state_data_qr = "data_qr"
    state_now = state_login

    # 출력용 필터 상태(프로그램 시작 시 기본 필터: none)
    filter_key_now = "none"
    filter_name_map = {
        "none": "BASIC",
        "gray": "GRAY",
        "gaussian": "GAUSSIAN",
        "canny": "CANNY",
        "sharpen": "SHARPEN",
    }

    # 버튼 접촉 판정 임계값(메뉴/세팅/로그인 공통)
    touch_ratio_min = 0.025
    touch_pixels_min = 120
    touch_required = 2
    touch_cooldown = 0.25

    # 메뉴 버튼 상태 저장용 맵
    menu_key_list = [action_key for _, action_key in menu_spec_list]
    touch_count_map = {key_name: 0 for key_name in menu_key_list}
    over_prev_map = {key_name: False for key_name in menu_key_list}
    touch_time_map = {key_name: 0.0 for key_name in menu_key_list}

    # 세팅(필터) 버튼 상태 저장용 맵
    setting_touch_count_map = {key_name: 0 for _, key_name in filter_spec_list}
    setting_over_prev_map = {key_name: False for _, key_name in filter_spec_list}
    setting_touch_time_map = {key_name: 0.0 for _, key_name in filter_spec_list}

    # 메뉴/세팅 진입 직후 오작동 방지를 위한 입력 잠금 시간
    menu_lock_start = 1.6
    menu_lock_reentry = 0.8
    setting_lock_reentry = 0.6
    menu_enable_time = time.time() + menu_lock_start
    setting_enable_time = 0.0

    # 화면 지속 시간/게임 시간 설정
    score_now = 0
    game_sec = 60
    result_sec = 5

    game_time_start = 0.0
    result_time_start = 0.0
    countdown_time_start = 0.0

    # 히트 판정 관련 임계값
    hit_cooldown = 0.35
    hit_ratio_min = 0.08
    hit_guard_start = 0.5

    # 프레임 차분용 이전 프레임
    prev_filtered = None

    # 메인 루프 시작
    while True:
        ret_ok, frame_img = cap_obj.read()
        if not ret_ok or frame_img is None:
            print("Failed to read frame.")
            break

        # 거울 모드(사용자 기준 좌우가 직관적)
        frame_img = cv2.flip(frame_img, 1)

        # 모션 검출용 전처리(함수화): 그레이/블러/차분/마스크를 한 번에 처리
        motion_mask, prev_filtered = MotionTool.build_frameMotion(frame_img, prev_filtered)

        now_time = time.time()

        # 표시용 캔버스
        # 로그인 화면은 QR 인식 가독성을 위해 필터 미적용 원본으로 고정
        if state_now == state_login or state_now == state_login_notice:
            canvas_img = frame_img.copy()
        else:
            canvas_img = MotionTool.apply_displayFilter(frame_img, filter_key_now)
        if state_now == state_login:
            qr_text, qr_points, qr_mode = AuthTool.detect_loginQr(qr_detector, frame_img)

            cv2.putText(canvas_img, "LOGIN - QR", (20, frame_height - 55), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(canvas_img, "QR: LOGIN|id|password (nickname optional)", (20, frame_height - 90), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            cv2.putText(canvas_img, "Show your QR to login", (20, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            cv2.putText(canvas_img, f"QR Detect Mode: {qr_mode}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (180, 255, 180), 2)

            if qr_points is not None and len(qr_points) > 0:
                qr_poly = np.int32(qr_points).reshape(-1, 2)
                cv2.polylines(canvas_img, [qr_poly], True, (0, 255, 255), 2)

            if qr_text and (now_time - login_decode_time_last) > login_decode_cooldown:
                login_decode_time_last = now_time
                login_info = AuthTool.parse_loginQr(qr_text)
                matched_user = AuthTool.verify_login(login_info, user_list)

                if matched_user is not None:
                    login_user = matched_user
                    login_nickname = matched_user.get("nickname") or matched_user.get("id", "GUEST")
                    login_fail_until = 0.0
                    corner_exit_count = 0
                    corner_exit_prev = False
                    corner_exit_time = 0.0
                    state_now = state_login_notice
                    login_notice_start = now_time
                else:
                    login_fail_until = now_time + 5.0

            if now_time < login_fail_until:
                cv2.putText(canvas_img, "Invalid login info. Please check your QR code.", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 80, 255), 2)

            # 로그인 화면 우상단 EXIT 버튼 (2회 접촉)
            exit_x2 = frame_width - 20
            exit_y1 = 20
            exit_x1 = max(0, exit_x2 - corner_exit_w)
            exit_y2 = exit_y1 + corner_exit_h

            cv2.rectangle(canvas_img, (exit_x1, exit_y1), (exit_x2, exit_y2), (30, 30, 30), -1)
            cv2.rectangle(canvas_img, (exit_x1, exit_y1), (exit_x2, exit_y2), (0, 165, 255), 2)
            DrawTool.draw_textCenter(canvas_img, "EXIT", (exit_x1 + exit_x2) // 2, (exit_y1 + exit_y2) // 2, font_scale=0.9, color=(255, 255, 255), thickness=2)

            ratio_now, pixels_now, _ = MotionTool.calc_rectMotion(motion_mask, exit_x1, exit_y1, exit_x2, exit_y2)
            over_now = (ratio_now >= touch_ratio_min) and (pixels_now >= touch_pixels_min)
            edge_up = over_now and (not corner_exit_prev)
            cooldown_ok = (now_time - corner_exit_time) > touch_cooldown
            if edge_up and cooldown_ok:
                corner_exit_count = min(touch_required, corner_exit_count + 1)
                corner_exit_time = now_time
            corner_exit_prev = over_now

            progress = corner_exit_count / float(touch_required)
            bar_x1 = exit_x1 + 6
            bar_x2 = exit_x2 - 6
            bar_y1 = exit_y2 + 6
            bar_y2 = exit_y2 + 14
            cv2.rectangle(canvas_img, (bar_x1, bar_y1), (bar_x2, bar_y2), (60, 60, 60), -1)
            fill_w = int((bar_x2 - bar_x1) * progress)
            cv2.rectangle(canvas_img, (bar_x1, bar_y1), (bar_x1 + fill_w, bar_y2), (0, 255, 0), -1)

            if corner_exit_count >= touch_required:
                break

        elif state_now == state_login_notice:
            # 로그인 성공 직후, 사용자가 전환을 인지할 수 있도록 짧은 안내 화면 표시
            elapsed = now_time - login_notice_start

            # 중앙 안내 박스(반투명)
            overlay_img = canvas_img.copy()
            box_x1 = max(0, (frame_width // 2) - 320)
            box_y1 = max(0, (frame_height // 2) - 120)
            box_x2 = min(frame_width, (frame_width // 2) + 320)
            box_y2 = min(frame_height, (frame_height // 2) + 120)
            cv2.rectangle(overlay_img, (box_x1, box_y1), (box_x2, box_y2), (20, 20, 20), -1)
            cv2.addWeighted(overlay_img, 0.55, canvas_img, 0.45, 0, canvas_img)
            cv2.rectangle(canvas_img, (box_x1, box_y1), (box_x2, box_y2), (0, 200, 255), 2)

            DrawTool.draw_textCenter(canvas_img, "LOGIN SUCCESS", frame_width // 2, frame_height // 2 - 35, font_scale=1.2, color=(0, 255, 120), thickness=3)
            DrawTool.draw_textCenter(canvas_img, f"WELCOME {login_user.get('id', 'USER') if isinstance(login_user, dict) else 'USER'}", frame_width // 2, frame_height // 2 + 10, font_scale=0.9, color=(255, 255, 255), thickness=2)
            DrawTool.draw_textCenter(canvas_img, "Moving to Menu...", frame_width // 2, frame_height // 2 + 45, font_scale=0.8, color=(200, 255, 255), thickness=2)

            if elapsed >= login_notice_sec:
                state_now = state_menu
                MenuTool.reset_touchState(touch_count_map, over_prev_map)
                for key_name in touch_time_map:
                    touch_time_map[key_name] = 0.0
                menu_enable_time = now_time + menu_lock_reentry

        elif state_now == state_menu:
            # putText(화면, 문자열, 위치, 폰트, 크기, 색상(BGR), 두께)
            # - "MENU" 라벨을 좌하단에 출력해 현재 상태를 명시
            cv2.putText(canvas_img, "MENU", (20, frame_height - 55), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            # 사용 방법 안내 문구(2회 접촉 선택)
            cv2.putText(canvas_img, "Touch button 2 times to select (1 touch = 50%)", (20, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(canvas_img, f"Filter: {filter_name_map.get(filter_key_now, 'BASIC')}", (20, frame_height - 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 255, 200), 2)

            # 이번 프레임에서 실행할 액션(없으면 None)
            action_trigger = None
            # 잠금 시간이 지난 뒤에만 버튼 입력 허용
            input_enabled = now_time >= menu_enable_time

            for button in button_list:
                # 버튼 사양(중심좌표/크기/액션키) 추출
                center_x = button["center_x"]
                center_y = button["center_y"]
                width = button["width"]
                height = button["height"]
                action_key = button["action"]

                # 버튼 배경 이미지 + 버튼 텍스트를 같은 중심좌표에 출력
                DrawTool.draw_spriteCenter(canvas_img, button["sprite"], center_x, center_y)
                DrawTool.draw_textCenter(canvas_img, button["label"], center_x, center_y, font_scale=0.8, color=(255, 255, 255), thickness=2)

                # ROI(버튼 사각형)를 프레임 경계 안으로 계산
                x1 = max(0, center_x - width // 2)
                y1 = max(0, center_y - height // 2)
                x2 = min(frame_width, center_x + width // 2)
                y2 = min(frame_height, center_y + height // 2)

                # 버튼 영역 내 움직임 통계를 계산
                ratio_now, pixels_now, _ = MotionTool.calc_rectMotion(motion_mask, x1, y1, x2, y2)
                # 비율 + 픽셀 수 임계값을 동시에 만족해야 "접촉"으로 인정
                over_now = (ratio_now >= touch_ratio_min) and (pixels_now >= touch_pixels_min)

                # 접촉 중이면 초록 테두리, 아니면 회색 테두리
                border_color = (0, 255, 0) if over_now else (140, 140, 140)
                cv2.rectangle(canvas_img, (x1, y1), (x2, y2), border_color, 2)

                if input_enabled:
                    # 상승 에지: 직전 프레임 False -> 현재 True인 "막 닿은 순간"만 카운트
                    edge_up = over_now and (not over_prev_map[action_key])
                    # 같은 접촉이 너무 빠르게 중복 카운트되지 않게 쿨다운 적용
                    cooldown_ok = (now_time - touch_time_map[action_key]) > touch_cooldown

                    if edge_up and cooldown_ok:
                        # 버튼별 누적 접촉 수 증가(최대 touch_required)
                        touch_count_map[action_key] = min(touch_required, touch_count_map[action_key] + 1)
                        touch_time_map[action_key] = now_time
                        # 2회 채우면 해당 액션 확정
                        if touch_count_map[action_key] >= touch_required:
                            action_trigger = action_key

                # 다음 프레임의 edge-up 계산 기준으로 현재 상태 저장
                over_prev_map[action_key] = over_now

                # 진행바(0~100%) 계산 및 출력
                progress = touch_count_map[action_key] / float(touch_required)
                bar_x1 = x1 + 6
                bar_x2 = x2 - 6
                bar_y1 = y2 + 6
                bar_y2 = y2 + 14
                cv2.rectangle(canvas_img, (bar_x1, bar_y1), (bar_x2, bar_y2), (60, 60, 60), -1)
                fill_w = int((bar_x2 - bar_x1) * progress)
                cv2.rectangle(canvas_img, (bar_x1, bar_y1), (bar_x1 + fill_w, bar_y2), (0, 255, 0), -1)

            if not input_enabled:
                # 메뉴 잠금 중이면 남은 시간 안내
                remain = max(0.0, menu_enable_time - now_time)
                cv2.putText(canvas_img, f"Menu Ready In: {remain:.1f}s", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 255, 255), 2)

            # -------- 메뉴 분기점: 상태 전환 --------
            if action_trigger == "start":
                # 카운트다운 시작 시각 기록 후 상태 전환
                countdown_time_start = now_time
                state_now = state_countdown
                # 이전 입력 누적은 반드시 초기화(오작동 방지)
                MenuTool.reset_touchState(touch_count_map, over_prev_map)

            elif action_trigger == "mode":
                # 필터 설정 화면으로 전환
                state_now = state_setting
                MenuTool.reset_touchState(touch_count_map, over_prev_map)
                MenuTool.reset_touchState(setting_touch_count_map, setting_over_prev_map)
                for key_name in setting_touch_time_map:
                    setting_touch_time_map[key_name] = 0.0
                setting_enable_time = now_time + setting_lock_reentry
            elif action_trigger == "data":
                # Load latest result JSON for current login id.
                login_id = login_user.get("id", "GUEST") if isinstance(login_user, dict) else "GUEST"
                selected_obj, selected_path = ResultTool.load_latestResult(login_id)

                if selected_obj is None:
                    # If none exists, create one fallback record.
                    fallback_name = login_nickname if login_nickname else login_id
                    fallback_play = last_game_record.get("play_time", "N/A")
                    if str(fallback_play).strip().upper() == "N/A":
                        fallback_play = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    fallback_score = last_game_record.get("score", 0)
                    fallback_filter = last_game_record.get("filter", "BASIC")

                    try:
                        selected_path, selected_obj = ResultTool.save_gameResult(
                            fallback_name,
                            fallback_play,
                            fallback_score,
                            fallback_filter,
                            login_id=login_id,
                        )
                        print(f"[INFO] No previous record for {login_id}. Created fallback: {selected_path}")
                    except Exception as err:
                        print(f"[WARN] Failed to prepare fallback result: {err}")
                        selected_obj = {
                            "Name": fallback_name,
                            "PlayTime": str(fallback_play),
                            "Score": int(fallback_score),
                            "Filter": str(fallback_filter),
                            "LoginID": login_id,
                        }
                        selected_path = ""
                else:
                    print(f"[INFO] Latest record selected for {login_id}: {selected_path}")

                score_value = selected_obj.get("Score", 0)
                try:
                    score_value = int(score_value)
                except Exception:
                    score_value = 0

                data_selected_result = {
                    "Name": str(selected_obj.get("Name", login_id)),
                    "PlayTime": str(selected_obj.get("PlayTime", "N/A")),
                    "Score": score_value,
                    "Filter": str(selected_obj.get("Filter", "BASIC")),
                    "LoginID": str(selected_obj.get("LoginID", login_id)),
                }

                data_qr_text = QrTool.compose_resultText(
                    data_selected_result["Name"],
                    data_selected_result["PlayTime"],
                    data_selected_result["Score"],
                    data_selected_result["Filter"],
                )
                data_qr_image = QrTool.make_qrImage(data_qr_text, image_size=360)

                # Show 5-second prepare screen, then move to QR screen.
                data_prepare_start_time = now_time
                corner_exit_count = 0
                corner_exit_prev = False
                corner_exit_time = 0.0
                state_now = state_data_prepare
                MenuTool.reset_touchState(touch_count_map, over_prev_map)
                for key_name in touch_time_map:
                    touch_time_map[key_name] = 0.0

            elif action_trigger == "exit":
                # 루프 탈출 = 프로그램 종료
                break

        elif state_now == state_countdown:
            # 카운트다운 시작 이후 경과 시간
            elapsed = now_time - countdown_time_start

            if elapsed < 3.0:
                # 3초 구간 동안 3->2->1 출력
                number_now = 3 - int(elapsed)
                # 각 1초 안에서 크기를 점점 줄이는 연출
                phase = elapsed - int(elapsed)
                scale_now = 3.0 - (2.0 * phase)
                DrawTool.draw_textCenter(canvas_img, str(number_now), frame_width // 2, frame_height // 2, font_scale=scale_now, color=(255, 255, 255), thickness=4)

            elif elapsed < 3.5:
                # 숫자 뒤 짧게 START 표시
                DrawTool.draw_textCenter(canvas_img, "START", frame_width // 2, frame_height // 2, font_scale=1.8, color=(0, 255, 0), thickness=4)

            else:
                # 실제 게임 시작 시점
                score_now = 0
                game_time_start = now_time
                # 동시에 보일 타겟 수를 3개로 시작
                target_pool.spawn_targets(active_count=3, frame_width=frame_width, frame_height=frame_height, now_time=now_time)
                state_now = state_game

        elif state_now == state_game:
            # 게임 경과/남은 시간
            elapsed = now_time - game_time_start
            remain = max(0, int(game_sec - elapsed))

            # 시간이 된 비활성 타겟 재등장 처리
            target_pool.update_respawnTargets(now_time, frame_width, frame_height)

            # 현재 활성 타겟만 그리기/판정
            for target_obj in target_pool.list_activeTargets():
                DrawTool.draw_spriteCenter(canvas_img, target_obj.sprite_asset, target_obj.pos_x, target_obj.pos_y)

                # 스폰 보호 중이면 노란색 링으로 시각화
                ring_color = (0, 255, 0)
                if now_time < target_obj.guard_time_spawn:
                    ring_color = (0, 255, 255)
                cv2.circle(canvas_img, (int(target_obj.pos_x), int(target_obj.pos_y)), target_obj.hit_radius, ring_color, 1)

                # 보호 시간 중에는 히트 판정을 건너뜀
                if now_time < target_obj.guard_time_spawn or elapsed < hit_guard_start:
                    continue

                # 타겟 원을 포함하는 사각 ROI 계산
                x1 = max(0, int(target_obj.pos_x - target_obj.hit_radius))
                y1 = max(0, int(target_obj.pos_y - target_obj.hit_radius))
                x2 = min(frame_width, int(target_obj.pos_x + target_obj.hit_radius))
                y2 = min(frame_height, int(target_obj.pos_y + target_obj.hit_radius))

                # ROI 움직임 비율/픽셀 계산
                hit_ratio, hit_pixels, roi_area = MotionTool.calc_rectMotion(motion_mask, x1, y1, x2, y2)
                if roi_area <= 0:
                    continue

                # 같은 타겟 연속 히트 방지 쿨다운
                cooldown_ok = (now_time - target_obj.hit_time_last) > hit_cooldown
                if hit_ratio > hit_ratio_min and hit_pixels > 15 and cooldown_ok:
                    # 히트 성공: 점수 누적 + 타겟 비활성 + 재등장 예약
                    score_now += target_obj.score_gain
                    target_obj.hit_time_last = now_time
                    target_obj.deactivate_target(now_time, 0.25, 1.0)#사라진 직후 0.25~1초 사이로 랜덤한 시간 후에 출현

            # 점수 표시 putText:
            # 1) canvas_img : 출력 대상 프레임
            # 2) f"Score: {score_now}" : 현재 누적 점수 문자열
            # 3) (20,45) : 좌상단 근처 위치(좌하단 기준)
            # 4) FONT_HERSHEY_SIMPLEX : 폰트
            # 5) 1.1 : 폰트 크기
            # 6) (255,255,255) : 흰색(BGR)
            # 7) 2 : 글자 두께
            cv2.putText(canvas_img, f"Score: {score_now}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2)

            # 남은 시간 표시 putText (형식: 00초)
            cv2.putText(canvas_img, f"Time: {remain:02d}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 2)

            # 게임 시간 종료 시 결과 화면으로 전환
            if elapsed >= game_sec:
                # DATA QR에 쓸 마지막 게임 결과를 갱신
                last_game_record["play_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                last_game_record["score"] = score_now
                last_game_record["filter"] = filter_name_map.get(filter_key_now, "BASIC")

                # 게임 1회 종료 시점마다 결과 JSON을 자동 저장한다.
                save_name = login_nickname if str(login_nickname).strip() else "GUEST"
                save_login_id = "GUEST"
                if isinstance(login_user, dict):
                    save_login_id = str(login_user.get("id", "GUEST")).strip() or "GUEST"
                try:
                    saved_path, _ = ResultTool.save_gameResult(
                        save_name,
                        last_game_record["play_time"],
                        last_game_record["score"],
                        last_game_record["filter"],
                        login_id=save_login_id,
                    )
                    print(f"[INFO] Game result saved: {saved_path}")
                except Exception as err:
                    print(f"[WARN] Failed to save game result: {err}")

                result_time_start = now_time
                state_now = state_result

        elif state_now == state_result:
            # 결과 화면 경과/남은 시간
            elapsed = now_time - result_time_start
            remain = max(0, int(result_sec - elapsed))

            # 최종 결과 텍스트 3줄 출력
            DrawTool.draw_textCenter(canvas_img, "TIME OVER", frame_width // 2, frame_height // 2 - 40, font_scale=1.6, color=(0, 0, 255), thickness=3)
            DrawTool.draw_textCenter(canvas_img, f"FINAL SCORE: {score_now}", frame_width // 2, frame_height // 2 + 20, font_scale=1.2, color=(255, 255, 255), thickness=2)
            DrawTool.draw_textCenter(canvas_img, f"Back to menu: {remain}", frame_width // 2, frame_height // 2 + 70, font_scale=0.9, color=(200, 200, 200), thickness=2)

            if elapsed >= result_sec:
                # 메뉴 복귀 시 타겟 비활성 + 입력 상태 초기화 + 재진입 잠금
                state_now = state_menu
                target_pool.spawn_targets(active_count=0, frame_width=frame_width, frame_height=frame_height, now_time=now_time)
                MenuTool.reset_touchState(touch_count_map, over_prev_map)
                menu_enable_time = now_time + menu_lock_reentry

        elif state_now == state_setting:
            # 세팅 화면: 5개 필터 버튼을 메뉴와 같은 2회 접촉 방식으로 선택
            cv2.putText(canvas_img, "SETTING - FILTER", (20, frame_height - 55), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(canvas_img, "Touch filter button 2 times to apply", (20, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(canvas_img, f"Current: {filter_name_map.get(filter_key_now, 'BASIC')}", (20, frame_height - 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 255, 200), 2)

            action_trigger = None
            input_enabled = now_time >= setting_enable_time

            for button in setting_button_list:
                center_x = button["center_x"]
                center_y = button["center_y"]
                width = button["width"]
                height = button["height"]
                action_key = button["action"]

                DrawTool.draw_spriteCenter(canvas_img, button["sprite"], center_x, center_y)
                DrawTool.draw_textCenter(canvas_img, button["label"], center_x, center_y, font_scale=0.8, color=(255, 255, 255), thickness=2)

                x1 = max(0, center_x - width // 2)
                y1 = max(0, center_y - height // 2)
                x2 = min(frame_width, center_x + width // 2)
                y2 = min(frame_height, center_y + height // 2)

                ratio_now, pixels_now, _ = MotionTool.calc_rectMotion(motion_mask, x1, y1, x2, y2)
                over_now = (ratio_now >= touch_ratio_min) and (pixels_now >= touch_pixels_min)

                border_color = (0, 255, 0) if over_now else (140, 140, 140)
                cv2.rectangle(canvas_img, (x1, y1), (x2, y2), border_color, 2)

                # 현재 적용 중 필터 버튼은 노란 테두리로 강조
                if action_key == filter_key_now:
                    cv2.rectangle(canvas_img, (x1 + 3, y1 + 3), (x2 - 3, y2 - 3), (0, 255, 255), 2)

                if input_enabled:
                    edge_up = over_now and (not setting_over_prev_map[action_key])
                    cooldown_ok = (now_time - setting_touch_time_map[action_key]) > touch_cooldown

                    if edge_up and cooldown_ok:
                        setting_touch_count_map[action_key] = min(touch_required, setting_touch_count_map[action_key] + 1)
                        setting_touch_time_map[action_key] = now_time
                        if setting_touch_count_map[action_key] >= touch_required:
                            action_trigger = action_key

                setting_over_prev_map[action_key] = over_now

                progress = setting_touch_count_map[action_key] / float(touch_required)
                bar_x1 = x1 + 6
                bar_x2 = x2 - 6
                bar_y1 = y2 + 6
                bar_y2 = y2 + 14
                cv2.rectangle(canvas_img, (bar_x1, bar_y1), (bar_x2, bar_y2), (60, 60, 60), -1)
                fill_w = int((bar_x2 - bar_x1) * progress)
                cv2.rectangle(canvas_img, (bar_x1, bar_y1), (bar_x1 + fill_w, bar_y2), (0, 255, 0), -1)

            if not input_enabled:
                remain = max(0.0, setting_enable_time - now_time)
                cv2.putText(canvas_img, f"Setting Ready In: {remain:.1f}s", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 255, 255), 2)

            if action_trigger is not None:
                # 필터 적용 후 즉시 메뉴로 복귀(재시작 불필요)
                filter_key_now = action_trigger
                state_now = state_menu
                MenuTool.reset_touchState(setting_touch_count_map, setting_over_prev_map)
                for key_name in setting_touch_time_map:
                    setting_touch_time_map[key_name] = 0.0
                MenuTool.reset_touchState(touch_count_map, over_prev_map)
                for key_name in touch_time_map:
                    touch_time_map[key_name] = 0.0
                menu_enable_time = now_time + menu_lock_reentry

        elif state_now == state_data_prepare:
            elapsed = now_time - data_prepare_start_time
            remain = max(0, int(data_prepare_sec - elapsed + 0.999))

            selected_id = str(data_selected_result.get("LoginID", "GUEST"))
            selected_name = str(data_selected_result.get("Name", "GUEST"))
            selected_play = str(data_selected_result.get("PlayTime", "N/A"))
            selected_score = int(data_selected_result.get("Score", 0))
            selected_filter = str(data_selected_result.get("Filter", "BASIC"))

            cv2.putText(canvas_img, "DATA PREPARE", (20, frame_height - 55), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(canvas_img, f"Selected latest record for ID: {selected_id}", (20, frame_height - 90), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            cv2.putText(canvas_img, f"Sending selected data to QR... ({remain})", (20, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (180, 255, 180), 2)

            DrawTool.draw_textCenter(canvas_img, f"Name: {selected_name}", frame_width // 2, frame_height // 2 - 30, font_scale=0.85, color=(255, 255, 255), thickness=2)
            DrawTool.draw_textCenter(canvas_img, f"PlayTime: {selected_play}", frame_width // 2, frame_height // 2 + 5, font_scale=0.75, color=(220, 220, 220), thickness=2)
            DrawTool.draw_textCenter(canvas_img, f"Score: {selected_score}   Filter: {selected_filter}", frame_width // 2, frame_height // 2 + 38, font_scale=0.8, color=(220, 255, 220), thickness=2)

            if elapsed >= data_prepare_sec:
                data_qr_start_time = now_time
                corner_exit_count = 0
                corner_exit_prev = False
                corner_exit_time = 0.0
                state_now = state_data_qr

        elif state_now == state_data_qr:
            elapsed = now_time - data_qr_start_time
            remain = max(0, int(data_qr_sec - elapsed))

            cv2.putText(canvas_img, "DATA QR", (20, frame_height - 55), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(canvas_img, "Scan with your phone", (20, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            cv2.putText(canvas_img, f"Back to menu: {remain}", (20, frame_height - 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 255, 200), 2)

            if data_qr_image is not None:
                qr_h, qr_w = data_qr_image.shape[:2]
                qr_x1 = max(0, (frame_width // 2) - (qr_w // 2))
                qr_y1 = max(0, (frame_height // 2) - (qr_h // 2))
                qr_x2 = min(frame_width, qr_x1 + qr_w)
                qr_y2 = min(frame_height, qr_y1 + qr_h)
                canvas_img[qr_y1:qr_y2, qr_x1:qr_x2] = data_qr_image[0:(qr_y2 - qr_y1), 0:(qr_x2 - qr_x1)]
            else:
                DrawTool.draw_textCenter(canvas_img, "qrcode package not ready", frame_width // 2, frame_height // 2, font_scale=0.9, color=(0, 80, 255), thickness=2)

            # 데이터 화면 우상단 EXIT 버튼 (2회 접촉)
            exit_x2 = frame_width - 20
            exit_y1 = 20
            exit_x1 = max(0, exit_x2 - corner_exit_w)
            exit_y2 = exit_y1 + corner_exit_h

            cv2.rectangle(canvas_img, (exit_x1, exit_y1), (exit_x2, exit_y2), (30, 30, 30), -1)
            cv2.rectangle(canvas_img, (exit_x1, exit_y1), (exit_x2, exit_y2), (0, 165, 255), 2)
            DrawTool.draw_textCenter(canvas_img, "EXIT", (exit_x1 + exit_x2) // 2, (exit_y1 + exit_y2) // 2, font_scale=0.9, color=(255, 255, 255), thickness=2)

            ratio_now, pixels_now, _ = MotionTool.calc_rectMotion(motion_mask, exit_x1, exit_y1, exit_x2, exit_y2)
            over_now = (ratio_now >= touch_ratio_min) and (pixels_now >= touch_pixels_min)
            edge_up = over_now and (not corner_exit_prev)
            cooldown_ok = (now_time - corner_exit_time) > touch_cooldown
            if edge_up and cooldown_ok:
                corner_exit_count = min(touch_required, corner_exit_count + 1)
                corner_exit_time = now_time
            corner_exit_prev = over_now

            progress = corner_exit_count / float(touch_required)
            bar_x1 = exit_x1 + 6
            bar_x2 = exit_x2 - 6
            bar_y1 = exit_y2 + 6
            bar_y2 = exit_y2 + 14
            cv2.rectangle(canvas_img, (bar_x1, bar_y1), (bar_x2, bar_y2), (60, 60, 60), -1)
            fill_w = int((bar_x2 - bar_x1) * progress)
            cv2.rectangle(canvas_img, (bar_x1, bar_y1), (bar_x1 + fill_w, bar_y2), (0, 255, 0), -1)

            if corner_exit_count >= touch_required:
                break

            if elapsed >= data_qr_sec:
                state_now = state_menu
                corner_exit_count = 0
                corner_exit_prev = False
                corner_exit_time = 0.0
                MenuTool.reset_touchState(touch_count_map, over_prev_map)
                for key_name in touch_time_map:
                    touch_time_map[key_name] = 0.0
                menu_enable_time = now_time + menu_lock_reentry

        # 최종 합성 프레임 출력
        cv2.imshow("portfolio_game", canvas_img)

        # ESC(27) 키로 강제 종료
        if cv2.waitKey(10) == 27:
            break

    # 종료 시 자원 정리(카메라 해제 + 모든 창 닫기)
    cap_obj.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # 파일 단독 실행 시에만 main() 진입
    main()









































