#include <WiFiS3.h>

// Arduino UNO R4 WiFi
// admin PC -> Arduino("amr") -> LD-90 Outgoing ARCL

const char WIFI_SSID[] = "ROBOT3_2G";
// 비밀번호가 생기면 connectWiFi()의 WiFi.begin(WIFI_SSID)를
// WiFi.begin(WIFI_SSID, "비밀번호")로 변경하세요.

// 중요: Arduino와 같은 네트워크에서 접근 가능한 admin PC의 IPv4 주소입니다.
// Windows에서 ipconfig로 확인하세요. Arduino에는 Tailscale이 없으므로
// 일반적으로 100.x.x.x Tailscale 주소를 넣으면 연결되지 않습니다.
IPAddress ADMIN_IP(192, 168, 0, 100);  // 반드시 실제 admin PC 주소로 수정
const uint16_t ADMIN_PORT = 5000;
const char CLIENT_NAME[] = "amr";

// AMR 위 컨베이어 릴레이(또는 모터드라이버) 제어 출력입니다.
// Arduino 핀으로 모터를 직접 구동하지 마세요.
const uint8_t CONVEYOR_PIN = 7;
const uint8_t CONVEYOR_ON_LEVEL = HIGH; // LOW 트리거 릴레이면 LOW로 변경
const uint8_t CONVEYOR_OFF_LEVEL = (CONVEYOR_ON_LEVEL == HIGH) ? LOW : HIGH;

// MobilePlanner > Outgoing ARCL connection setup에서
// Arduino IP와 아래 포트를 지정합니다.
const uint16_t ARCL_PORT = 5353;

const char ROUTE_1[] = "경로1";
const char ROUTE_2[] = "경로2";
const char ROUTE_3[] = "경로3";

WiFiServer arclServer(ARCL_PORT);
WiFiClient amrClient;
WiFiClient adminClient;

String adminRx;
String amrRx;
unsigned long lastWiFiAttempt = 0;
unsigned long lastAdminAttempt = 0;
unsigned long lastStatusQuery = 0;
bool macroRunning = false;
bool conveyorRunning = false;
String activeMacro = "";

void reportToAdmin(const String &text);

void setConveyor(bool run)
{
  digitalWrite(CONVEYOR_PIN, run ? CONVEYOR_ON_LEVEL : CONVEYOR_OFF_LEVEL);
  if (conveyorRunning == run) return;

  conveyorRunning = run;
  reportToAdmin(run ? "CONVEYOR ON" : "CONVEYOR OFF");
}

void sendLine(WiFiClient &client, const String &text)
{
  if (client && client.connected()) client.println(text);
}

void reportToAdmin(const String &text)
{
  Serial.print("[상태] ");
  Serial.println(text);
  sendLine(adminClient, text);
}

void connectWiFi()
{
  Serial.print("Wi-Fi 연결 중: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID);

  unsigned long started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 20000)
  {
    delay(500);
    Serial.print('.');
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED)
  {
    arclServer.begin();
    Serial.print("Arduino IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("LD-90 Outgoing ARCL 포트: ");
    Serial.println(ARCL_PORT);
  }
}

void maintainWiFi()
{
  if (WiFi.status() == WL_CONNECTED) return;
  if (millis() - lastWiFiAttempt < 10000) return;

  lastWiFiAttempt = millis();
  setConveyor(false);
  macroRunning = false;
  activeMacro = "";
  adminClient.stop();
  amrClient.stop();
  WiFi.disconnect();
  WiFi.begin(WIFI_SSID);

  unsigned long started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 10000) delay(250);
  if (WiFi.status() == WL_CONNECTED) arclServer.begin();
}

void connectAdmin()
{
  if (WiFi.status() != WL_CONNECTED) return;
  if (adminClient && adminClient.connected()) return;
  if (millis() - lastAdminAttempt < 3000) return;

  lastAdminAttempt = millis();
  adminClient.stop();

  Serial.print("admin 서버 접속 시도: ");
  Serial.print(ADMIN_IP);
  Serial.print(':');
  Serial.println(ADMIN_PORT);

  if (adminClient.connect(ADMIN_IP, ADMIN_PORT))
  {
    adminRx = "";
    sendLine(adminClient, CLIENT_NAME);  // Server_admin의 접속 이름 등록
    sendLine(adminClient, "Arduino connected; waiting for LD-90");
    Serial.println("admin 서버 연결 성공: 이름 amr 등록");
  }
}

void acceptAMR()
{
  if (amrClient && amrClient.connected()) return;

  WiFiClient incoming = arclServer.available();
  if (!incoming) return;

  amrClient.stop();
  amrClient = incoming;
  amrRx = "";
  reportToAdmin("LD-90 connected");
  sendLine(amrClient, "echo off");
  sendLine(amrClient, "oneLineStatus");
}

