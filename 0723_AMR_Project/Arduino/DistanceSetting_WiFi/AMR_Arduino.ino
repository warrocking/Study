#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <HUSKYLENS.h>

/*
  Arduino UNO R4 WiFi <-> laptop Admin server <-> Omron LD-90 ARCL

  Confirmed network:
    Wi-Fi       ROBOT_MA2_2G (open network)
    Arduino     192.168.0.182 (static)
    LD-90       192.168.0.10:7171
    ARCL        password 1234
    Admin       UDP 5001 discovery, TCP 5000 commands

  HUSKYLENS:
    Protocol must be I2C.  A failed camera initialization never blocks Wi-Fi.
    Learned object ID 1 starts the conveyor only while an AMR macro is waiting.
*/

// ---------------------------- User settings ----------------------------
const char WIFI_SSID[] = "ROBOT_MA2_2G";
// This network is open. If a password is added later, replace
// WiFi.begin(WIFI_SSID) below with WiFi.begin(WIFI_SSID, "password").

IPAddress ARDUINO_IP(192, 168, 0, 182);
IPAddress DNS_IP(192, 168, 0, 1);
IPAddress GATEWAY_IP(192, 168, 0, 1);
IPAddress SUBNET_MASK(255, 255, 255, 0);

IPAddress LD90_IP(192, 168, 0, 10);
const uint16_t LD90_PORT = 7171;
const char ARCL_PASSWORD[] = "1234";
const char FIRMWARE_VERSION[] = "2026-08-04-sequence-conveyor-v4";

const char ROUTE_ST1[] = "ROUTE_ST1";
const char ROUTE_ST2[] = "ROUTE_ST2";
const char ROUTE_ST3[] = "ROUTE_ST3";
const char MACRO_ST1[] = "MACRO_ST1";
const char MACRO_ST2[] = "MACRO_ST2";
const char MACRO_ST3[] = "MACRO_ST3";

const uint8_t PRODUCT_OBJECT_ID = 1;  // HUSKYLENS learned ID
const uint8_t CONVEYOR_FORWARD_PIN = 10; // D10: forward
const uint8_t CONVEYOR_REVERSE_PIN = 11; // D11: reverse
const unsigned long CONVEYOR_RUN_MS = 5000;
// ----------------------------------------------------------------------

const char CLIENT_NAME[] = "amr";
const uint16_t ADMIN_TCP_PORT = 5000;
const uint16_t DISCOVERY_PORT = 5001;
const char DISCOVERY_REQUEST[] = "DISCOVER_AMR_ADMIN_V1";
const char DISCOVERY_REPLY[] = "AMR_ADMIN_V1";

const unsigned long WIFI_RETRY_MS = 15000;
const unsigned long ADMIN_DISCOVERY_MS = 3000;
const unsigned long ADMIN_RETRY_MS = 3000;
const unsigned long LD90_RETRY_MS = 5000;
const unsigned long ARCL_LOGIN_TIMEOUT_MS = 10000;
const unsigned long MOTION_TIMEOUT_MS = 180000;
const unsigned long NEXT_MACRO_DELAY_MS = 1500;
const unsigned long HUSKY_RETRY_MS = 10000;
const unsigned long HUSKY_POLL_MS = 150;

WiFiUDP discovery;
WiFiClient admin;
WiFiClient ld90;
HUSKYLENS huskylens;
IPAddress adminIP;

String adminRx;
String ldRx;
String activeMacro;
String activeRoute;

unsigned long lastWiFiAttempt = 0;
unsigned long lastDiscoveryAttempt = 0;
unsigned long lastAdminAttempt = 0;
unsigned long lastLD90Attempt = 0;
unsigned long ld90ConnectedAt = 0;
unsigned long motionStartedAt = 0;
unsigned long nextMacroAt = 0;
unsigned long conveyorStartedAt = 0;
unsigned long lastHuskyAttempt = 0;
unsigned long lastHuskyPoll = 0;

bool wifiWasOnline = false;
bool adminKnown = false;
bool arclAuthenticated = false;
bool motorsConfirmed = false;
bool macroRunning = false;
bool routeRunning = false;
bool waitRunning = false;
bool conveyorStartedInCurrentWait = false;
bool conveyorRunning = false;
bool cycleConveyorPending = false;
bool cycleRunning = false;
bool nextMacroPending = false;
bool huskyOnline = false;

