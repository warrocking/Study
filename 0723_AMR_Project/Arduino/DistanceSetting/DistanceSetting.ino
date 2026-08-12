/*
  DistanceSetting.ino  (비WiFi 모델용)

  목적:
    상단에 고정된 HuskyLens 카메라로 AMR 컨베이어 위의 빨강(좌)/파랑(우) 마커를 인식하고,
    각 마커가 목표 위치에서 허용 오차(mm) 이내에 있는지 판정한다.
    두 마커가 모두 오차 범위 안이면 "성공", 아니면 "재시도"로 판단하고
    그 결과를 디지털 출력 핀(PIN_SUCCESS / PIN_RETRY)으로 AMR 쪽에 알려준다.

  준비물 / 사전 작업 (코드로 자동화 불가, 반드시 먼저 할 것):
    1) 아두이노 Library Manager에서 "HUSKYLENS" (DFRobot) 라이브러리 설치
    2) HuskyLens 본체에서 카메라를 빨강 마커에 맞추고 러닝 버튼으로 학습 -> ID 1
       카메라를 파랑 마커에 맞추고 다시 학습 -> ID 2
       (Color Recognition 모드에서 학습된 순서대로 ID가 매겨짐)
    3) HuskyLens I2C 배선: SDA -> A4, SCL -> A5, VCC -> 5V, GND -> GND (Uno/Nano 기준)

  출력 핀:
    PIN_SUCCESS - 판정이 "성공"인 동안 계속 HIGH
    PIN_RETRY   - 판정이 "재시도"인 동안 계속 HIGH
    (둘은 항상 반대 상태 유지, AMR은 이 핀을 GPIO 입력으로 읽으면 됨)
*/

#include <Wire.h>
#include <HUSKYLENS.h>

HUSKYLENS huskylens;

// ==== HuskyLens에서 미리 학습해둔 색상 ID ====
#define ID_RED  1   // 좌측 마커
#define ID_BLUE 2   // 우측 마커

// ==== 보정 상수 (설치 후 실측하여 조정할 것) ====
#define TARGET_X_LEFT    80   // 빨강 마커가 정위치일 때의 목표 픽셀 X좌표
#define TARGET_X_RIGHT   240  // 파랑 마커가 정위치일 때의 목표 픽셀 X좌표
#define MM_PER_PIXEL     1.0  // 픽셀 1칸당 실제 거리(mm) - 카메라 높이에 따라 다름, 실측 필요
#define TOLERANCE_MM     50   // 허용 오차(mm), 30~50(3~5cm) 사이에서 조정

#define CHECK_INTERVAL_MS 200 // 판정 주기(ms)

// ==== 출력 핀 ====
#define PIN_SUCCESS 7
#define PIN_RETRY   8

unsigned long lastCheckMs = 0;

// HuskyLens 블록 중 지정한 ID를 찾아 중심 X좌표를 반환한다.
// 찾으면 true와 함께 xOut에 값을 채우고, 못 찾으면 false를 반환한다.
bool findMarkerX(int id, int &xOut) {
  while (huskylens.available()) {
    HUSKYLENSResult result = huskylens.read();
    if (result.ID == id) {
      xOut = result.xCenter;
      return true;
    }
  }
  return false;
}

void setup() {
  Serial.begin(115200);

  Wire.begin();
  while (!huskylens.begin(Wire)) {
    Serial.println("HuskyLens 연결 실패 - 배선을 확인하세요");
    delay(1000);
  }
  huskylens.writeAlgorithm(ALGORITHM_COLOR_RECOGNITION);

  pinMode(PIN_SUCCESS, OUTPUT);
  pinMode(PIN_RETRY, OUTPUT);
  digitalWrite(PIN_SUCCESS, LOW);
  digitalWrite(PIN_RETRY, HIGH); // 판정 전에는 "재시도" 상태로 시작
}

void loop() {
  if (millis() - lastCheckMs < CHECK_INTERVAL_MS) {
    return;
  }
  lastCheckMs = millis();

  if (!huskylens.request()) {
    Serial.println("HuskyLens 요청 실패");
    setResult(false);
    return;
  }

  int redX = 0;
  int blueX = 0;
  bool foundRed = findMarkerX(ID_RED, redX);
  bool foundBlue = findMarkerX(ID_BLUE, blueX);

  if (!foundRed || !foundBlue) {
    Serial.println("마커를 모두 찾지 못함 -> 재시도");
    setResult(false);
    return;
  }

  float errorLeftMM = abs(redX - TARGET_X_LEFT) * MM_PER_PIXEL;
  float errorRightMM = abs(blueX - TARGET_X_RIGHT) * MM_PER_PIXEL;
  bool success = (errorLeftMM <= TOLERANCE_MM) && (errorRightMM <= TOLERANCE_MM);

  Serial.print("좌 오차(mm): ");
  Serial.print(errorLeftMM);
  Serial.print(" / 우 오차(mm): ");
  Serial.print(errorRightMM);
  Serial.print(" -> ");
  Serial.println(success ? "성공" : "재시도");

  setResult(success);
}

// 판정 결과를 출력 핀에 반영한다.
void setResult(bool success) {
  digitalWrite(PIN_SUCCESS, success ? HIGH : LOW);
  digitalWrite(PIN_RETRY, success ? LOW : HIGH);
}
