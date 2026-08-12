#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <ctype.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

/*
  Arduino UNO R4 WiFi - AMR bridge V25 FIXED-6S-RETURN EXPLICIT-SIGNALS

  Main server <-> Arduino <-> Omron LD-90 ARCL

  One START command runs this entire process automatically twice:
    ST1 load -> ST2 unload/reload -> ST1 unload -> ST3 load
    -> ST2 unload/reload -> ST3 unload

  Every station route must finish its Precision Drive with an indefinite Wait.
  Arduino polls waitTaskState, detects WaitState/Pausing, performs the conveyor
  action, sends waitTaskCancel,
  waits for "Finished patrolling route", runs SAFE, then starts the next route.

  Route order per cycle: ST1, ST2, ST1, ST3, ST2, ST3
    - First cycle ST1 uses route START.
    - Second cycle ST1 uses route ROUTE_ST1.
    - Between every station route Arduino automatically runs SAFE.

  Conveyor order per cycle:
    1. ST1 FWD continuously until D2 detects the plate.
    2. ST2 REV 6 s, stop 10 s, then FWD until a new D2 detection.
    3. ST1 REV 6 s (D2 clear does not stop it early).
    4. ST3 FWD continuously until D2 detects the plate.
    5. ST2 REV 6 s, stop 10 s, then FWD until a new D2 detection.
    6. ST3 REV 6 s (D2 clear does not stop it early).

  Recommended: place ARCLSendText DOCKED_READY immediately after
  PrecisionDrive and before waitIndefinitely. If that task is unavailable,
  Arduino safely falls back to an actual "WaitState: Waiting" response.

  Arduino conveyor outputs:
    FWD  = D10 HIGH, D11 LOW
    REV  = D10 LOW,  D11 HIGH
    STOP = D10 LOW,  D11 LOW

  D10 and D11 are forced LOW before every direction change, so they are never
  intentionally driven HIGH at the same time.

  Object sensor:
    D2 HIGH = no object
    D2 LOW  = object detected
*/

// ---------- Network ----------
const char WIFI_SSID[] = "ROBOT_MA2_2G";
const char WIFI_PASSWORD[] = "";

const uint16_t ADMIN_SERVER_PORT = 5000;
const uint16_t DISCOVERY_SERVER_PORT = 5001;
const uint16_t DISCOVERY_LOCAL_PORT = 5002;
const char DISCOVERY_REQUEST[] = "AMR_SERVER_DISCOVER_V1 device=amr";
const char DISCOVERY_RESPONSE[] = "AMR_SERVER_V1 name=admin tcp_port=5000";

IPAddress LD90_IP(192, 168, 0, 10);
const uint16_t LD90_ARCL_PORT = 7171;
const char ARCL_PASSWORD[] = "1234";

const char FIRMWARE_VERSION[] = "AMR_Server_Bridge_V25_FIXED_6S_RETURN_EXPLICIT_SIGNALS";
const char DOCKED_READY_MARKER[] = "DOCKED_READY";

// ---------- I/O ----------
const uint8_t OBJECT_SENSOR_PIN = 2;
const uint8_t CONVEYOR_FWD_PIN = 10;
const uint8_t CONVEYOR_REV_PIN = 11;
const unsigned long CONVEYOR_DIRECTION_DEADTIME_MS = 20UL;

// ---------- Timings ----------
const unsigned long RETURN_REV_RUN_MS = 6000UL;
const unsigned long ST2_DELIVERY_REV_RUN_MS = 6000UL;
const unsigned long ST2_CHANGEOVER_WAIT_MS = 10000UL;
const unsigned long ST3_LOAD_FWD_RUN_MS = 5000UL;
const unsigned long ROUTE_TIMEOUT_MS = 10UL * 60UL * 1000UL;
const unsigned long HEARTBEAT_MS = 5000UL;
const unsigned long WIFI_RETRY_MS = 5000UL;
const unsigned long DISCOVERY_RETRY_MS = 3000UL;
const unsigned long ADMIN_RETRY_MS = 3000UL;
const unsigned long ARCL_RETRY_MS = 3000UL;
const unsigned long ARCL_LOGIN_TIMEOUT_MS = 10000UL;
const unsigned long DIAGNOSTIC_TIMEOUT_MS = 10000UL;
const unsigned long SENSOR_DEBOUNCE_MS = 50UL;
const unsigned long WAIT_STATE_POLL_MS = 500UL;
const unsigned long WAIT_STATE_FIRST_POLL_DELAY_MS = 500UL;

WiFiClient adminClient;
WiFiClient arclClient;
WiFiUDP discoveryUdp;

IPAddress discoveredAdminIP;
bool adminServerKnown = false;
bool discoveryUdpStarted = false;
bool wifiWasConnected = false;
bool adminWasConnected = false;

char adminLine[192];
size_t adminLineLength = 0;
char arclLine[288];
size_t arclLineLength = 0;
char discoveryBuffer[96];

enum ConveyorDirection : uint8_t {
  CONVEYOR_STOPPED,
  CONVEYOR_FWD,
  CONVEYOR_REV
};

enum StationAction : uint8_t {
  ACTION_LOAD_UNTIL_D2,
  ACTION_UNLOAD_REV_6S,
  ACTION_ST2_UNLOAD_WAIT_RELOAD,
};

struct ProcessStep {
  const char* route;
  StationAction action;
};

const ProcessStep PROCESS_SEQUENCE[] = {
  {"START",     ACTION_LOAD_UNTIL_D2},
  {"ROUTE_ST2", ACTION_ST2_UNLOAD_WAIT_RELOAD},
  {"ROUTE_ST1", ACTION_UNLOAD_REV_6S},
  {"ROUTE_ST3", ACTION_LOAD_UNTIL_D2},
  {"ROUTE_ST2", ACTION_ST2_UNLOAD_WAIT_RELOAD},
  {"ROUTE_ST3", ACTION_UNLOAD_REV_6S},
};

const uint8_t PROCESS_STEP_COUNT =
    sizeof(PROCESS_SEQUENCE) / sizeof(PROCESS_SEQUENCE[0]);

bool arclReady = false;
bool arclAuthenticated = false;
bool motorsCheckComplete = false;
bool motorsEnabled = false;
bool faultCheckInProgress = false;
bool faultCheckComplete = false;
bool faultDetected = false;

bool routeRunning = false;
bool conveyorRunning = false;
bool conveyorStartedForRoute = false;
bool lastObjectDetected = false;
bool rawObjectDetected = false;

