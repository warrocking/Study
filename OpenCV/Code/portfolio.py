"""
OpenCV 손동작 메뉴 + 과일 터치 게임

[프로그램 목적]
- 카메라 영상의 "움직임"을 입력으로 사용해 메뉴 선택과 과일 맞추기 게임을 진행합니다.
- 마우스/키보드 없이 손동작만으로 시작/설정/종료 선택, 게임 플레이, 결과 표시까지 처리합니다.

[메인 실행 흐름]
1) 초기화
- 카메라 해상도 설정, 리소스 이미지 로드, Target/TargetPool 생성, 상태 변수 초기화를 수행합니다.
2) 프레임 입력 + 전처리
- 프레임 좌우반전 -> 그레이 변환 -> GaussianBlur -> 프레임 차분(absdiff) -> 이진화(threshold) 순으로
  움직임 마스크를 생성합니다.
3) 상태 머신(state_now) 분기
- menu: 상단 버튼 ROI의 움직임 비율로 버튼 선택을 판정합니다.
- countdown: 3, 2, 1, Start 텍스트 애니메이션 후 game 상태로 전환합니다.
- game: 타겟 스폰/재스폰, 원형 ROI 움직임량 기반 히트 판정, 점수 갱신을 수행합니다.
- result: 점수와 안내를 일정 시간 보여준 뒤 menu로 복귀합니다.
- setting: "추후 기능" 안내와 카운트다운 후 menu로 복귀합니다.
4) 렌더링
- 배경 프레임 위에 버튼/텍스트/타겟 스프라이트를 합성해 최종 화면을 만듭니다.
5) 종료
- ESC 또는 종료 버튼 선택 시 루프를 종료하고 카메라/창 리소스를 해제합니다.

[적용된 핵심 처리와 목적]
- GaussianBlur: 카메라 노이즈와 미세 떨림을 줄여 오검출(가짜 움직임)을 완화합니다.
- absdiff(프레임 차분): 이전 프레임과 현재 프레임의 차이를 계산해 "실제 움직임 후보"를 찾습니다.
- threshold(이진화): 작은 밝기 변화는 버리고, 의미 있는 변화만 0/255 마스크로 남깁니다.
- morphology(open/close): 소금-후추 노이즈 제거 + 끊긴 영역 연결로 안정적인 움직임 영역을 만듭니다.
- ROI 비율 판정: 전체 화면이 아니라 버튼/타겟 주변만 검사해 입력 정확도를 높입니다.
- TargetPool(풀링형 관리): 타겟을 매번 생성/삭제하지 않고 활성/비활성으로 재사용해 처리 부담을 줄입니다.
- 가드타임/쿨다운: 스폰 직후 즉시 제거/연속 중복 히트를 막아 게임 판정을 안정화합니다.
- 알파 블렌딩(draw_sprite_center): PNG 투명 채널을 유지해 과일 이미지를 자연스럽게 합성합니다.
- 상태 머신 구조: 메뉴/게임/결과 로직을 분리해 코드 가독성과 유지보수성을 높입니다.

[핵심 클래스 역할]
- Target: 타겟 1개의 위치, 반지름, 활성 상태, 재등장 시각, 히트 시각을 관리합니다.
- TargetPool: 여러 Target의 등장/비등장 스케줄을 묶어서 제어합니다.
- ImageTool: 파일 경로 탐색, 리소스 이미지 로드/전처리 유틸을 제공합니다.
- DrawTool: 텍스트/도형/스프라이트 출력 함수를 제공합니다.
- MotionTool: 움직임 마스크 생성과 입력 판정(ROI 기반)을 담당합니다.
- MenuTool: 버튼 상태 초기화/업데이트 등 메뉴 입력 보조를 담당합니다.
"""

# 경로 처리(리소스 폴더 탐색), 랜덤 값(위치/점수), 시간(쿨다운/경과시간) 계산용 모듈
import os
import random
import time

