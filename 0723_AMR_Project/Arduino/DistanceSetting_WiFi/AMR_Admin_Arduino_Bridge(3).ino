#include <WiFiS3.h>

/*
  Arduino UNO R4 WiFi <-> temporary Admin server <-> Omron LD-90

  Network
    Wi-Fi       : ROBOT_MA2_2G (open network)
    Admin PC    : 192.168.0.168:5000
    Arduino     : DHCP reservation recommended: 192.168.0.182
    LD-90       : connects OUT to Arduino TCP 5353

  Safe test sequence
    1) admin: prepare   -> query motors/routes/macros/status
    2) physically check E-stop and clear travel area
    3) admin: arm       -> enableMotors
    4) admin: start     -> patrolOnce ROUTE_ST1

  "cycle" runs MACRO_ST1 -> ST2 -> ST1 -> ST3 -> ST2 -> ST3.
  Use cycle only after the single ROUTE_ST1 test succeeds.
*/

const char WIFI_SSID[] = "ROBOT_MA2_2G";
IPAddress ADMIN_IP(192, 168, 0, 168);
const uint16_t ADMIN_PORT = 5000;
const uint16_t ARCL_PORT = 5353;
const char CLIENT_NAME[] = "amr";

const char ROUTE_ST1[] = "ROUTE_ST1";
const char ROUTE_ST2[] = "ROUTE_ST2";
const char ROUTE_ST3[] = "ROUTE_ST3";
const char MACRO_ST1[] = "MACRO_ST1";
const char MACRO_ST2[] = "MACRO_ST2";
const char MACRO_ST3[] = "MACRO_ST3";

const uint8_t CONVEYOR_PIN = 7;
const uint8_t CONVEYOR_ON_LEVEL = HIGH; // LOW-trigger relay: change to LOW
const uint8_t CONVEYOR_OFF_LEVEL =
    (CONVEYOR_ON_LEVEL == HIGH) ? LOW : HIGH;
const unsigned long RECEIVE_DELAY_MS = 3000;
const unsigned long MACRO_TIMEOUT_MS = 180000;
const unsigned long NEXT_MACRO_DELAY_MS = 1500;

WiFiServer arclServer(ARCL_PORT);
WiFiClient ld90;
WiFiClient admin;

String ldRx;
String adminRx;
unsigned long lastWiFiAttempt = 0;
unsigned long lastAdminAttempt = 0;
unsigned long macroStartedAt = 0;
unsigned long waitStartedAt = 0;
unsigned long nextMacroAt = 0;

bool motorsConfirmed = false;
bool macroRunning = false;
bool waitRunning = false;
bool conveyorRunning = false;
bool cycleRunning = false;
bool nextMacroPending = false;
String activeMacro;

const char *CYCLE[] = {
  MACRO_ST1, MACRO_ST2, MACRO_ST1, MACRO_ST3, MACRO_ST2, MACRO_ST3
};
const uint8_t CYCLE_COUNT = sizeof(CYCLE) / sizeof(CYCLE[0]);
uint8_t cycleStep = 0;

void sendLine(WiFiClient &client, const String &line) {
  if (client && client.connected()) client.println(line);
}

void report(const String &line) {
  Serial.println(line);
  sendLine(admin, line);
}

void conveyor(bool on) {
  digitalWrite(CONVEYOR_PIN, on ? CONVEYOR_ON_LEVEL : CONVEYOR_OFF_LEVEL);
  if (conveyorRunning != on) {
    conveyorRunning = on;
    report(on ? "EVENT CONVEYOR_ON pin=D7" : "EVENT CONVEYOR_OFF pin=D7");
  }
}

void clearRunState() {
  conveyor(false);
  macroRunning = false;
  waitRunning = false;
  cycleRunning = false;
  nextMacroPending = false;
  activeMacro = "";
}

bool sendARCL(const String &command) {
  if (!ld90 || !ld90.connected()) {
    report("ERROR LD90_DISCONNECTED command=\"" + command + "\"");
    return false;
  }
  sendLine(ld90, command);
  report("ARCL_TX " + command);
  return true;
}

void sendDiagnostics() {
  if (!sendARCL("queryMotors")) return;
  sendARCL("oneLineStatus");
  sendARCL("getRoutes");
  sendARCL("getMacros");
  sendARCL("queryFaults");
  report("EVENT DIAGNOSTICS_REQUESTED");
}

bool startMacro(const char *name) {
  if (!motorsConfirmed) {
    report("REJECTED MOTORS_NOT_CONFIRMED use=arm");
    return false;
  }
  if (macroRunning) {
    report("REJECTED AMR_BUSY macro=" + activeMacro);
    return false;
  }
  conveyor(false);
  waitRunning = false;
  activeMacro = name;
  if (!sendARCL(String("executeMacro ") + name)) return false;
  macroRunning = true;
  macroStartedAt = millis();
  return true;
}