enum WorkflowState : uint8_t {
  WORKFLOW_IDLE,
  WORKFLOW_STATION_ROUTE,
  WORKFLOW_LOADING_TO_D2,
  WORKFLOW_UNLOADING_TO_D2_CLEAR,
  WORKFLOW_UNLOADING_TIMED,
  WORKFLOW_ST2_WAIT_10S,
  WORKFLOW_FORWARD_TIMED,
  WORKFLOW_WAIT_ROUTE_FINISH,
  WORKFLOW_SAFE_ROUTE,
  WORKFLOW_COMPLETE
};

WorkflowState workflowState = WORKFLOW_IDLE;
bool dockWaitObserved = false;
bool sequenceStarted = false;
bool sensorArmedForLoad = false;
bool sensorArmedForUnload = false;
bool waitStateClearedForRoute = false;
bool waitCancelPending = false;

uint8_t expectedStep = 0;
uint8_t completedCycles = 0;
char activeRoute[32] = "";
ConveyorDirection activeDirection = CONVEYOR_STOPPED;

bool pendingRunRequested = false;
char pendingRunRoute[32] = "";
ConveyorDirection pendingRunDirection = CONVEYOR_STOPPED;

bool pendingArrival = false;
char pendingArrivalLine[64] = "";

unsigned long conveyorStartedAt = 0;
unsigned long routeStartedAt = 0;
unsigned long lastHeartbeatAt = 0;
unsigned long lastWiFiAttemptAt = 0;
unsigned long lastDiscoveryAt = 0;
unsigned long lastAdminAttemptAt = 0;
unsigned long lastArclAttemptAt = 0;
unsigned long arclConnectedAt = 0;
unsigned long diagnosticsRequestedAt = 0;
unsigned long lastSensorChangeAt = 0;
unsigned long lastWaitStatePollAt = 0;

char asciiLower(char c) {
  if (c >= 'A' && c <= 'Z') return static_cast<char>(c + ('a' - 'A'));
  return c;
}

bool equalsIgnoreCase(const char* left, const char* right) {
  if (left == nullptr || right == nullptr) return false;
  while (*left && *right) {
    if (asciiLower(*left) != asciiLower(*right)) return false;
    ++left;
    ++right;
  }
  return *left == '\0' && *right == '\0';
}

bool startsWithIgnoreCase(const char* text, const char* prefix) {
  if (text == nullptr || prefix == nullptr) return false;
  while (*prefix) {
    if (!*text || asciiLower(*text) != asciiLower(*prefix)) return false;
    ++text;
    ++prefix;
  }
  return true;
}

bool containsIgnoreCase(const char* text, const char* needle) {
  if (text == nullptr || needle == nullptr || !*needle) return false;
  for (const char* start = text; *start; ++start) {
    const char* a = start;
    const char* b = needle;
    while (*a && *b && asciiLower(*a) == asciiLower(*b)) {
      ++a;
      ++b;
    }
    if (!*b) return true;
  }
  return false;
}

char* trimInPlace(char* text) {
  if (text == nullptr) return text;
  while (*text == ' ' || *text == '\t' || *text == '\r' || *text == '\n') ++text;
  size_t length = strlen(text);
  while (length > 0) {
    char c = text[length - 1];
    if (c != ' ' && c != '\t' && c != '\r' && c != '\n') break;
    text[--length] = '\0';
  }
  return text;
}

const char* directionName(ConveyorDirection direction) {
  if (direction == CONVEYOR_FWD) return "FWD";
  if (direction == CONVEYOR_REV) return "REV";
  return "STOP";
}

const char* workflowName(WorkflowState state) {
  if (state == WORKFLOW_STATION_ROUTE) return "STATION_ROUTE";
  if (state == WORKFLOW_LOADING_TO_D2) return "LOADING_TO_D2";
  if (state == WORKFLOW_UNLOADING_TO_D2_CLEAR) return "UNLOADING_TO_D2_CLEAR";
  if (state == WORKFLOW_UNLOADING_TIMED) return "UNLOADING_TIMED";
  if (state == WORKFLOW_ST2_WAIT_10S) return "ST2_WAIT_10S";
  if (state == WORKFLOW_FORWARD_TIMED) return "FORWARD_TIMED";
  if (state == WORKFLOW_WAIT_ROUTE_FINISH) return "WAIT_ROUTE_FINISH";
  if (state == WORKFLOW_SAFE_ROUTE) return "SAFE_ROUTE";
  if (state == WORKFLOW_COMPLETE) return "COMPLETE";
  return "IDLE";
}

const char* stationNameForStep(uint8_t step) {
  if (step == 0 || step == 2) return "3abb";
  if (step == 1 || step == 4) return "4abb";
  if (step == 3 || step == 5) return "5abb";
  return "unknown";
}

const char* actionName(StationAction action) {
  if (action == ACTION_LOAD_UNTIL_D2) return "LOAD_UNTIL_D2";
  if (action == ACTION_UNLOAD_REV_6S) return "UNLOAD_REV_6S";
  if (action == ACTION_ST2_UNLOAD_WAIT_RELOAD) return "ST2_UNLOAD_WAIT_RELOAD";
  return "UNKNOWN";
}

ConveyorDirection parseDirection(const char* value) {
  if (equalsIgnoreCase(value, "FWD")) return CONVEYOR_FWD;
  if (equalsIgnoreCase(value, "REV")) return CONVEYOR_REV;
  return CONVEYOR_STOPPED;
}

void printIPAddress(const IPAddress& ip) {
  Serial.print(ip[0]); Serial.print('.');
  Serial.print(ip[1]); Serial.print('.');
  Serial.print(ip[2]); Serial.print('.');
  Serial.print(ip[3]);
}

bool sendArclRaw(const char* command);

void stopConveyor() {
  // Interlock: both direction commands must be OFF in the stopped state.
  digitalWrite(CONVEYOR_FWD_PIN, LOW);
  digitalWrite(CONVEYOR_REV_PIN, LOW);
  conveyorRunning = false;
  activeDirection = CONVEYOR_STOPPED;
  Serial.println("IO ARDUINO_CONVEYOR direction=STOP D10=LOW D11=LOW");
}