const char *CYCLE[] = {
  MACRO_ST1, MACRO_ST2, MACRO_ST1, MACRO_ST3, MACRO_ST2, MACRO_ST3
};
enum ConveyorDirection : uint8_t {
  CONVEYOR_STOPPED,
  CONVEYOR_FORWARD,
  CONVEYOR_REVERSE
};
const ConveyorDirection CYCLE_CONVEYOR[] = {
  CONVEYOR_FORWARD, CONVEYOR_REVERSE, CONVEYOR_REVERSE,
  CONVEYOR_FORWARD, CONVEYOR_REVERSE, CONVEYOR_REVERSE
};
const uint8_t CYCLE_COUNT = sizeof(CYCLE) / sizeof(CYCLE[0]);
uint8_t cycleStep = 0;
uint8_t manualSequenceStep = 0;
ConveyorDirection conveyorDirection = CONVEYOR_STOPPED;

void sendLine(WiFiClient &client, const String &line) {
  if (client.connected()) client.println(line);
}

void report(const String &line) {
  Serial.println(line);
  sendLine(admin, line);
}

void stopConveyor() {
  // The interlock invariant: both outputs are LOW whenever stopped or changing
  // direction. D10 and D11 are never written HIGH at the same time.
  digitalWrite(CONVEYOR_FORWARD_PIN, LOW);
  digitalWrite(CONVEYOR_REVERSE_PIN, LOW);
  bool wasRunning = conveyorRunning;
  conveyorRunning = false;
  conveyorDirection = CONVEYOR_STOPPED;
  if (wasRunning) report("EVENT CONVEYOR_OFF D10=LOW D11=LOW");
}

void startConveyor(ConveyorDirection direction) {
  stopConveyor();
  if (direction == CONVEYOR_FORWARD) {
    digitalWrite(CONVEYOR_REVERSE_PIN, LOW);
    digitalWrite(CONVEYOR_FORWARD_PIN, HIGH);
    report("EVENT CONVEYOR_FORWARD D10=HIGH D11=LOW duration_ms=5000");
  } else if (direction == CONVEYOR_REVERSE) {
    digitalWrite(CONVEYOR_FORWARD_PIN, LOW);
    digitalWrite(CONVEYOR_REVERSE_PIN, HIGH);
    report("EVENT CONVEYOR_REVERSE D10=LOW D11=HIGH duration_ms=5000");
  } else {
    return;
  }
  conveyorDirection = direction;
  conveyorRunning = true;
  conveyorStartedAt = millis();
}

bool stationMatchesStep(const String &name, uint8_t step) {
  String station = name;
  station.toLowerCase();
  String expected = CYCLE[step];
  expected.toLowerCase();
  expected.replace("macro_", "");
  return station.indexOf(expected) >= 0;
}

ConveyorDirection conveyorForCurrentVisit(const String &name) {
  uint8_t step = cycleRunning ? cycleStep : manualSequenceStep;
  if (step >= CYCLE_COUNT || !stationMatchesStep(name, step)) {
    report("EVENT CONVEYOR_SKIPPED reason=SEQUENCE_MISMATCH expected=\"" +
           String(CYCLE[step < CYCLE_COUNT ? step : 0]) + "\" actual=\"" +
           name + "\"");
    return CONVEYOR_STOPPED;
  }
  ConveyorDirection direction = CYCLE_CONVEYOR[step];
  report("EVENT CONVEYOR_SEQUENCE step=" + String(step + 1) +
         " station=\"" + name + "\"");
  if (!cycleRunning) manualSequenceStep = (manualSequenceStep + 1) % CYCLE_COUNT;
  return direction;
}

void clearMotionState() {
  stopConveyor();
  macroRunning = false;
  routeRunning = false;
  waitRunning = false;
  conveyorStartedInCurrentWait = false;
  cycleRunning = false;
  nextMacroPending = false;
  cycleConveyorPending = false;
  activeMacro = "";
  activeRoute = "";
}