# OpenCV: 카메라/영상 처리/텍스트·도형 출력
# NumPy: 이미지(배열) 생성·합성 시 데이터 타입/채널 연산
import cv2
import numpy as np


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
        resource_dir = os.path.join(base_dir, "Resource")

        file_name_list = ["banana.png", "strawberry.png", "watermelon.png"]
        fruit_assets = []

        # 이미지가 존재하면 (이름, 이미지) 튜플로 적재
        for file_name in file_name_list:
            file_path = os.path.join(resource_dir, file_name)
            image_asset = ImageTool.load_resizedImage(file_path, (80, 80))
            if image_asset is None:
                print(f"[WARN] 이미지 로드 실패: {file_path}")
                continue
            fruit_assets.append((os.path.splitext(file_name)[0], image_asset))

        # 전부 실패한 경우에도 게임이 시작되게 fallback 1개를 넣는다.
        if not fruit_assets:
            fruit_assets.append(("fallback", ImageTool.make_fallbackCircle((80, 80))))

        return fruit_assets

    @staticmethod
    def load_squareAsset(sprite_size=(240, 130)):
        # 버튼 베이스 이미지(square.png) 로드
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        file_path = os.path.join(base_dir, "Resource", "square.png")
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
        print("WebCam is not define")
        return

    # 카메라 해상도 요청/적용
    frame_width, frame_height = camera_set(cap_obj, 1280, 720)
    print(frame_width, frame_height)

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
    color_list = [
        (235, 206, 135),  # sky blue (BGR)
        (255, 0, 0),      # blue (BGR)
        (0, 165, 255),    # orange (BGR)
    ]
    spec_list = [
        ("START", "start"),
        ("SETTING", "mode"),
        ("EXIT", "exit"),
    ]

    # 버튼 레이아웃 계산(3개 버튼을 상단 중앙 정렬)
    button_w, button_h = 240, 130
    gap_w = 40
    total_w = button_w * 3 + gap_w * 2
    start_x = max(0, (frame_width - total_w) // 2)
    center_y = 20 + (button_h // 2)

    button_list = []
    for idx, (label_text, action_key) in enumerate(spec_list):
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

    # 상태머신 상수: 문자열 오타를 줄이기 위해 상수로 정의
    state_menu = "menu"
    state_countdown = "countdown"
    state_game = "game"
    state_result = "result"
    state_setting = "setting_notice"
    state_now = state_menu

    # 메뉴 버튼 접촉 판정 임계값들
    touch_ratio_min = 0.025
    touch_pixels_min = 120
    touch_required = 2
    touch_cooldown = 0.25

    # 버튼별 상태 저장용 맵
    # - touch_count_map: 누적 접촉 횟수(2회면 선택)
    # - over_prev_map  : 직전 프레임 접촉 여부(상승 에지 판정용)
    # - touch_time_map : 마지막 접촉 시각(쿨다운)
    touch_count_map = {"start": 0, "mode": 0, "exit": 0}
    over_prev_map = {"start": False, "mode": False, "exit": False}
    touch_time_map = {"start": 0.0, "mode": 0.0, "exit": 0.0}

    # 메뉴 진입 직후 오작동 방지를 위한 입력 잠금 시간
    menu_lock_start = 1.6
    menu_lock_reentry = 0.8
    menu_enable_time = time.time() + menu_lock_start

    # 화면 지속 시간/게임 시간 설정
    score_now = 0
    game_sec = 60
    result_sec = 5
    setting_sec = 5

    game_time_start = 0.0
    result_time_start = 0.0
    setting_time_start = 0.0
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
            print("프레임을 읽지 못했습니다.")
            break

        # 거울 모드(사용자 기준 좌우가 직관적)
        frame_img = cv2.flip(frame_img, 1)

        # 모션 검출용 전처리
        gray_frame = cv2.cvtColor(frame_img, cv2.COLOR_BGR2GRAY)
        curr_filtered = MotionTool.filter_grayFrame(gray_frame)

        # 첫 프레임은 이전 프레임이 없으므로 현재 값을 복사
        if prev_filtered is None:
            prev_filtered = curr_filtered.copy()

        now_time = time.time()

        # 움직임 마스크 생성 후, 다음 비교를 위해 현재 프레임 저장
        motion_mask = MotionTool.build_diffMask(curr_filtered, prev_filtered)
        prev_filtered = curr_filtered.copy()

        # 표시용 캔버스
        canvas_img = frame_img.copy()

        if state_now == state_menu:
            # putText(화면, 문자열, 위치, 폰트, 크기, 색상(BGR), 두께)
            # - "MENU" 라벨을 좌하단에 출력해 현재 상태를 명시
            cv2.putText(canvas_img, "MENU", (20, frame_height - 55), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            # 사용 방법 안내 문구(2회 접촉 선택)
            cv2.putText(canvas_img, "Touch button 2 times to select (1 touch = 50%)", (20, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

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
                # 설정 안내 화면으로 전환
                setting_time_start = now_time
                state_now = state_setting
                MenuTool.reset_touchState(touch_count_map, over_prev_map)

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
            # 설정 안내 화면 경과/남은 시간
            elapsed = now_time - setting_time_start
            remain = max(0, int(setting_sec - elapsed))

            # 현재는 안내 문구만 보여주고 자동 복귀
            DrawTool.draw_textCenter(canvas_img, "추후 기능을 추가합니다", frame_width // 2, frame_height // 2 - 20, font_scale=1.0, color=(255, 255, 255), thickness=2)
            DrawTool.draw_textCenter(canvas_img, "Feature coming soon", frame_width // 2, frame_height // 2 + 20, font_scale=0.9, color=(180, 220, 255), thickness=2)
            DrawTool.draw_textCenter(canvas_img, f"Back to menu: {remain}", frame_width // 2, frame_height // 2 + 70, font_scale=0.9, color=(200, 200, 200), thickness=2)

            if elapsed >= setting_sec:
                # 안내 시간 종료 -> 메뉴 복귀
                state_now = state_menu
                MenuTool.reset_touchState(touch_count_map, over_prev_map)
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

