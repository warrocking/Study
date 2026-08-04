/*
  DistanceSetting_WiFi.ino  (WiFi 모델용 - ESP32 기준)

  목적:
    상단에 고정된 HuskyLens 카메라로 AMR 컨베이어 위의 빨강(좌)/파랑(우) 마커를 인식하고,
    각 마커가 목표 위치에서 허용 오차(mm) 이내에 있는지 판정한다.
    두 마커가 모두 오차 범위 안이면 "성공", 아니면 "재시도"로 판단하고
    그 결과를 WiFi로 서버(PC)에 TCP 문자열("Success" 또는 "Retry")로 전송한다.

  준비물 / 사전 작업 (코드로 자동화 불가, 반드시 먼저 할 것):
    1) 아두이노 Library Manager에서 "HUSKYLENS" (DFRobot) 라이브러리 설치
    2) HuskyLens 본체에서 카메라를 빨강 마커에 맞추고 러닝 버튼으로 학습 -> ID 1
       카메라를 파랑 마커에 맞추고 다시 학습 -> ID 2
       (Color Recognition 모드에서 학습된 순서대로 ID가 매겨짐)
    3) HuskyLens I2C 배선: SDA -> ESP32 GPIO21, SCL -> ESP32 GPIO22, VCC -> 3.3V, GND -> GND
    4) 아래 WIFI_SSID / WIFI_PASSWORD / SERVER_IP 를 실제 환경에 맞게 수정

  전송 방식:
    판정 주기(CHECK_INTERVAL_MS)마다 TCP로 서버에 접속해 "Success\n" 또는 "Retry\n"을
    한 줄 텍스트로 전송한다. 연결이 끊어져 있으면 매 주기마다 재접속을 시도한다.
*/

#include <Wire.h>
#include <HUSKYLENS.h>
#include <WiFi.h>

HUSKYLENS huskylens;
WiFiClient client;

// ==== WiFi / 서버 접속 정보 ====
const char *WIFI_SSID = "YOUR_WIFI_SSID";
const char *WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char *SERVER_IP = "192.168.0.100"; // 결과를 받을 PC/서버 IP
const int SERVER_PORT = 5000;            // 저장소 내 다른 TCP 통신과 동일한 포트 관례

// ==== HuskyLens에서 미리 학습해둔 색상 ID ====
#define ID_RED  1   // 좌측 마커
#define ID_BLUE 2   // 우측 마커

// ==== 보정 상수 (설치 후 실측하여 조정할 것) ====
#define TARGET_X_LEFT    80   // 빨강 마커가 정위치일 때의 목표 픽셀 X좌표
#define TARGET_X_RIGHT   240  // 파랑 마커가 정위치일 때의 목표 픽셀 X좌표
#define MM_PER_PIXEL     1.0  // 픽셀 1칸당 실제 거리(mm) - 카메라 높이에 따라 다름, 실측 필요
#define TOLERANCE_MM     50   // 허용 오차(mm), 30~50(3~5cm) 사이에서 조정

#define CHECK_INTERVAL_MS 200 // 판정 주기(ms)

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

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("WiFi 연결 중");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("WiFi 연결됨, IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (millis() - lastCheckMs < CHECK_INTERVAL_MS) {
    return;
  }
  lastCheckMs = millis();

  if (!huskylens.request()) {
    Serial.println("HuskyLens 요청 실패");
    sendResult(false);
    return;
  }

  int redX = 0;
  int blueX = 0;
  bool foundRed = findMarkerX(ID_RED, redX);
  bool foundBlue = findMarkerX(ID_BLUE, blueX);

  if (!foundRed || !foundBlue) {
    Serial.println("마커를 모두 찾지 못함 -> 재시도");
    sendResult(false);
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

  sendResult(success);
}

// 판정 결과를 서버로 TCP 전송한다. 연결이 없으면 먼저 재접속을 시도한다.
void sendResult(bool success) {
  if (!client.connected()) {
    if (!client.connect(SERVER_IP, SERVER_PORT)) {
      Serial.println("서버 접속 실패");
      return;
    }
  }
  client.print(success ? "Success\n" : "Retry\n");
}