void startCycle() {
  if (cycleRunning || macroRunning) {
    report("REJECTED AMR_BUSY");
    return;
  }
  cycleStep = 0;
  cycleRunning = true;
  report("EVENT CYCLE_START sequence=ST1,ST2,ST1,ST3,ST2,ST3");
  if (!startMacro(CYCLE[cycleStep])) {
    clearRunState();
    report("EVENT CYCLE_ABORT reason=FIRST_MACRO_REJECTED");
  }
}

void connectWiFi() {
  WiFi.begin(WIFI_SSID); // open Wi-Fi: no password argument
  unsigned long began = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - began < 20000) {
    delay(250);
  }
  if (WiFi.status() == WL_CONNECTED) {
    arclServer.begin();
    Serial.print("EVENT WIFI_ONLINE ip=");
    Serial.println(WiFi.localIP());
    Serial.println("EVENT ARCL_LISTENING port=5353");
  } else {
    Serial.println("ERROR WIFI_CONNECT_FAILED ssid=ROBOT_MA2_2G");
  }
}

void maintainConnections() {
  if (WiFi.status() != WL_CONNECTED) {
    motorsConfirmed = false;
    clearRunState();
    ld90.stop();
    admin.stop();
    if (millis() - lastWiFiAttempt >= 10000) {
      lastWiFiAttempt = millis();
      WiFi.disconnect();
      WiFi.begin(WIFI_SSID);
    }
    return;
  }

  if ((!admin || !admin.connected()) && millis() - lastAdminAttempt >= 3000) {
    lastAdminAttempt = millis();
    admin.stop();
    if (admin.connect(ADMIN_IP, ADMIN_PORT)) {
      adminRx = "";
      sendLine(admin, CLIENT_NAME);
      sendLine(admin, "EVENT ARDUINO_ONLINE ip=" + WiFi.localIP().toString());
      sendLine(admin, (ld90 && ld90.connected())
          ? "EVENT LD90_ONLINE arcl_port=5353"
          : "STATUS LD90_DISCONNECTED waiting_port=5353");
    }
  }

  if (!ld90 || !ld90.connected()) {
    WiFiClient incoming = arclServer.available();
    if (incoming) {
      ld90.stop();
      ld90 = incoming;
      ldRx = "";
      motorsConfirmed = false;
      report("EVENT LD90_ONLINE arcl_port=5353 remote=" + ld90.remoteIP().toString());
      sendDiagnostics();
    }
  }
}

void finishMacro(String name) {
  conveyor(false);
  macroRunning = false;
  waitRunning = false;
  activeMacro = "";
  report("EVENT MACRO_COMPLETE name=\"" + name + "\"");
  if (!cycleRunning) return;
  cycleStep++;
  if (cycleStep >= CYCLE_COUNT) {
    cycleRunning = false;
    report("EVENT CYCLE_COMPLETE");
  } else {
    nextMacroPending = true;
    nextMacroAt = millis() + NEXT_MACRO_DELAY_MS;
  }
}

void processLD90Line(String line) {
  line.trim();
  if (!line.length()) return;
  report("ARCL_RX " + line);

  String lower = line;
  lower.toLowerCase();
  if (lower.indexOf("motors enabled") >= 0 ||
      lower.indexOf("motors are enabled") >= 0) {
    motorsConfirmed = true;
    report("EVENT MOTORS_READY");
  }
  if (lower.indexOf("estop") >= 0 || lower.indexOf("motors disabled") >= 0) {
    motorsConfirmed = false;
    conveyor(false);
    report("REJECTED SAFETY_STATE detail=\"" + line + "\"");
  }
  if (line.startsWith("Executing macro ")) {
    activeMacro = line.substring(16);
    macroRunning = true;
    macroStartedAt = millis();
    report("EVENT MACRO_RUNNING name=\"" + activeMacro + "\"");
  } else if (macroRunning && line.startsWith("WaitState: Waiting") &&
             lower.indexOf("completed") < 0) {
    waitRunning = true;
    waitStartedAt = millis();
    report("EVENT DOCK_WAIT_STARTED conveyor_delay_ms=3000");
  } else if (lower.indexOf("waitstate: waiting completed") >= 0) {
    waitRunning = false;
    conveyor(false);
  } else if (line.startsWith("Completed macro ")) {
    finishMacro(line.substring(16));
  } else if (line.startsWith("Patrolling route ") && lower.indexOf(" once") >= 0) {
    report("EVENT ROUTE_STARTED");
  } else if (line.startsWith("Finished patrolling route ")) {
    report("EVENT ROUTE_COMPLETE route=\"" + line.substring(26) + "\"");
  }

  if (lower.indexOf("commanderror") >= 0 || lower.indexOf("failed") >= 0 ||
      lower.indexOf("interrupted") >= 0 || lower.indexOf("cannot") >= 0 ||
      lower.indexOf("unavailable") >= 0 || lower.indexOf("lost") >= 0) {
    conveyor(false);
    cycleRunning = false;
    nextMacroPending = false;
    report("EVENT MOVEMENT_REJECTED detail=\"" + line + "\"");
  }
}

