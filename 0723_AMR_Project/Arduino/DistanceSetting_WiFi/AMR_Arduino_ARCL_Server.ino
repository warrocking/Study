#include <WiFiS3.h>

// ============================================================
// Network settings
// ============================================================
// ROBOT3_2G is an open Wi-Fi network. If a password is later added,
// replace WiFi.begin(WIFI_SSID) with WiFi.begin(WIFI_SSID, WIFI_PASS).
const char WIFI_SSID[] = "ROBOT3_2G";

// LD-90 connects to this Arduino TCP port through
// MobilePlanner > Outgoing ARCL connection setup.
const uint16_t ARCL_PORT = 5353;
const uint16_t WEB_PORT  = 80;

WiFiServer arclServer(ARCL_PORT);
WiFiServer webServer(WEB_PORT);
WiFiClient amrClient;

// ============================================================
// MobilePlanner route names - change these to the actual route names.
// Each route can include safe goal -> docking goal -> Precision Drive -> macros.
// ============================================================
const char ROUTE_ST1[] = "경로1";
const char ROUTE_ST2[] = "경로2";
const char ROUTE_ST3[] = "경로3";

String rxLine;
String lastCommand = "없음";
String lastResponse = "AMR 연결 대기 중";
String robotStatus = "연결 안 됨";
unsigned long lastWiFiAttempt = 0;
unsigned long lastStatusQuery = 0;

// ============================================================
// Setup / loop
// ============================================================
void setup()
{
  Serial.begin(115200);
  delay(1500);

  Serial.println("AMR Arduino ARCL Server 시작");
  connectWiFi();
}

void loop()
{
  maintainWiFi();
  acceptAMRConnection();
  readAMRResponses();
  handleWebClient();

  // Query status every 2 seconds only while the AMR is connected.
  if (amrClient && amrClient.connected() && millis() - lastStatusQuery >= 2000)
  {
    sendARCL("oneLineStatus");
    lastStatusQuery = millis();
  }
}

// ============================================================
// Wi-Fi
// ============================================================
void connectWiFi()
{
  if (WiFi.status() == WL_NO_MODULE)
  {
    Serial.println("UNO R4 WiFi 모듈을 찾지 못했습니다.");
    return;
  }

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
    startServers();
  }
  else
  {
    Serial.println("Wi-Fi 연결 실패 - 10초마다 재시도합니다.");
  }
}

void maintainWiFi()
{
  if (WiFi.status() == WL_CONNECTED)
  {
    return;
  }

  if (millis() - lastWiFiAttempt < 10000)
  {
    return;
  }

  lastWiFiAttempt = millis();
  WiFi.disconnect();
  WiFi.begin(WIFI_SSID);

  unsigned long started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 10000)
  {
    delay(250);
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    startServers();
  }
}

void startServers()
{
  arclServer.begin();
  webServer.begin();

  Serial.println("Wi-Fi 연결 성공");
  Serial.print("Arduino IP: ");
  Serial.println(WiFi.localIP());
  Serial.print("AMR Outgoing ARCL 목적지: ");
  Serial.print(WiFi.localIP());
  Serial.print(':');
  Serial.println(ARCL_PORT);
  Serial.print("제어 화면: http://");
  Serial.println(WiFi.localIP());
}

// ============================================================
// AMR TCP / ARCL communication
// ============================================================
void acceptAMRConnection()
{
  if (amrClient && amrClient.connected())
  {
    return;
  }

  WiFiClient incoming = arclServer.available();
  if (!incoming)
  {
    robotStatus = "연결 안 됨";
    return;
  }

  amrClient.stop();
  amrClient = incoming;
  rxLine = "";
  robotStatus = "연결됨";
  lastResponse = "LD-90이 Arduino 서버에 접속했습니다.";

  Serial.print("AMR 연결됨: ");
  Serial.println(amrClient.remoteIP());
  sendARCL("echo off");
  sendARCL("oneLineStatus");
}

void readAMRResponses()
{
  if (!amrClient || !amrClient.connected())
  {
    return;
  }

  while (amrClient.available())
  {
    char c = amrClient.read();

    if (c == '\n')
    {
      rxLine.trim();
      if (rxLine.length() > 0)
      {
        lastResponse = rxLine;
        Serial.print("AMR > ");
        Serial.println(rxLine);

        if (rxLine.startsWith("Status:") || rxLine.startsWith("OneLineStatus:"))
        {
          robotStatus = rxLine;
        }
      }
      rxLine = "";
    }
    else if (c != '\r' && rxLine.length() < 500)
    {
      rxLine += c;
    }
  }
}