bool sendARCL(const String &command)
{
  if (!amrClient || !amrClient.connected())
  {
    reportToAdmin("COMMAND FAILED - LD-90 disconnected: " + command);
    return false;
  }

  sendLine(amrClient, command);
  Serial.print("Arduino > LD-90: ");
  Serial.println(command);
  reportToAdmin("SENT TO LD-90: " + command);
  return true;
}

void executeAdminCommand(String command)
{
  command.trim();
  if (command.length() == 0) return;

  Serial.print("admin > Arduino: ");
  Serial.println(command);

  String lower = command;
  lower.toLowerCase();

  if (lower == "route1")       sendARCL(String("patrolOnce ") + ROUTE_1);
  else if (lower == "route2")  sendARCL(String("patrolOnce ") + ROUTE_2);
  else if (lower == "route3")  sendARCL(String("patrolOnce ") + ROUTE_3);
  else if (lower == "macro1")
  {
    activeMacro = "MACRO_ST1";
    macroRunning = sendARCL("executeMacro MACRO_ST1");
  }
  else if (lower == "macro2")
  {
    activeMacro = "MACRO_ST2";
    macroRunning = sendARCL("executeMacro MACRO_ST2");
  }
  else if (lower == "macro3")
  {
    activeMacro = "MACRO_ST3";
    macroRunning = sendARCL("executeMacro MACRO_ST3");
  }
  else if (lower == "status")  sendARCL("oneLineStatus");
  else if (lower == "stop")
  {
    setConveyor(false);
    macroRunning = false;
    activeMacro = "";
    sendARCL("stop");
  }
  else if (lower == "conveyor_on")  setConveyor(true);   // 배선 시험용
  else if (lower == "conveyor_off") setConveyor(false);  // 배선 시험용
  else if (lower.startsWith("raw ")) sendARCL(command.substring(4));
  else if (lower == "/quit")
  {
    reportToAdmin("Arduino bridge disconnecting from admin");
    adminClient.stop();
  }
  else
  {
    reportToAdmin("UNKNOWN COMMAND: " + command +
      " | use route1/2/3, macro1/2/3, conveyor_on/off, status, stop, raw <ARCL>");
  }
}

void readAdmin()
{
  if (!adminClient || !adminClient.connected()) return;

  while (adminClient.available())
  {
    char c = adminClient.read();
    if (c == '\n')
    {
      executeAdminCommand(adminRx);
      adminRx = "";
    }
    else if (c != '\r' && adminRx.length() < 300) adminRx += c;
  }
}

void readAMR()
{
  if (!amrClient || !amrClient.connected()) return;

  while (amrClient.available())
  {
    char c = amrClient.read();
    if (c == '\n')
    {
      amrRx.trim();
      if (amrRx.length() > 0)
      {
        Serial.print("LD-90 > Arduino: ");
        Serial.println(amrRx);
        sendLine(adminClient, "LD-90: " + amrRx);

        // 매크로의 PrecisionDrive 다음에 둔 wait(5)에 진입하면
        // 컨베이어를 켜고, wait 완료 응답이 오면 끕니다.
        if (amrRx.startsWith("Executing macro "))
        {
          macroRunning = true;
          activeMacro = amrRx.substring(String("Executing macro ").length());
          reportToAdmin("MACRO RUNNING: " + activeMacro);
        }
        else if (macroRunning &&
                 amrRx.startsWith("WaitState: Waiting") &&
                 amrRx.indexOf("completed") < 0)
        {
          setConveyor(true);
        }
        else if (macroRunning && amrRx.indexOf("WaitState: Waiting completed") >= 0)
        {
          setConveyor(false);
        }
        else if (amrRx.startsWith("Completed macro "))
        {
          setConveyor(false);
          macroRunning = false;
          reportToAdmin("MACRO COMPLETED: " + activeMacro);
          activeMacro = "";
        }
        else if (amrRx.indexOf("Failed") >= 0 ||
                 amrRx.indexOf("Error") >= 0 ||
                 amrRx.indexOf("Interrupted") >= 0)
        {
          setConveyor(false);
          macroRunning = false;
          reportToAdmin("MACRO/AMR ERROR: " + amrRx);
          activeMacro = "";
        }
      }
      amrRx = "";
    }
    else if (c != '\r' && amrRx.length() < 600) amrRx += c;
  }
}

void setup()
{
  Serial.begin(115200);
  delay(1200);

  pinMode(CONVEYOR_PIN, OUTPUT);
  digitalWrite(CONVEYOR_PIN, CONVEYOR_OFF_LEVEL);

  if (WiFi.status() == WL_NO_MODULE)
  {
    Serial.println("UNO R4 WiFi 모듈을 찾지 못했습니다.");
    return;
  }
  connectWiFi();
}

void loop()
{
  maintainWiFi();
  connectAdmin();
  acceptAMR();
  readAdmin();
  readAMR();

  // 상태 조회는 너무 자주 보내지 않고 5초마다 수행합니다.
  if (amrClient && amrClient.connected() && millis() - lastStatusQuery >= 5000)
  {
    sendLine(amrClient, "oneLineStatus");
    lastStatusQuery = millis();
  }
}