void executeAdminCommand(String command) {
  command.trim();
  String lower = command;
  lower.toLowerCase();
  if (lower == "prepare" || lower == "diagnose") {
    motorsConfirmed = false;
    sendDiagnostics();
  } else if (lower == "arm") {
    motorsConfirmed = false;
    sendARCL("enableMotors");
    sendARCL("queryMotors");
  } else if (lower == "start" || lower == "route1") {
    if (!motorsConfirmed) report("REJECTED MOTORS_NOT_CONFIRMED use=arm");
    else sendARCL(String("patrolOnce ") + ROUTE_ST1);
  } else if (lower == "route2") {
    if (!motorsConfirmed) report("REJECTED MOTORS_NOT_CONFIRMED use=arm");
    else sendARCL(String("patrolOnce ") + ROUTE_ST2);
  } else if (lower == "route3") {
    if (!motorsConfirmed) report("REJECTED MOTORS_NOT_CONFIRMED use=arm");
    else sendARCL(String("patrolOnce ") + ROUTE_ST3);
  } else if (lower == "macro1") startMacro(MACRO_ST1);
  else if (lower == "macro2") startMacro(MACRO_ST2);
  else if (lower == "macro3") startMacro(MACRO_ST3);
  else if (lower == "cycle") startCycle();
  else if (lower == "stop") {
    clearRunState();
    sendARCL("stop");
    report("EVENT STOP_SENT");
  } else if (lower == "status") {
    report("STATUS wifi=" + String(WiFi.status() == WL_CONNECTED ? "ONLINE" : "OFFLINE") +
           " ld90=" + String(ld90 && ld90.connected() ? "ONLINE" : "OFFLINE") +
           " motors=" + String(motorsConfirmed ? "READY" : "NOT_CONFIRMED") +
           " conveyor=" + String(conveyorRunning ? "ON" : "OFF"));
    sendARCL("oneLineStatus");
    sendARCL("queryMotors");
  } else if (lower == "conveyor_on") conveyor(true);
  else if (lower == "conveyor_off") conveyor(false);
  else if (lower.startsWith("raw ")) sendARCL(command.substring(4));
  else report("ERROR UNKNOWN_COMMAND use=prepare,arm,start,stop,status,route1-3,macro1-3,cycle,raw");
}

void readClientLines(WiFiClient &client, String &buffer, bool fromLD90) {
  while (client && client.connected() && client.available()) {
    char c = client.read();
    if (c == '\n') {
      if (fromLD90) processLD90Line(buffer);
      else executeAdminCommand(buffer);
      buffer = "";
    } else if (c != '\r' && buffer.length() < 900) {
      buffer += c;
    }
  }
}

void updateTimedActions() {
  if (macroRunning && waitRunning && !conveyorRunning &&
      millis() - waitStartedAt >= RECEIVE_DELAY_MS) {
    report("EVENT PRODUCT_RECEIVED assumed=true");
    conveyor(true);
  }
  if (cycleRunning && nextMacroPending && (long)(millis() - nextMacroAt) >= 0) {
    nextMacroPending = false;
    if (!startMacro(CYCLE[cycleStep])) {
      clearRunState();
      report("EVENT CYCLE_ABORT reason=NEXT_MACRO_REJECTED");
    }
  }
  if (macroRunning && millis() - macroStartedAt >= MACRO_TIMEOUT_MS) {
    sendARCL("stop");
    clearRunState();
    report("EVENT MOVEMENT_REJECTED detail=MACRO_TIMEOUT");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1200);
  pinMode(CONVEYOR_PIN, OUTPUT);
  digitalWrite(CONVEYOR_PIN, CONVEYOR_OFF_LEVEL);
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("ERROR WIFI_MODULE_NOT_FOUND");
    return;
  }
  connectWiFi();
}

void loop() {
  maintainConnections();
  readClientLines(admin, adminRx, false);
  readClientLines(ld90, ldRx, true);
  updateTimedActions();
}