bool sendARCL(const String &command) {
  if (!ld90.connected() || !arclAuthenticated) {
    report("ERROR LD90_NOT_READY command=\"" + command + "\"");
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

bool motionAllowed() {
  if (!arclAuthenticated) {
    report("REJECTED LD90_NOT_READY");
    return false;
  }
  if (!motorsConfirmed) {
    report("REJECTED MOTORS_NOT_CONFIRMED use=arm");
    return false;
  }
  if (macroRunning || routeRunning || nextMacroPending) {
    report("REJECTED AMR_BUSY");
    return false;
  }
  return true;
}

bool startMacro(const char *name, bool fromCycle = false) {
  if (!fromCycle && !motionAllowed()) return false;
  if (fromCycle && (!arclAuthenticated || !motorsConfirmed ||
                    macroRunning || routeRunning)) return false;
  stopConveyor();
  waitRunning = false;
  conveyorStartedInCurrentWait = false;
  activeMacro = name;
  if (!sendARCL(String("executeMacro ") + name)) return false;
  macroRunning = true;
  motionStartedAt = millis();
  return true;
}

bool startRoute(const char *name) {
  if (!motionAllowed()) return false;
  stopConveyor();
  waitRunning = false;
  conveyorStartedInCurrentWait = false;
  activeRoute = name;
  if (!sendARCL(String("patrolOnce ") + name)) return false;
  routeRunning = true;
  motionStartedAt = millis();
  return true;
}

void startCycle() {
  if (!motionAllowed()) return;
  cycleStep = 0;
  manualSequenceStep = 0;
  cycleRunning = true;
  report("EVENT CYCLE_START sequence=ST1:FWD,ST2:REV,ST1:REV,ST3:FWD,ST2:REV,ST3:REV");
  if (!startMacro(CYCLE[cycleStep], true)) {
    clearMotionState();
    report("EVENT CYCLE_ABORT reason=FIRST_MACRO_REJECTED");
  }
}

void discoverAdmin() {
  discovery.beginPacket(IPAddress(255, 255, 255, 255), DISCOVERY_PORT);
  discovery.print(DISCOVERY_REQUEST);
  discovery.endPacket();
  Serial.println("STATUS ADMIN_DISCOVERY_SENT udp=5001");
}

void readDiscovery() {
  int packetSize = discovery.parsePacket();
  if (!packetSize) return;
  char buffer[80];
  int count = discovery.read(buffer, sizeof(buffer) - 1);
  if (count <= 0) return;
  buffer[count] = '\0';
  String reply(buffer);
  reply.trim();
  if (reply.startsWith(DISCOVERY_REPLY)) {
    adminIP = discovery.remoteIP();
    adminKnown = true;
    Serial.println("EVENT ADMIN_DISCOVERED ip=" + adminIP.toString());
  }
}

void beginWiFi() {
  lastWiFiAttempt = millis();
  WiFi.config(ARDUINO_IP, DNS_IP, GATEWAY_IP, SUBNET_MASK);
  WiFi.begin(WIFI_SSID);
  Serial.println("STATUS WIFI_CONNECTING ssid=ROBOT_MA2_2G static_ip=192.168.0.182");
}

void maintainWiFi() {
  if (WiFi.status() == WL_CONNECTED &&
      WiFi.localIP() == ARDUINO_IP) return;

  if (wifiWasOnline) {
    Serial.println("EVENT WIFI_OFFLINE");
    wifiWasOnline = false;
    adminKnown = false;
    arclAuthenticated = false;
    motorsConfirmed = false;
    admin.stop();
    ld90.stop();
    clearMotionState();
  }

  if (lastWiFiAttempt == 0 || millis() - lastWiFiAttempt >= WIFI_RETRY_MS) {
    WiFi.disconnect();
    delay(100);
    beginWiFi();
  }
}

void maintainConnections() {
  maintainWiFi();
  if (WiFi.status() != WL_CONNECTED || WiFi.localIP() != ARDUINO_IP) return;

  if (!wifiWasOnline) {
    wifiWasOnline = true;
    Serial.println("EVENT WIFI_ONLINE ip=" + WiFi.localIP().toString());
    discovery.stop();
    discovery.begin(DISCOVERY_PORT);
  }

  readDiscovery();
  if (!adminKnown && millis() - lastDiscoveryAttempt >= ADMIN_DISCOVERY_MS) {
    lastDiscoveryAttempt = millis();
    discoverAdmin();
  }

  if (adminKnown && !admin.connected() &&
      millis() - lastAdminAttempt >= ADMIN_RETRY_MS) {
    lastAdminAttempt = millis();
    admin.stop();
    if (admin.connect(adminIP, ADMIN_TCP_PORT)) {
      adminRx = "";
      sendLine(admin, CLIENT_NAME);
      sendLine(admin, "EVENT ARDUINO_ONLINE ip=" + WiFi.localIP().toString());
      sendLine(admin, arclAuthenticated
          ? "EVENT LD90_ONLINE ip=192.168.0.10 port=7171"
          : "STATUS LD90_CONNECTING ip=192.168.0.10 port=7171");
    }
  }

  if (!ld90.connected() && millis() - lastLD90Attempt >= LD90_RETRY_MS) {
    lastLD90Attempt = millis();
    arclAuthenticated = false;
    motorsConfirmed = false;
    clearMotionState();
    ld90.stop();
    if (ld90.connect(LD90_IP, LD90_PORT)) {
      ldRx = "";
      ld90ConnectedAt = millis();
      sendLine(ld90, ARCL_PASSWORD);
      report("EVENT LD90_TCP_ONLINE ip=192.168.0.10 port=7171");
      report("STATUS ARCL_AUTHENTICATING");
    }
  }

  if (ld90.connected() && !arclAuthenticated &&
      millis() - ld90ConnectedAt >= ARCL_LOGIN_TIMEOUT_MS) {
    report("ERROR ARCL_AUTH_TIMEOUT");
    ld90.stop();
  }
}

void finishMacro(const String &name) {
  stopConveyor();
  macroRunning = false;
  waitRunning = false;
  conveyorStartedInCurrentWait = false;
  activeMacro = "";
  report("EVENT MACRO_COMPLETE name=\"" + name + "\"");
  if (cycleRunning) {
    // The conveyor already ran during the MobilePlanner Wait action.
    cycleStep++;
    if (cycleStep >= CYCLE_COUNT) {
      cycleRunning = false;
      report("EVENT CYCLE_COMPLETE");
    } else {
      nextMacroPending = true;
      nextMacroAt = millis() + NEXT_MACRO_DELAY_MS;
    }
  }
}

void finishRoute(const String &name) {
  stopConveyor();
  routeRunning = false;
  waitRunning = false;
  conveyorStartedInCurrentWait = false;
  activeRoute = "";
  report("EVENT ROUTE_COMPLETE route=\"" + name + "\"");
}

void processLD90Line(String line) {
  line.trim();
  if (!line.length()) return;
  report("ARCL_RX " + line);
  String lower = line;
  lower.toLowerCase();

  if (lower.indexOf("incorrect password") >= 0 ||
      lower.indexOf("invalid password") >= 0) {
    report("ERROR ARCL_AUTH_FAILED");
    arclAuthenticated = false;
    ld90.stop();
    return;
  }

  // Per ACRL manual, a successful login returns the supported command list.
  if (!arclAuthenticated && lower == "end of commands") {
    arclAuthenticated = true;
    report("EVENT ARCL_AUTHENTICATED");
    report("EVENT LD90_ONLINE ip=192.168.0.10 port=7171");
    sendLine(ld90, "echo off");
    sendDiagnostics();
    return;
  }

  // queryMotors normally returns "Motors enabled". Some ARCL versions use
  // "Motors are enabled", so accept both forms.
  if (lower.indexOf("motors enabled") >= 0 ||
      lower.indexOf("motors are enabled") >= 0) {
    motorsConfirmed = true;
    report("EVENT MOTORS_READY");
  } else if (lower.indexOf("motors disabled") >= 0 ||
             lower.indexOf("motors are disabled") >= 0 ||
             lower.indexOf("estop") >= 0) {
    motorsConfirmed = false;
    stopConveyor();
    report("REJECTED SAFETY_STATE detail=\"" + line + "\"");
  }

  if (lower.startsWith("executing macro ")) {
    activeMacro = line.substring(String("Executing macro ").length());
    macroRunning = true;
    motionStartedAt = millis();
    report("EVENT MACRO_RUNNING name=\"" + activeMacro + "\"");
  } else if ((macroRunning || routeRunning) &&
             lower.startsWith("waitstate: waiting") &&
             lower.indexOf("completed") < 0) {
    waitRunning = true;
    if (!conveyorStartedInCurrentWait) {
      String stationName = macroRunning ? activeMacro : activeRoute;
      ConveyorDirection direction = conveyorForCurrentVisit(stationName);
      conveyorStartedInCurrentWait = true;
      report("EVENT DOCK_WAIT_STARTED station=\"" + stationName + "\"");
      if (direction == CONVEYOR_STOPPED) {
        report("EVENT CONVEYOR_SKIPPED reason=UNKNOWN_STATION name=\"" +
               stationName + "\"");
      } else {
        startConveyor(direction);
      }
    }
  } else if (lower.indexOf("waitstate: waiting completed") >= 0) {
    waitRunning = false;
    stopConveyor();
  } else if (macroRunning &&
             (lower.startsWith("completed macro ") ||
              lower.startsWith("completed executing macro ") ||
              lower.startsWith("finished macro "))) {
    // Use the macro we actually started. This avoids firmware-specific wording
    // and capitalization changing the station name extraction.
    String completedName = activeMacro;
    if (!completedName.length()) completedName = line;
    finishMacro(completedName);
  } else if (lower.startsWith("patrolling route ") &&
             lower.indexOf(" once") >= 0) {
    routeRunning = true;
    motionStartedAt = millis();
    report("EVENT ROUTE_STARTED route=\"" + activeRoute + "\"");
  } else if (routeRunning && lower.startsWith("finished patrolling route ")) {
    String completedRoute = activeRoute;
    if (!completedRoute.length()) {
      completedRoute = line.substring(String("Finished patrolling route ").length());
    }
    finishRoute(completedRoute);
  }

  if (lower.indexOf("commanderror") >= 0 || lower.indexOf("failed") >= 0 ||
      lower.indexOf("interrupted") >= 0 || lower.indexOf("cannot") >= 0 ||
      lower.indexOf("unavailable") >= 0 || lower.indexOf("lost") >= 0) {
    clearMotionState();
    report("EVENT MOVEMENT_REJECTED detail=\"" + line + "\"");
  }
}

void executeAdminCommand(String command) {
  command.trim();
  String lower = command;
  lower.toLowerCase();

  if (lower == "prepare" || lower == "diagnose") {
    motorsConfirmed = false;
    manualSequenceStep = 0;
    sendDiagnostics();
  } else if (lower == "arm") {
    motorsConfirmed = false;
    if (sendARCL("enableMotors")) sendARCL("queryMotors");
  } else if (lower == "start" || lower == "route1") startRoute(ROUTE_ST1);
  else if (lower == "route2") startRoute(ROUTE_ST2);
  else if (lower == "route3") startRoute(ROUTE_ST3);
  else if (lower == "macro1") startMacro(MACRO_ST1);
  else if (lower == "macro2") startMacro(MACRO_ST2);
  else if (lower == "macro3") startMacro(MACRO_ST3);
  else if (lower == "cycle") startCycle();
  else if (lower == "stop") {
    clearMotionState();
    sendARCL("stop");
    report("EVENT STOP_SENT");
  } else if (lower == "status") {
    report("STATUS firmware=" + String(FIRMWARE_VERSION) +
           " wifi=" + String(wifiWasOnline ? "ONLINE" : "OFFLINE") +
           " ip=" + WiFi.localIP().toString() +
           " admin=" + String(admin.connected() ? "ONLINE" : "OFFLINE") +
           " ld90=" + String(arclAuthenticated ? "ONLINE" : "OFFLINE") +
           " motors=" + String(motorsConfirmed ? "READY" : "NOT_CONFIRMED") +
           " husky=" + String(huskyOnline ? "ONLINE" : "OFFLINE") +
           " conveyor=" + String(conveyorRunning ? "ON" : "OFF") +
           " sequence_next_step=" + String(manualSequenceStep + 1));
    if (arclAuthenticated) {
      sendARCL("oneLineStatus");
      sendARCL("queryMotors");
    }
  } else if (lower == "conveyor_forward") startConveyor(CONVEYOR_FORWARD);
  else if (lower == "conveyor_reverse") startConveyor(CONVEYOR_REVERSE);
  else if (lower == "conveyor_off") stopConveyor();
  else if (lower.startsWith("raw ")) sendARCL(command.substring(4));
  else report("ERROR UNKNOWN_COMMAND use=prepare,arm,start,stop,status,route1-3,macro1-3,cycle,conveyor_forward,conveyor_reverse,conveyor_off,raw");
}

void readClientLines(WiFiClient &client, String &buffer, bool fromLD90) {
  while (client.connected() && client.available()) {
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

void maintainHuskyLens() {
  if (!huskyOnline) {
    if (lastHuskyAttempt != 0 && millis() - lastHuskyAttempt < HUSKY_RETRY_MS)
      return;
    lastHuskyAttempt = millis();
    huskyOnline = huskylens.begin(Wire);
    report(huskyOnline ? "EVENT HUSKYLENS_ONLINE protocol=I2C"
                       : "STATUS HUSKYLENS_OFFLINE retry_ms=10000");
    return;
  }

  if (millis() - lastHuskyPoll < HUSKY_POLL_MS) return;
  lastHuskyPoll = millis();
  if (!huskylens.request()) {
    huskyOnline = false;
    report("EVENT HUSKYLENS_OFFLINE reason=REQUEST_FAILED");
    return;
  }

  bool productSeen = false;
  while (huskylens.available()) {
    HUSKYLENSResult result = huskylens.read();
    if (result.ID == PRODUCT_OBJECT_ID) productSeen = true;
  }

  if (productSeen && macroRunning && waitRunning) {
    report("EVENT PRODUCT_DETECTED husky_id=" + String(PRODUCT_OBJECT_ID));
  }
}

void updateTimedActions() {
  if (conveyorRunning && millis() - conveyorStartedAt >= CONVEYOR_RUN_MS) {
    stopConveyor();
    if (cycleRunning && cycleConveyorPending) {
      cycleConveyorPending = false;
      cycleStep++;
      if (cycleStep >= CYCLE_COUNT) {
        cycleRunning = false;
        report("EVENT CYCLE_COMPLETE");
      } else {
        nextMacroPending = true;
        nextMacroAt = millis() + NEXT_MACRO_DELAY_MS;
      }
    }
  }

  if (cycleRunning && nextMacroPending &&
      (long)(millis() - nextMacroAt) >= 0) {
    nextMacroPending = false;
    if (!startMacro(CYCLE[cycleStep], true)) {
      clearMotionState();
      report("EVENT CYCLE_ABORT reason=NEXT_MACRO_REJECTED");
    }
  }

  if ((macroRunning || routeRunning) &&
      millis() - motionStartedAt >= MOTION_TIMEOUT_MS) {
    sendARCL("stop");
    clearMotionState();
    report("EVENT MOVEMENT_REJECTED detail=MOTION_TIMEOUT");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1200);

  pinMode(CONVEYOR_FORWARD_PIN, OUTPUT);
  pinMode(CONVEYOR_REVERSE_PIN, OUTPUT);
  digitalWrite(CONVEYOR_FORWARD_PIN, LOW);
  digitalWrite(CONVEYOR_REVERSE_PIN, LOW);
  Wire.begin();

  Serial.println("AMR bridge starting - static IP + direct ARCL + HUSKYLENS I2C");
  Serial.println(String("FIRMWARE ") + FIRMWARE_VERSION);
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("ERROR WIFI_MODULE_NOT_FOUND");
    while (true) delay(1000);
  }

  discovery.begin(DISCOVERY_PORT);
  beginWiFi();
}

void loop() {
  maintainConnections();
  readClientLines(admin, adminRx, false);
  readClientLines(ld90, ldRx, true);
  maintainHuskyLens();
  updateTimedActions();
}