void startConveyor(ConveyorDirection direction) {
  // Break-before-make interlock: remove both commands before selecting one.
  stopConveyor();
  delay(CONVEYOR_DIRECTION_DEADTIME_MS);
  if (direction == CONVEYOR_FWD) {
    digitalWrite(CONVEYOR_REV_PIN, LOW);
    digitalWrite(CONVEYOR_FWD_PIN, HIGH);
  } else if (direction == CONVEYOR_REV) {
    digitalWrite(CONVEYOR_FWD_PIN, LOW);
    digitalWrite(CONVEYOR_REV_PIN, HIGH);
  } else {
    return;
  }
  activeDirection = direction;
  conveyorRunning = true;
  conveyorStartedAt = millis();
  Serial.print("IO ARDUINO_CONVEYOR direction=");
  Serial.print(directionName(direction));
  Serial.print(direction == CONVEYOR_FWD
                   ? " D10=HIGH D11=LOW"
                   : " D10=LOW D11=HIGH");
  Serial.print(" D2=");
  Serial.print(static_cast<unsigned int>(digitalRead(OBJECT_SENSOR_PIN)));
  Serial.println();
}

bool sendAdminRaw(const char* message) {
  Serial.println(message);
  if (!adminClient.connected()) return false;
  return adminClient.println(message) > 0;
}

bool sendAdminFormat(const char* format, ...) {
  char message[192];
  va_list arguments;
  va_start(arguments, format);
  vsnprintf(message, sizeof(message), format, arguments);
  va_end(arguments);
  return sendAdminRaw(message);
}

bool sendArclRaw(const char* command) {
  Serial.print("ARCL_TX ");
  Serial.println(command);
  if (!arclClient.connected()) return false;
  return arclClient.println(command) > 0;
}

bool sendArclFormat(const char* format, ...) {
  char command[96];
  va_list arguments;
  va_start(arguments, format);
  vsnprintf(command, sizeof(command), format, arguments);
  va_end(arguments);
  return sendArclRaw(command);
}

void clearActiveRoute() {
  routeRunning = false;
  conveyorStartedForRoute = false;
  activeRoute[0] = '\0';
  activeDirection = CONVEYOR_STOPPED;
}

void resetWorkflow() {
  workflowState = WORKFLOW_IDLE;
  dockWaitObserved = false;
  sequenceStarted = false;
  expectedStep = 0;
  completedCycles = 0;
  sensorArmedForLoad = false;
  sensorArmedForUnload = false;
  waitStateClearedForRoute = false;
  waitCancelPending = false;
}

void safetyStopForServerLoss() {
  stopConveyor();
  if (arclClient.connected()) sendArclRaw("stop");
  clearActiveRoute();
  resetWorkflow();
}

void invalidateAdminServer(bool stopForSafety) {
  if (stopForSafety) safetyStopForServerLoss();
  adminClient.stop();
  adminWasConnected = false;
  adminServerKnown = false;
  discoveredAdminIP = IPAddress(0, 0, 0, 0);
  adminLineLength = 0;
  adminLine[0] = '\0';
  pendingRunRequested = false;
  lastDiscoveryAt = millis() - DISCOVERY_RETRY_MS;
}

bool sameSubnet(const IPAddress& a, const IPAddress& b, const IPAddress& mask) {
  for (uint8_t i = 0; i < 4; ++i) {
    if ((a[i] & mask[i]) != (b[i] & mask[i])) return false;
  }
  return true;
}

IPAddress calculateBroadcast(const IPAddress& local, const IPAddress& mask) {
  return IPAddress(
      static_cast<uint8_t>(local[0] | static_cast<uint8_t>(~mask[0])),
      static_cast<uint8_t>(local[1] | static_cast<uint8_t>(~mask[1])),
      static_cast<uint8_t>(local[2] | static_cast<uint8_t>(~mask[2])),
      static_cast<uint8_t>(local[3] | static_cast<uint8_t>(~mask[3])));
}

void startDiscoveryUdp() {
  if (discoveryUdpStarted) discoveryUdp.stop();
  discoveryUdpStarted = discoveryUdp.begin(DISCOVERY_LOCAL_PORT) == 1;
  if (!discoveryUdpStarted) Serial.println("DISCOVERY_UDP_START_FAILED port=5002");
}

void sendDiscoveryPacket(const IPAddress& destination) {
  if (!discoveryUdp.beginPacket(destination, DISCOVERY_SERVER_PORT)) return;
  discoveryUdp.write(reinterpret_cast<const uint8_t*>(DISCOVERY_REQUEST),
                     strlen(DISCOVERY_REQUEST));
  discoveryUdp.endPacket();
}

void discoverAdminIfNeeded() {
  if (WiFi.status() != WL_CONNECTED || adminServerKnown || adminClient.connected()) return;
  if (!discoveryUdpStarted) startDiscoveryUdp();
  if (!discoveryUdpStarted || millis() - lastDiscoveryAt < DISCOVERY_RETRY_MS) return;
  lastDiscoveryAt = millis();
  IPAddress broadcast = calculateBroadcast(WiFi.localIP(), WiFi.subnetMask());
  sendDiscoveryPacket(broadcast);
  if (!(broadcast == IPAddress(255, 255, 255, 255))) {
    sendDiscoveryPacket(IPAddress(255, 255, 255, 255));
  }
  Serial.println("DISCOVERY_TX port=5001");
}

void readDiscoveryResponses() {
  if (!discoveryUdpStarted || adminServerKnown || WiFi.status() != WL_CONNECTED) return;
  int packetSize = discoveryUdp.parsePacket();
  while (packetSize > 0) {
    IPAddress remote = discoveryUdp.remoteIP();
    int stored = 0;
    while (discoveryUdp.available()) {
      int value = discoveryUdp.read();
      if (value < 0) break;
      if (stored < static_cast<int>(sizeof(discoveryBuffer) - 1)) {
        discoveryBuffer[stored++] = static_cast<char>(value);
      }
    }
    discoveryBuffer[stored] = '\0';
    while (stored > 0 &&
           (discoveryBuffer[stored - 1] == '\r' || discoveryBuffer[stored - 1] == '\n')) {
      discoveryBuffer[--stored] = '\0';
    }
    if (strcmp(discoveryBuffer, DISCOVERY_RESPONSE) == 0 &&
        sameSubnet(WiFi.localIP(), remote, WiFi.subnetMask())) {
      discoveredAdminIP = remote;
      adminServerKnown = true;
      Serial.print("DISCOVERY_RX server=");
      printIPAddress(discoveredAdminIP);
      Serial.println(" tcp_port=5000");
      return;
    }
    packetSize = discoveryUdp.parsePacket();
  }
}