bool sendARCL(const String &command)
{
  if (!amrClient || !amrClient.connected())
  {
    lastResponse = "명령 실패: AMR이 서버에 연결되지 않았습니다.";
    Serial.println(lastResponse);
    return false;
  }

  amrClient.println(command);
  lastCommand = command;
  Serial.print("Arduino > ");
  Serial.println(command);
  return true;
}

void runRoute(const char *routeName)
{
  sendARCL(String("patrolOnce ") + routeName);
}

// ============================================================
// Web controller
// ============================================================
void handleWebClient()
{
  WiFiClient client = webServer.available();
  if (!client)
  {
    return;
  }

  String requestLine;
  unsigned long started = millis();

  while (client.connected() && millis() - started < 1500)
  {
    if (client.available())
    {
      requestLine = client.readStringUntil('\n');

      // Discard the rest of the HTTP headers.
      while (client.available())
      {
        client.read();
      }
      break;
    }
  }

  executeWebCommand(requestLine);
  sendWebPage(client);
  delay(1);
  client.stop();
}

void executeWebCommand(const String &request)
{
  if      (request.indexOf("GET /cmd?c=route1 ") >= 0) runRoute(ROUTE_ST1);
  else if (request.indexOf("GET /cmd?c=route2 ") >= 0) runRoute(ROUTE_ST2);
  else if (request.indexOf("GET /cmd?c=route3 ") >= 0) runRoute(ROUTE_ST3);
  else if (request.indexOf("GET /cmd?c=status ") >= 0)  sendARCL("oneLineStatus");
  else if (request.indexOf("GET /cmd?c=stop ") >= 0)    sendARCL("stop");
}

void sendWebPage(WiFiClient &client)
{
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html; charset=utf-8");
  client.println("Cache-Control: no-store");
  client.println("Connection: close");
  client.println();

  client.println("<!doctype html><html lang='ko'><head><meta charset='utf-8'>");
  client.println("<meta name='viewport' content='width=device-width,initial-scale=1'>");
  client.println("<meta http-equiv='refresh' content='3'>");
  client.println("<title>LD-90 AMR 제어</title><style>");
  client.println("body{font-family:Arial,sans-serif;background:#eef2f6;margin:0;padding:18px;color:#17202a}");
  client.println("main{max-width:760px;margin:auto}.card{background:#fff;border-radius:14px;padding:18px;margin-bottom:14px;box-shadow:0 3px 12px #0002}");
  client.println(".ok{color:#087f23}.ng{color:#c62828}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}");
  client.println("a{display:block;text-align:center;text-decoration:none;background:#1565c0;color:white;padding:14px;border-radius:10px;font-weight:bold}");
  client.println("a.stop{background:#c62828}code{display:block;white-space:pre-wrap;word-break:break-all;background:#f5f7f9;padding:10px;border-radius:8px}");
  client.println("</style></head><body><main>");

  client.println("<div class='card'><h2>Arduino - LD-90 ARCL 서버</h2>");
  client.print("<p>AMR 연결: <b class='");
  client.print((amrClient && amrClient.connected()) ? "ok'>연결됨" : "ng'>연결 안 됨");
  client.println("</b></p>");
  client.print("<p>Arduino IP: "); client.print(WiFi.localIP());
  client.print(" / ARCL Port: "); client.print(ARCL_PORT); client.println("</p></div>");

  client.println("<div class='card'><h3>AMR 경로 실행</h3><div class='grid'>");
  addButton(client, "route1", "경로1 실행");
  addButton(client, "route2", "경로2 실행");
  addButton(client, "route3", "경로3 실행");
  addButton(client, "status", "상태 새로 요청");
  client.println("<a class='stop' href='/cmd?c=stop'>정지 명령</a>");
  client.println("</div></div>");

  client.println("<div class='card'><h3>통신 기록</h3>");
  client.print("<p>마지막 송신</p><code>"); printHtmlEscaped(client, lastCommand); client.println("</code>");
  client.print("<p>마지막 수신</p><code>"); printHtmlEscaped(client, lastResponse); client.println("</code>");
  client.print("<p>로봇 상태</p><code>"); printHtmlEscaped(client, robotStatus); client.println("</code>");
  client.println("</div></main></body></html>");
}

void addButton(WiFiClient &client, const char *command, const char *label)
{
  client.print("<a href='/cmd?c=");
  client.print(command);
  client.print("'>");
  client.print(label);
  client.println("</a>");
}

void printHtmlEscaped(WiFiClient &client, const String &text)
{
  for (unsigned int i = 0; i < text.length(); i++)
  {
    char c = text[i];
    if      (c == '&') client.print("&amp;");
    else if (c == '<') client.print("&lt;");
    else if (c == '>') client.print("&gt;");
    else               client.print(c);
  }
}