void manageWiFi() {
  bool connected = WiFi.status() == WL_CONNECTED;
  if (connected && !wifiWasConnected) {
    wifiWasConnected = true;
    Serial.print("WIFI_CONNECTED ip=");
    printIPAddress(WiFi.localIP());
    Serial.println();
    invalidateAdminServer(false);
    startDiscoveryUdp();
    return;
  }
  if (!connected && wifiWasConnected) {
    wifiWasConnected = false;
    Serial.println("WIFI_DISCONNECTED");
    invalidateAdminServer(true);
    if (discoveryUdpStarted) discoveryUdp.stop();
    discoveryUdpStarted = false;
    arclClient.stop();
    arclReady = false;
    arclAuthenticated = false;
    motorsCheckComplete = false;
    faultCheckComplete = false;
    pendingRunRequested = false;
  }
  if (connected || millis() - lastWiFiAttemptAt < WIFI_RETRY_MS) return;
  lastWiFiAttemptAt = millis();
  stopConveyor();
  Serial.print("WIFI_CONNECTING ssid=");
  Serial.print(WIFI_SSID);
  Serial.println(WIFI_PASSWORD[0] == '\0' ? " security=OPEN" : " security=WPA");
  if (WIFI_PASSWORD[0] == '\0') WiFi.begin(WIFI_SSID);
  else WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void connectAdminIfNeeded() {
  if (WiFi.status() != WL_CONNECTED || !adminServerKnown || adminClient.connected()) return;
  if (millis() - lastAdminAttemptAt < ADMIN_RETRY_MS) return;
  lastAdminAttemptAt = millis();
  adminClient.stop();
  Serial.print("ADMIN_CONNECTING ");
  printIPAddress(discoveredAdminIP);
  Serial.println(":5000");
  if (!adminClient.connect(discoveredAdminIP, ADMIN_SERVER_PORT)) {
    adminServerKnown = false;
    lastDiscoveryAt = millis() - DISCOVERY_RETRY_MS;
    return;
  }
  adminClient.println("amr");
  adminWasConnected = true;
  Serial.print("ADMIN_CONNECTED server=");
  printIPAddress(discoveredAdminIP);
  Serial.println();
  sendAdminFormat("STATUS ONLINE firmware=%s", FIRMWARE_VERSION);
  if (pendingArrival && sendAdminRaw(pendingArrivalLine)) {
    Serial.print("ADMIN_REPLAY ");
    Serial.println(pendingArrivalLine);
    pendingArrival = false;
  }
}

void connectArclIfNeeded() {
  if (WiFi.status() != WL_CONNECTED || arclClient.connected()) return;
  if (millis() - lastArclAttemptAt < ARCL_RETRY_MS) return;
  lastArclAttemptAt = millis();
  arclReady = false;
  arclAuthenticated = false;
  motorsCheckComplete = false;
  motorsEnabled = false;
  faultCheckInProgress = false;
  faultCheckComplete = false;
  faultDetected = false;
  pendingRunRequested = false;
  arclClient.stop();
  Serial.println("ARCL_CONNECTING 192.168.0.10:7171");
  if (!arclClient.connect(LD90_IP, LD90_ARCL_PORT)) return;
  arclConnectedAt = millis();
  arclClient.println(ARCL_PASSWORD);
  sendAdminRaw("STATUS LD90_TCP_CONNECTED ARCL=AUTHENTICATING");
}

void monitorArclLogin() {
  if (!arclClient.connected() || arclAuthenticated) return;
  if (millis() - arclConnectedAt < ARCL_LOGIN_TIMEOUT_MS) return;
  Serial.println("ARCL_AUTH_TIMEOUT");
  sendAdminRaw("ERR ARCL_AUTH_TIMEOUT check=ARCL_PASSWORD");
  arclClient.stop();
}

void sendStatus() {
  sendAdminFormat(
      "STATUS cycle=%u/2 step=%u/6 workflow=%s routeRunning=%u object=%s arcl=%s motors=%s faults=%s",
      static_cast<unsigned int>(completedCycles + (sequenceStarted ? 1U : 0U)),
      static_cast<unsigned int>(expectedStep + 1), workflowName(workflowState),
      routeRunning ? 1U : 0U,
      lastObjectDetected ? "DETECTED" : "CLEAR",
      arclReady && arclClient.connected() ? "ONLINE" : "OFFLINE",
      motorsCheckComplete ? (motorsEnabled ? "ENABLED" : "NOT_READY") : "PENDING",
      faultCheckComplete ? (faultDetected ? "DETECTED" : "CLEAR") : "PENDING");
}

const char* currentStationRoute() {
  if (expectedStep == 0 && completedCycles > 0) return "ROUTE_ST1";
  return PROCESS_SEQUENCE[expectedStep].route;
}

void beginRoute(const char* route, ConveyorDirection direction) {
  if (routeRunning) {
    sendAdminFormat("ERR AMR_BUSY active=%s", activeRoute);
    return;
  }
  if (!arclReady || !arclClient.connected()) {
    sendAdminRaw("ERR LD90_ARCL_OFFLINE");
    return;
  }
  if (!motorsCheckComplete || !faultCheckComplete) {
    sendAdminRaw("ERR LD90_SAFETY_CHECK_PENDING");
    pendingRunRequested = true;
    strncpy(pendingRunRoute, route, sizeof(pendingRunRoute) - 1);
    pendingRunRoute[sizeof(pendingRunRoute) - 1] = '\0';
    pendingRunDirection = direction;
    sendArclRaw("faultsGet");
    faultCheckInProgress = true;
    faultCheckComplete = false;
    faultDetected = false;
    diagnosticsRequestedAt = millis();
    sendArclRaw("queryMotors");
    return;
  }
  if (!motorsEnabled) { sendAdminRaw("ERR LD90_MOTORS_NOT_ENABLED"); return; }
  if (faultDetected) { sendAdminRaw("ERR LD90_FAULT_PRESENT"); return; }

  bool isSafeRoute = equalsIgnoreCase(route, "SAFE");
  if (isSafeRoute) {
    if (!sequenceStarted || workflowState != WORKFLOW_WAIT_ROUTE_FINISH) {
      sendAdminRaw("ERR SAFE_NOT_EXPECTED");
      return;
    }
    workflowState = WORKFLOW_SAFE_ROUTE;
    direction = CONVEYOR_STOPPED;
  } else {
    const char* expectedRoute = currentStationRoute();
    if (!sequenceStarted || workflowState != WORKFLOW_IDLE ||
        !equalsIgnoreCase(route, expectedRoute)) {
      sendAdminFormat("ERR SEQUENCE_MISMATCH expected=%s received=%s",
                      expectedRoute, route);
      return;
    }
    workflowState = WORKFLOW_STATION_ROUTE;
    dockWaitObserved = false;
    sensorArmedForLoad = false;
    sensorArmedForUnload = false;
    waitStateClearedForRoute = false;
    waitCancelPending = false;
    lastWaitStatePollAt = 0;
    direction = CONVEYOR_STOPPED;
  }
  routeRunning = true;
  conveyorStartedForRoute = false;
  strncpy(activeRoute, route, sizeof(activeRoute) - 1);
  activeRoute[sizeof(activeRoute) - 1] = '\0';
  activeDirection = direction;
  routeStartedAt = millis();
  const char* destination = isSafeRoute ? "safe" : stationNameForStep(expectedStep);
  sendAdminFormat("EVENT MOVE_STARTED destination=%s cycle=%u step=%u route=%s workflow=%s",
                  destination,
                  static_cast<unsigned int>(completedCycles + 1),
                  static_cast<unsigned int>(expectedStep + 1), activeRoute,
                  workflowName(workflowState));
  sendAdminFormat("STATUS ROUTE_START destination=%s cycle=%u step=%u route=%s direction=%s workflow=%s",
                  destination,
                  static_cast<unsigned int>(completedCycles + 1),
                  static_cast<unsigned int>(expectedStep + 1), activeRoute,
                  directionName(activeDirection), workflowName(workflowState));
  sendArclFormat("patrolOnce %s", activeRoute);
}

void retryPendingRunIfReady() {
  if (!pendingRunRequested || !motorsCheckComplete || !faultCheckComplete) return;
  pendingRunRequested = false;
  char route[32];
  strncpy(route, pendingRunRoute, sizeof(route) - 1);
  route[sizeof(route) - 1] = '\0';
  ConveyorDirection direction = pendingRunDirection;
  sendAdminRaw("STATUS RUN_RETRY_AFTER_SAFETY_CHECK");
  beginRoute(route, direction);
}

void failActiveRoute(const char* reason);

void finishDockTransfer() {
  stopConveyor();
  workflowState = WORKFLOW_WAIT_ROUTE_FINISH;
  waitCancelPending = true;
  lastWaitStatePollAt = 0;
  sendAdminFormat(
      "EVENT TRANSFER_DONE station=%s cycle=%u step=%u route=%s action=%s",
      stationNameForStep(expectedStep),
      static_cast<unsigned int>(completedCycles + 1),
      static_cast<unsigned int>(expectedStep + 1), activeRoute,
      actionName(PROCESS_SEQUENCE[expectedStep].action));
  sendAdminFormat("STATUS TRANSFER_DONE cycle=%u step=%u next=CONFIRM_AND_CANCEL_WAIT",
                  static_cast<unsigned int>(completedCycles + 1),
                  static_cast<unsigned int>(expectedStep + 1));
  if (arclClient.connected()) sendArclRaw("waitTaskState");
  else failActiveRoute("ARCL_DISCONNECTED_BEFORE_WAIT_CANCEL");
}

void startLoadUntilD2(bool requireClearBeforeDetection) {
  workflowState = WORKFLOW_LOADING_TO_D2;
  sensorArmedForLoad = requireClearBeforeDetection ? !lastObjectDetected : true;
  startConveyor(CONVEYOR_FWD);

  // Preserve the current server's legacy 3abb/5abb tags without allowing the
  // ST2 reload movement to be mistaken for arrival at 3abb.
  const char* mode =
      expectedStep == 0 ? "UNTIL_D2"
                        : (expectedStep == 3 ? "ST3_LOAD_UNTIL_D2"
                                             : "ST2_RELOAD_UNTIL_D2");
  sendAdminFormat(
      "STATUS CONVEYOR_START direction=FWD mode=%s station=%s cycle=%u step=%u route=%s sensorArmed=%u",
      mode, stationNameForStep(expectedStep),
      static_cast<unsigned int>(completedCycles + 1),
      static_cast<unsigned int>(expectedStep + 1), activeRoute,
      sensorArmedForLoad ? 1U : 0U);
  if (lastObjectDetected && sensorArmedForLoad) finishDockTransfer();
}

void startUnloadUntilD2Clear() {
  workflowState = WORKFLOW_UNLOADING_TO_D2_CLEAR;
  // Require proof that a plate was present before accepting D2 HIGH as unload.
  sensorArmedForUnload = lastObjectDetected;
  startConveyor(CONVEYOR_REV);
  sendAdminFormat("STATUS CONVEYOR_START direction=REV mode=UNTIL_D2_CLEAR sensorArmed=%u",
                  sensorArmedForUnload ? 1U : 0U);
}

void startDockAction() {
  if (!routeRunning || workflowState != WORKFLOW_STATION_ROUTE ||
      dockWaitObserved) return;
  dockWaitObserved = true;
  conveyorStartedForRoute = true;
  StationAction action = PROCESS_SEQUENCE[expectedStep].action;
  sendAdminFormat(
      "EVENT DOCK_ARRIVED station=%s cycle=%u step=%u route=%s action=%s",
      stationNameForStep(expectedStep),
      static_cast<unsigned int>(completedCycles + 1),
      static_cast<unsigned int>(expectedStep + 1), activeRoute,
      actionName(action));
  if (action == ACTION_LOAD_UNTIL_D2) {
    startLoadUntilD2(false);
  } else {
    workflowState = WORKFLOW_UNLOADING_TIMED;
    startConveyor(CONVEYOR_REV);
    unsigned long reverseMs =
        action == ACTION_ST2_UNLOAD_WAIT_RELOAD
            ? ST2_DELIVERY_REV_RUN_MS
            : RETURN_REV_RUN_MS;
    const char* mode = action == ACTION_ST2_UNLOAD_WAIT_RELOAD
                           ? "ST2_UNLOAD_TIMER"
                           : "RETURN_UNLOAD_6S";
    sendAdminFormat(
        "STATUS CONVEYOR_START direction=REV mode=%s station=%s cycle=%u step=%u route=%s timer_ms=%lu",
        mode, stationNameForStep(expectedStep),
        static_cast<unsigned int>(completedCycles + 1),
        static_cast<unsigned int>(expectedStep + 1), activeRoute, reverseMs);
  }
}

void handleAdminCommand(char* rawCommand) {
  char* command = trimInPlace(rawCommand);
  if (!*command) return;

  if (equalsIgnoreCase(command, "START")) {
    if (routeRunning || sequenceStarted) {
      sendAdminFormat("ERR AMR_BUSY active=%s", activeRoute);
      return;
    }
    if (!arclReady || !arclClient.connected()) {
      sendAdminRaw("ERR START_REJECTED reason=LD90_ARCL_OFFLINE");
      return;
    }
    if (motorsCheckComplete && !motorsEnabled) {
      sendAdminRaw("ERR START_REJECTED reason=LD90_MOTORS_NOT_ENABLED");
      return;
    }
    if (faultCheckComplete && faultDetected) {
      sendAdminRaw("ERR START_REJECTED reason=LD90_FAULT_PRESENT");
      return;
    }
    resetWorkflow();
    sequenceStarted = true;
    sendAdminRaw("EVENT START_ACCEPTED mode=AUTO_2_CYCLES cycles=2 steps=12 first_station=3abb route=START");
    beginRoute(currentStationRoute(), CONVEYOR_STOPPED);
    return;
  }

  if (equalsIgnoreCase(command, "STOP") || equalsIgnoreCase(command, "ESTOP")) {
    stopConveyor();
    if (arclClient.connected()) sendArclRaw("stop");
    clearActiveRoute();
    resetWorkflow();
    pendingRunRequested = false;
    sendAdminRaw("STATUS STOPPED");
    return;
  }
  if (equalsIgnoreCase(command, "STATUS")) { sendStatus(); return; }
  if (equalsIgnoreCase(command, "RESET_SEQUENCE")) {
    if (routeRunning) sendAdminRaw("ERR AMR_BUSY");
    else {
      expectedStep = 0;
      resetWorkflow();
      pendingArrival = false;
      pendingArrivalLine[0] = '\0';
      sendAdminRaw("STATUS SEQUENCE_RESET");
    }
    return;
  }
  if (startsWithIgnoreCase(command, "RUN ")) {
    sendAdminRaw("STATUS RUN_IGNORED mode=AUTO_2_CYCLES");
    return;
  }
  sendAdminFormat("ERR UNKNOWN_COMMAND command=%s", command);
}

void finishActiveRoute() {
  char completedRoute[32];
  strncpy(completedRoute, activeRoute, sizeof(completedRoute) - 1);
  completedRoute[sizeof(completedRoute) - 1] = '\0';

  if (equalsIgnoreCase(completedRoute, "SAFE")) {
    clearActiveRoute();
    workflowState = WORKFLOW_IDLE;
    if (expectedStep == PROCESS_STEP_COUNT - 1) {
      ++completedCycles;
      expectedStep = 0;
    } else {
      ++expectedStep;
    }
    sendAdminFormat("EVENT SAFE_COMPLETE next_route=%s cycle=%u step=%u",
                    currentStationRoute(),
                    static_cast<unsigned int>(completedCycles + 1),
                    static_cast<unsigned int>(expectedStep + 1));
    beginRoute(currentStationRoute(), CONVEYOR_STOPPED);
    return;
  }

  if (workflowState != WORKFLOW_WAIT_ROUTE_FINISH) {
    failActiveRoute("STATION_ROUTE_FINISHED_BEFORE_TRANSFER_DONE");
    return;
  }
  sendAdminFormat(
      "EVENT STATION_STEP_COMPLETE station=%s cycle=%u step=%u route=%s",
      stationNameForStep(expectedStep),
      static_cast<unsigned int>(completedCycles + 1),
      static_cast<unsigned int>(expectedStep + 1), completedRoute);
  clearActiveRoute();
  workflowState = WORKFLOW_WAIT_ROUTE_FINISH;
  sendAdminFormat("STATUS AUTO_STEP_DONE cycle=%u step=%u route=%s",
                  static_cast<unsigned int>(completedCycles + 1),
                  static_cast<unsigned int>(expectedStep + 1), completedRoute);

  if (expectedStep == PROCESS_STEP_COUNT - 1 && completedCycles == 1) {
    sequenceStarted = false;
    workflowState = WORKFLOW_COMPLETE;
    completedCycles = 2;
    sendAdminRaw("STATUS AUTO_SEQUENCE_COMPLETE cycles=2 conveyor=STOP");
    sendAdminRaw("DONE PRODUCTION cycles=2 steps=12 final_station=5abb");
    return;
  }

  sendAdminRaw("STATUS NEXT_ROUTE=SAFE");
  beginRoute("SAFE", CONVEYOR_STOPPED);
}

void failActiveRoute(const char* reason) {
  stopConveyor();
  char failedRoute[32];
  strncpy(failedRoute, activeRoute, sizeof(failedRoute) - 1);
  failedRoute[sizeof(failedRoute) - 1] = '\0';
  if (arclClient.connected()) sendArclRaw("stop");
  clearActiveRoute();
  resetWorkflow();
  sendAdminFormat("ERR ROUTE_FAILED route=%s detail=%s", failedRoute, reason);
}

void handleArclLine(char* rawLine) {
  char* line = trimInPlace(rawLine);
  if (!*line) return;
  Serial.print("ARCL_RX ");
  Serial.println(line);
  if (!arclAuthenticated) {
    if (containsIgnoreCase(line, "invalid password") ||
        containsIgnoreCase(line, "login failed") ||
        containsIgnoreCase(line, "incorrect password")) {
      sendAdminRaw("ERR ARCL_AUTH_FAILED check=ARCL_PASSWORD");
      arclClient.stop();
      return;
    }
    if (equalsIgnoreCase(line, "End of commands")) {
      arclAuthenticated = true;
      arclReady = true;
      stopConveyor();
      sendArclRaw("echo off");
      sendArclRaw("enableMotors");
      faultCheckInProgress = true;
      diagnosticsRequestedAt = millis();
      sendArclRaw("faultsGet");
      sendArclRaw("queryMotors");
      sendAdminRaw("STATUS LD90_ARCL_ONLINE auth=OK checks=PENDING");
    }
    return;
  }
  if (startsWithIgnoreCase(line, "FaultList:")) {
    const char* detail = line + strlen("FaultList:");
    while (*detail == ' ' || *detail == '\t') ++detail;
    if (*detail != '\0' && !equalsIgnoreCase(detail, "none") &&
        !equalsIgnoreCase(detail, "0")) faultDetected = true;
  } else if (equalsIgnoreCase(line, "End of FaultList")) {
    faultCheckInProgress = false;
    faultCheckComplete = true;
    sendAdminRaw(faultDetected ? "STATUS LD90_FAULTS DETECTED"
                               : "STATUS LD90_FAULTS CLEAR");
  }
  if (containsIgnoreCase(line, "Motors enabled")) {
    motorsEnabled = true;
    motorsCheckComplete = true;
    sendAdminRaw("STATUS LD90_MOTORS ENABLED");
  } else if (containsIgnoreCase(line, "Motors disabled") ||
             containsIgnoreCase(line, "EStop pressed") ||
             containsIgnoreCase(line, "motors still disabled")) {
    motorsEnabled = false;
    motorsCheckComplete = true;
    if (routeRunning) failActiveRoute("MOTORS_OR_ESTOP_NOT_READY");
    sendAdminRaw("STATUS LD90_MOTORS NOT_READY");
  }
  // Prefer ARCLSendText DOCKED_READY immediately after PrecisionDrive.
  // Actual wait-state responses are accepted as compatible fallbacks.
  // Exact match prevents a route description such as
  // "ARCLSendText (DOCKED_READY)" from being mistaken for execution.
  bool dockedReadyReceived = equalsIgnoreCase(line, DOCKED_READY_MARKER);
  bool isWaitStateResponse = startsWithIgnoreCase(line, "WaitState:");
  if (routeRunning && waitCancelPending && isWaitStateResponse &&
      containsIgnoreCase(line, "WaitState: Waiting") &&
      !containsIgnoreCase(line, "cancelled") &&
      !containsIgnoreCase(line, "interrupted")) {
    waitCancelPending = false;
    sendAdminRaw("STATUS WAIT_CONFIRMED action=CANCEL_WAIT");
    sendArclRaw("waitTaskCancel");
  }
  if (routeRunning && workflowState == WORKFLOW_STATION_ROUTE &&
      !waitStateClearedForRoute &&
      isWaitStateResponse && containsIgnoreCase(line, "Not waiting")) {
    waitStateClearedForRoute = true;
    sendAdminRaw("STATUS WAITSTATE_ARMED state=NOT_WAITING");
  }
  // Require a fresh edge for every station route:
  //   Not waiting -> Waiting with status "Pausing"
  // This rejects the previous station's stale Pausing response.
  bool actualWaitEntered =
      waitStateClearedForRoute && isWaitStateResponse &&
      containsIgnoreCase(line, "WaitState: Waiting") &&
      (containsIgnoreCase(line, "status \"Pausing\"") ||
       containsIgnoreCase(line, "status \"Waiting\"")) &&
      !containsIgnoreCase(line, "cancelled") &&
      !containsIgnoreCase(line, "interrupted");
  if (routeRunning &&
      (dockedReadyReceived || actualWaitEntered)) {
    if (workflowState == WORKFLOW_STATION_ROUTE) startDockAction();
  }
  if (routeRunning && containsIgnoreCase(line, "Finished patrolling route") &&
      containsIgnoreCase(line, activeRoute)) {
    finishActiveRoute();
    return;
  }
  if (routeRunning && containsIgnoreCase(line, "Failed patrolling route") &&
      containsIgnoreCase(line, "patrolling again")) {
    sendAdminFormat(
        "EVENT ROUTE_RETRY station=%s cycle=%u step=%u route=%s detail=%s",
        stationNameForStep(expectedStep),
        static_cast<unsigned int>(completedCycles + 1),
        static_cast<unsigned int>(expectedStep + 1), activeRoute, line);
    return;
  }
  if (routeRunning && (containsIgnoreCase(line, "CommandError") ||
                       containsIgnoreCase(line, "Interrupted: Patrolling") ||
                       (containsIgnoreCase(line, "failed") &&
                        !containsIgnoreCase(line, "patrolling again")))) {
    failActiveRoute(line);
  }
}

void pollStationWaitState() {
  bool pollingForDock =
      workflowState == WORKFLOW_STATION_ROUTE && !dockWaitObserved;
  bool pollingForCancel =
      workflowState == WORKFLOW_WAIT_ROUTE_FINISH && waitCancelPending;
  if (!routeRunning || (!pollingForDock && !pollingForCancel) ||
      !arclAuthenticated || !arclClient.connected()) return;

  unsigned long now = millis();
  if (now - routeStartedAt < WAIT_STATE_FIRST_POLL_DELAY_MS) return;
  if (lastWaitStatePollAt != 0 &&
      now - lastWaitStatePollAt < WAIT_STATE_POLL_MS) return;

  lastWaitStatePollAt = now;
  sendArclRaw("waitTaskState");
}

void readAdminLines() {
  while (adminClient.connected() && adminClient.available()) {
    int value = adminClient.read();
    if (value < 0) break;
    char c = static_cast<char>(value);
    if (c == '\n') {
      adminLine[adminLineLength] = '\0';
      handleAdminCommand(adminLine);
      adminLineLength = 0;
    } else if (c != '\r') {
      if (adminLineLength < sizeof(adminLine) - 1) adminLine[adminLineLength++] = c;
      else { adminLineLength = 0; sendAdminRaw("ERR COMMAND_TOO_LONG"); }
    }
  }
}

void readArclLines() {
  while (arclClient.connected() && arclClient.available()) {
    int value = arclClient.read();
    if (value < 0) break;
    char c = static_cast<char>(value);
    if (c == '\n') {
      arclLine[arclLineLength] = '\0';
      handleArclLine(arclLine);
      arclLineLength = 0;
    } else if (c != '\r') {
      if (arclLineLength < sizeof(arclLine) - 1) arclLine[arclLineLength++] = c;
      else { arclLineLength = 0; Serial.println("ARCL_RX_LINE_TOO_LONG"); }
    }
  }
}

void monitorConnections() {
  if (adminWasConnected && !adminClient.connected()) {
    Serial.println("ADMIN_DISCONNECTED safety_stop=1 rediscover=1");
    invalidateAdminServer(true);
  }
  if (!arclClient.connected()) {
    arclLineLength = 0;
    arclReady = false;
    arclAuthenticated = false;
    motorsCheckComplete = false;
    faultCheckComplete = false;
    pendingRunRequested = false;
    if (routeRunning) failActiveRoute("ARCL_DISCONNECTED");
  }
}

void monitorObjectSensor() {
  bool rawNow = digitalRead(OBJECT_SENSOR_PIN) == LOW;
  unsigned long now = millis();
  if (rawNow != rawObjectDetected) {
    rawObjectDetected = rawNow;
    lastSensorChangeAt = now;
    return;
  }
  if (rawObjectDetected == lastObjectDetected ||
      now - lastSensorChangeAt < SENSOR_DEBOUNCE_MS) return;
  lastObjectDetected = rawObjectDetected;
  sendAdminRaw(lastObjectDetected ? "STATUS OBJECT_DETECTED pin=D2 level=LOW"
                                  : "STATUS OBJECT_CLEARED pin=D2 level=HIGH");
  if (workflowState == WORKFLOW_LOADING_TO_D2) {
    if (!lastObjectDetected) {
      sensorArmedForLoad = true;
      sendAdminRaw("STATUS D2_ARMED waiting=NEXT_DETECTION");
    } else if (sensorArmedForLoad) {
      finishDockTransfer();
    }
  }
}

void enforceTimeouts() {
  unsigned long now = millis();
  StationAction currentAction = PROCESS_SEQUENCE[expectedStep].action;
  unsigned long reverseRunMs =
      currentAction == ACTION_ST2_UNLOAD_WAIT_RELOAD
          ? ST2_DELIVERY_REV_RUN_MS
          : RETURN_REV_RUN_MS;
  if (workflowState == WORKFLOW_UNLOADING_TIMED && conveyorRunning &&
      now - conveyorStartedAt >= reverseRunMs) {
    stopConveyor();
    if (currentAction == ACTION_ST2_UNLOAD_WAIT_RELOAD) {
      workflowState = WORKFLOW_ST2_WAIT_10S;
      conveyorStartedAt = now;
      sendAdminRaw("STATUS CONVEYOR_STOP reason=REV_TIMER_6S next=WAIT_10S");
    } else {
      sendAdminRaw("STATUS CONVEYOR_STOP reason=REV_TIMER_6S next=CONFIRM_AND_CANCEL_WAIT");
      finishDockTransfer();
    }
  }

  if (workflowState == WORKFLOW_ST2_WAIT_10S &&
      now - conveyorStartedAt >= ST2_CHANGEOVER_WAIT_MS) {
    sendAdminRaw("STATUS ST2_WAIT_FINISHED next=FWD_UNTIL_NEW_D2");
    // The old plate must clear D2 (HIGH) before a new LOW is accepted.
    // SAFE is requested only after monitorObjectSensor() sees that new LOW.
    startLoadUntilD2(true);
  }

  if (workflowState == WORKFLOW_FORWARD_TIMED && conveyorRunning) {
    unsigned long forwardRunMs = ST3_LOAD_FWD_RUN_MS;
    if (now - conveyorStartedAt >= forwardRunMs) {
      stopConveyor();
      sendAdminFormat("STATUS CONVEYOR_STOP reason=FWD_TIMER timer_ms=%lu next=CANCEL_WAIT",
                      forwardRunMs);
      finishDockTransfer();
    }
  } else if (workflowState == WORKFLOW_UNLOADING_TO_D2_CLEAR) {
    if (lastObjectDetected) {
      sensorArmedForUnload = true;
    } else if (sensorArmedForUnload) {
      finishDockTransfer();
    }
  }

  bool stationIsIntentionallyWaiting =
      routeRunning && dockWaitObserved && workflowState != WORKFLOW_STATION_ROUTE;
  if (routeRunning && !stationIsIntentionallyWaiting &&
      now - routeStartedAt >= ROUTE_TIMEOUT_MS) {
    if (arclClient.connected()) sendArclRaw("stop");
    failActiveRoute("ROUTE_TIMEOUT_10MIN");
  }
  if (faultCheckInProgress &&
      now - diagnosticsRequestedAt >= DIAGNOSTIC_TIMEOUT_MS) {
    faultCheckInProgress = false;
    faultCheckComplete = false;
    sendAdminRaw("ERR DIAGNOSTIC_TIMEOUT command=faultsGet_or_queryMotors");
  }
}

void setup() {
  // Establish the safe motor state before starting networking or ARCL.
  digitalWrite(CONVEYOR_FWD_PIN, LOW);
  digitalWrite(CONVEYOR_REV_PIN, LOW);
  pinMode(CONVEYOR_FWD_PIN, OUTPUT);
  pinMode(CONVEYOR_REV_PIN, OUTPUT);
  digitalWrite(CONVEYOR_FWD_PIN, LOW);
  digitalWrite(CONVEYOR_REV_PIN, LOW);
  pinMode(OBJECT_SENSOR_PIN, INPUT_PULLUP);
  Serial.begin(115200);
  delay(1000);
  Serial.print("FIRMWARE ");
  Serial.println(FIRMWARE_VERSION);
  Serial.println("COMMAND START=AUTO_RUN_2_CYCLES");
  Serial.println("FLOW 1LOAD 2UNLOAD_RELOAD 1UNLOAD 3LOAD 2UNLOAD_RELOAD 3UNLOAD");
  Serial.println("CONVEYOR ARDUINO_PINS FWD=D10_HIGH REV=D11_HIGH STOP=BOTH_LOW");
  Serial.println("ROUTES first=START then SAFE_between_all station_routes repeat=2");
  rawObjectDetected = digitalRead(OBJECT_SENSOR_PIN) == LOW;
  lastObjectDetected = rawObjectDetected;
  lastSensorChangeAt = millis();
  WiFi.begin(WIFI_SSID);
  lastWiFiAttemptAt = millis();
  lastDiscoveryAt = millis() - DISCOVERY_RETRY_MS;
  lastAdminAttemptAt = millis() - ADMIN_RETRY_MS;
  lastArclAttemptAt = millis() - ARCL_RETRY_MS;
}

void loop() {
  manageWiFi();
  discoverAdminIfNeeded();
  readDiscoveryResponses();
  connectAdminIfNeeded();
  connectArclIfNeeded();
  monitorArclLogin();
  readAdminLines();
  readArclLines();
  // Polling supplies the safe WaitState fallback if DOCKED_READY is disabled.
  pollStationWaitState();
  retryPendingRunIfReady();
  monitorConnections();
  monitorObjectSensor();
  enforceTimeouts();
  if (adminClient.connected() && millis() - lastHeartbeatAt >= HEARTBEAT_MS) {
    lastHeartbeatAt = millis();
    sendStatus();
  }
}
