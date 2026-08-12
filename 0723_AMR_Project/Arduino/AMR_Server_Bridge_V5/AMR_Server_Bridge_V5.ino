#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <ctype.h>
#include <stdarg.h>
#include <string.h>

/*
  Arduino UNO R4 WiFi - AMR bridge V5

  Merge of two independently-written versions (V3, close to the AMR owner's
  original sketch; V4, a more elaborate rewrite) plus one real-world fix:

  Existing main server <-> Arduino <-> Omron LD-90 ARCL

  Main-server registration:
    The Arduino sends "amr" as the first TCP line.

  Six-step sequence (repeats after step 6, so the server can run it twice):
    1. ROUTE_ST1 FWD
    2. ROUTE_ST2 REV
    3. ROUTE_ST1 REV
    4. ROUTE_ST3 FWD
    5. ROUTE_ST2 REV
    6. ROUTE_ST3 REV

  Conveyor:
    D10 HIGH / D11 LOW = FWD
    D10 LOW  / D11 HIGH = REV
    both LOW             = STOP

  Object sensor:
    D2 HIGH = no object
    D2 LOW  = object detected

  What changed in V5 and why:
    - WiFi password fixed to "" (open network). V3 had a password ("azureuser")
      that turned out to be wrong for the real network; V4 had already guessed
      it was open and was right. ROBOT_MA2_2G is confirmed password-free.
    - FaultList parsing (from V4): only treat it as a real fault if there is
      actual content after "FaultList:" (not empty/"none"/"0"). V3's version
      set faultDetected=true on ANY "FaultList:" line, which would have
      permanently blocked all movement if LD-90 sends an empty header when
      there are no faults.
    - pendingArrival replay (from V4): if the "arrived ..." message can't be
      sent because the admin TCP link just dropped, it is remembered and
      replayed automatically right after the admin connection is re-established,
      instead of being lost forever.
    - pendingRun retry (from V3): if a RUN command arrives while the ARCL
      safety checks are still pending, it is remembered and replayed
      automatically once those checks complete, instead of being dropped.
      (V4 did not have this one - routeAllowed() there just drops a rejected
      RUN with no retry.)
    - Object sensor debounce (from V4, 50 ms) to ignore electrical bounce.
    - ARCL login is confirmed by waiting for "End of commands" (from V4,
      the documented end-of-banner marker) instead of V3's looser "no error
      seen within 1.5s" heuristic, with a bounded ARCL_LOGIN_TIMEOUT_MS so a
      wrong password/no response doesn't hang forever.
    - Bounded timeout on the initial fault/motor diagnostic request (from V4)
      so a non-responding LD-90 doesn't leave the checks pending forever.
    - V4's stricter WaitState/object-sensor "must actually see it before
      calling a route done" gates were intentionally NOT carried over - they
      are unverified against the real LD-90/conveyor behavior and could cause
      false ROUTE_ABORTED on a route that in fact completed fine. Revisit once
      tested on real hardware.
*/

// ---------- Network ----------
const char WIFI_SSID[] = "ROBOT_MA2_2G";
const char WIFI_PASSWORD[] = "";  // confirmed: open network, no password

const uint16_t ADMIN_SERVER_PORT = 5000;
const uint16_t DISCOVERY_SERVER_PORT = 5001;
const uint16_t DISCOVERY_LOCAL_PORT = 5002;
const char DISCOVERY_REQUEST[] = "AMR_SERVER_DISCOVER_V1 device=amr";
const char DISCOVERY_RESPONSE[] = "AMR_SERVER_V1 name=admin tcp_port=5000";

IPAddress LD90_IP(192, 168, 0, 10);
const uint16_t LD90_ARCL_PORT = 7171;
const char ARCL_PASSWORD[] = "adept";

const char FIRMWARE_VERSION[] = "AMR_Server_Bridge_V5";

// ---------- I/O ----------
const uint8_t OBJECT_SENSOR_PIN = 2;
const uint8_t CONVEYOR_FWD_PIN = 10;
const uint8_t CONVEYOR_REV_PIN = 11;

// ---------- Timings ----------
const unsigned long CONVEYOR_RUN_MS = 5000UL;
const unsigned long ROUTE_TIMEOUT_MS = 10UL * 60UL * 1000UL;
const unsigned long HEARTBEAT_MS = 5000UL;
const unsigned long WIFI_RETRY_MS = 5000UL;
const unsigned long DISCOVERY_RETRY_MS = 3000UL;
const unsigned long ADMIN_RETRY_MS = 3000UL;
const unsigned long ARCL_RETRY_MS = 3000UL;
const unsigned long ARCL_LOGIN_TIMEOUT_MS = 10000UL;
const unsigned long DIAGNOSTIC_TIMEOUT_MS = 10000UL;
const unsigned long SENSOR_DEBOUNCE_MS = 50UL;

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

struct ProcessStep {
  const char* route;
  ConveyorDirection direction;
};

const ProcessStep PROCESS_SEQUENCE[] = {
  {"ROUTE_ST1", CONVEYOR_FWD},
  {"ROUTE_ST2", CONVEYOR_REV},
  {"ROUTE_ST1", CONVEYOR_REV},
  {"ROUTE_ST3", CONVEYOR_FWD},
  {"ROUTE_ST2", CONVEYOR_REV},
  {"ROUTE_ST3", CONVEYOR_REV},
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

uint8_t expectedStep = 0;
char activeRoute[32] = "";
ConveyorDirection activeDirection = CONVEYOR_STOPPED;

// A RUN request deferred because the ARCL safety checks were still pending.
bool pendingRunRequested = false;
char pendingRunRoute[32] = "";
ConveyorDirection pendingRunDirection = CONVEYOR_STOPPED;

// An "arrived" message that couldn't be sent because the admin link had just
// dropped. Replayed automatically once the admin connection comes back.
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

ConveyorDirection parseDirection(const char* value) {
  if (equalsIgnoreCase(value, "FWD")) return CONVEYOR_FWD;
  if (equalsIgnoreCase(value, "REV")) return CONVEYOR_REV;
  return CONVEYOR_STOPPED;
}

void printIPAddress(const IPAddress& ip) {
  Serial.print(ip[0]);
  Serial.print('.');
  Serial.print(ip[1]);
  Serial.print('.');
  Serial.print(ip[2]);
  Serial.print('.');
  Serial.print(ip[3]);
}

void stopConveyor() {
  digitalWrite(CONVEYOR_FWD_PIN, LOW);
  digitalWrite(CONVEYOR_REV_PIN, LOW);
  conveyorRunning = false;
}

void startConveyor(ConveyorDirection direction) {
  stopConveyor();
  delay(20);  // Mechanical interlock: never switch FWD/REV directly.

  if (direction == CONVEYOR_FWD) {
    digitalWrite(CONVEYOR_FWD_PIN, HIGH);
    digitalWrite(CONVEYOR_REV_PIN, LOW);
  } else if (direction == CONVEYOR_REV) {
    digitalWrite(CONVEYOR_FWD_PIN, LOW);
    digitalWrite(CONVEYOR_REV_PIN, HIGH);
  } else {
    return;
  }

  conveyorRunning = true;
  conveyorStartedAt = millis();
}

bool sendAdminRaw(const char* message) {
  Serial.println(message);
  if (!adminClient.connected()) return false;
  size_t written = adminClient.println(message);
  return written > 0;
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

void safetyStopForServerLoss() {
  stopConveyor();
  if (arclClient.connected()) sendArclRaw("stop");
  clearActiveRoute();
}

void invalidateAdminServer(bool stopForSafety) {
  if (stopForSafety) safetyStopForServerLoss();
  adminClient.stop();
  adminWasConnected = false;
  adminServerKnown = false;
  discoveredAdminIP = IPAddress(0, 0, 0, 0);
  adminLineLength = 0;
  adminLine[0] = '\0';
  pendingRunRequested = false;  // don't fire a stale retry into a new admin session
  lastDiscoveryAt = millis() - DISCOVERY_RETRY_MS;
}

bool sameSubnet(const IPAddress& a, const IPAddress& b,
                const IPAddress& mask) {
  for (uint8_t i = 0; i < 4; ++i) {
    if ((a[i] & mask[i]) != (b[i] & mask[i])) return false;
  }
  return true;
}

IPAddress calculateBroadcast(const IPAddress& local,
                             const IPAddress& mask) {
  return IPAddress(
      static_cast<uint8_t>(local[0] | static_cast<uint8_t>(~mask[0])),
      static_cast<uint8_t>(local[1] | static_cast<uint8_t>(~mask[1])),
      static_cast<uint8_t>(local[2] | static_cast<uint8_t>(~mask[2])),
      static_cast<uint8_t>(local[3] | static_cast<uint8_t>(~mask[3])));
}

void startDiscoveryUdp() {
  if (discoveryUdpStarted) discoveryUdp.stop();
  discoveryUdpStarted = discoveryUdp.begin(DISCOVERY_LOCAL_PORT) == 1;
  if (!discoveryUdpStarted) {
    Serial.println("DISCOVERY_UDP_START_FAILED port=5002");
  }
}

void sendDiscoveryPacket(const IPAddress& destination) {
  if (!discoveryUdp.beginPacket(destination, DISCOVERY_SERVER_PORT)) return;
  discoveryUdp.write(reinterpret_cast<const uint8_t*>(DISCOVERY_REQUEST),
                     strlen(DISCOVERY_REQUEST));
  discoveryUdp.endPacket();
}

void discoverAdminIfNeeded() {
  if (WiFi.status() != WL_CONNECTED || adminServerKnown ||
      adminClient.connected()) return;
  if (!discoveryUdpStarted) startDiscoveryUdp();
  if (!discoveryUdpStarted) return;
  if (millis() - lastDiscoveryAt < DISCOVERY_RETRY_MS) return;

  lastDiscoveryAt = millis();
  IPAddress local = WiFi.localIP();
  IPAddress mask = WiFi.subnetMask();
  IPAddress broadcast = calculateBroadcast(local, mask);

  sendDiscoveryPacket(broadcast);
  if (!(broadcast == IPAddress(255, 255, 255, 255))) {
    sendDiscoveryPacket(IPAddress(255, 255, 255, 255));
  }
  Serial.println("DISCOVERY_TX port=5001");
}

void readDiscoveryResponses() {
  if (!discoveryUdpStarted || adminServerKnown ||
      WiFi.status() != WL_CONNECTED) return;

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
           (discoveryBuffer[stored - 1] == '\r' ||
            discoveryBuffer[stored - 1] == '\n')) {
      discoveryBuffer[--stored] = '\0';
    }

    IPAddress local = WiFi.localIP();
    IPAddress mask = WiFi.subnetMask();
    bool exactResponse = strcmp(discoveryBuffer, DISCOVERY_RESPONSE) == 0;
    bool localNetwork = sameSubnet(local, remote, mask);

    if (exactResponse && localNetwork) {
      discoveredAdminIP = remote;  // Trust the actual UDP sender address.
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
    pendingRunRequested = false;  // a route can't be resumed across a WiFi drop
  }

  if (connected) return;
  if (millis() - lastWiFiAttemptAt < WIFI_RETRY_MS) return;

  lastWiFiAttemptAt = millis();
  stopConveyor();
  Serial.print("WIFI_CONNECTING ssid=");
  Serial.print(WIFI_SSID);
  Serial.println(WIFI_PASSWORD[0] == '\0' ? " security=OPEN" : " security=WPA");

  if (WIFI_PASSWORD[0] == '\0') {
    WiFi.begin(WIFI_SSID);
  } else {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  }
}

void connectAdminIfNeeded() {
  if (WiFi.status() != WL_CONNECTED || !adminServerKnown ||
      adminClient.connected()) return;
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

  // Replay an "arrived" message that got stranded by the disconnect instead
  // of being lost - the server would otherwise wait for it forever.
  if (pendingArrival) {
    if (sendAdminRaw(pendingArrivalLine)) {
      Serial.print("ADMIN_REPLAY ");
      Serial.println(pendingArrivalLine);
      pendingArrival = false;
    }
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
  pendingRunRequested = false;  // re-check from scratch on a fresh ARCL session
  arclClient.stop();
  Serial.println("ARCL_CONNECTING 192.168.0.10:7171");

  if (!arclClient.connect(LD90_IP, LD90_ARCL_PORT)) return;

  arclConnectedAt = millis();
  arclClient.println(ARCL_PASSWORD);
  sendAdminRaw("STATUS LD90_TCP_CONNECTED ARCL=AUTHENTICATING");
  // Login result (success = "End of commands", failure = an explicit error
  // line, or ARCL_LOGIN_TIMEOUT_MS with neither) is handled as lines arrive
  // in handleArclLine()/monitorArclLogin(), not blocking here.
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
      "STATUS step=%u routeRunning=%u object=%s arcl=%s motors=%s faults=%s",
      static_cast<unsigned int>(expectedStep + 1),
      routeRunning ? 1U : 0U,
      lastObjectDetected ? "DETECTED" : "CLEAR",
      arclReady && arclClient.connected() ? "ONLINE" : "OFFLINE",
      motorsCheckComplete ? (motorsEnabled ? "ENABLED" : "NOT_READY") : "PENDING",
      faultCheckComplete ? (faultDetected ? "DETECTED" : "CLEAR") : "PENDING");
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
    // Remember this request instead of dropping it - retryPendingRunIfReady()
    // replays it automatically once the checks below finish.
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
  if (!motorsEnabled) {
    sendAdminRaw("ERR LD90_MOTORS_NOT_ENABLED");
    return;
  }
  if (faultDetected) {
    sendAdminRaw("ERR LD90_FAULT_PRESENT");
    return;
  }
  if (direction == CONVEYOR_STOPPED) {
    sendAdminRaw("ERR INVALID_DIRECTION");
    return;
  }

  const ProcessStep& expected = PROCESS_SEQUENCE[expectedStep];
  if (!equalsIgnoreCase(route, expected.route) ||
      direction != expected.direction) {
    sendAdminFormat("ERR SEQUENCE_MISMATCH expected=%s_%s received=%s_%s",
                    expected.route, directionName(expected.direction), route,
                    directionName(direction));
    return;
  }

  routeRunning = true;
  conveyorStartedForRoute = false;
  strncpy(activeRoute, route, sizeof(activeRoute) - 1);
  activeRoute[sizeof(activeRoute) - 1] = '\0';
  activeDirection = direction;
  routeStartedAt = millis();

  sendAdminFormat("STATUS ROUTE_START step=%u route=%s direction=%s",
                  static_cast<unsigned int>(expectedStep + 1), activeRoute,
                  directionName(activeDirection));
  sendArclFormat("patrolOnce %s", activeRoute);
}

// Replays a RUN request that beginRoute() had to defer because the ARCL
// fault/motor checks were still pending. Without this, that single request
// would just be lost - the central server only waits for "arrived" with no
// timeout, so a dropped RUN silently freezes automatic production.
void retryPendingRunIfReady() {
  if (!pendingRunRequested) return;
  if (!motorsCheckComplete || !faultCheckComplete) return;

  pendingRunRequested = false;
  char route[32];
  strncpy(route, pendingRunRoute, sizeof(route) - 1);
  route[sizeof(route) - 1] = '\0';
  ConveyorDirection direction = pendingRunDirection;

  sendAdminRaw("STATUS RUN_RETRY_AFTER_SAFETY_CHECK");
  beginRoute(route, direction);
}

void handleAdminCommand(char* rawCommand) {
  char* command = trimInPlace(rawCommand);
  if (!*command) return;

  if (equalsIgnoreCase(command, "STOP") ||
      equalsIgnoreCase(command, "ESTOP")) {
    stopConveyor();
    if (arclClient.connected()) sendArclRaw("stop");
    clearActiveRoute();
    pendingRunRequested = false;  // an explicit stop cancels any deferred RUN too
    sendAdminRaw("STATUS STOPPED");
    return;
  }

  if (equalsIgnoreCase(command, "STATUS")) {
    sendStatus();
    return;
  }

  if (equalsIgnoreCase(command, "RESET_SEQUENCE")) {
    if (routeRunning) {
      sendAdminRaw("ERR AMR_BUSY");
    } else {
      expectedStep = 0;
      pendingArrival = false;
      pendingArrivalLine[0] = '\0';
      sendAdminRaw("STATUS SEQUENCE_RESET");
    }
    return;
  }

  if (startsWithIgnoreCase(command, "RUN ")) {
    char route[32];
    char directionText[8];
    char extra[2];
    int parsed = sscanf(command, "%*s %31s %7s %1s", route, directionText, extra);
    if (parsed != 2) {
      sendAdminRaw("ERR COMMAND_FORMAT use=RUN_ROUTE_DIRECTION");
      return;
    }
    beginRoute(route, parseDirection(directionText));
    return;
  }

  sendAdminFormat("ERR UNKNOWN_COMMAND command=%s", command);
}

void finishActiveRoute() {
  char completedRoute[32];
  strncpy(completedRoute, activeRoute, sizeof(completedRoute) - 1);
  completedRoute[sizeof(completedRoute) - 1] = '\0';
  uint8_t completedStep = expectedStep + 1;

  stopConveyor();
  clearActiveRoute();
  expectedStep = (expectedStep + 1) % PROCESS_STEP_COUNT;

  char line[64];
  snprintf(line, sizeof(line), "arrived route=%s step=%u", completedRoute,
           static_cast<unsigned int>(completedStep));

  // Main server releases the next leg when this line contains "arrived".
  // If it can't be sent right now (admin link just dropped), remember it and
  // replay it as soon as the admin connection comes back - otherwise the
  // server would wait for "arrived" forever with no way to recover.
  if (sendAdminRaw(line)) {
    pendingArrival = false;
  } else {
    strncpy(pendingArrivalLine, line, sizeof(pendingArrivalLine) - 1);
    pendingArrivalLine[sizeof(pendingArrivalLine) - 1] = '\0';
    pendingArrival = true;
  }
}

void failActiveRoute(const char* reason) {
  stopConveyor();
  char failedRoute[32];
  strncpy(failedRoute, activeRoute, sizeof(failedRoute) - 1);
  failedRoute[sizeof(failedRoute) - 1] = '\0';
  clearActiveRoute();
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
    // Documented end-of-login-banner marker - more specific than "no error
    // seen yet", so a slow or partial response can't be mistaken for success.
    if (equalsIgnoreCase(line, "End of commands")) {
      arclAuthenticated = true;
      arclReady = true;
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

  // Only real content after "FaultList:" means an actual fault - an empty
  // (or "none"/"0") header is what LD-90 sends when there is nothing wrong.
  if (startsWithIgnoreCase(line, "FaultList:")) {
    const char* detail = line + strlen("FaultList:");
    while (*detail == ' ' || *detail == '\t') ++detail;
    if (*detail != '\0' && !equalsIgnoreCase(detail, "none") &&
        !equalsIgnoreCase(detail, "0")) {
      faultDetected = true;
    }
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

  if (routeRunning && !conveyorStartedForRoute &&
      containsIgnoreCase(line, "WaitState: Waiting") &&
      !containsIgnoreCase(line, "completed")) {
    conveyorStartedForRoute = true;
    startConveyor(activeDirection);
    sendAdminFormat("STATUS CONVEYOR_START direction=%s",
                    directionName(activeDirection));
  }

  if (routeRunning &&
      containsIgnoreCase(line, "Finished patrolling route") &&
      containsIgnoreCase(line, activeRoute)) {
    finishActiveRoute();
    return;
  }

  if (routeRunning &&
      (containsIgnoreCase(line, "CommandError") ||
       containsIgnoreCase(line, "Interrupted: Patrolling") ||
       containsIgnoreCase(line, "failed"))) {
    failActiveRoute(line);
  }
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
      if (adminLineLength < sizeof(adminLine) - 1) {
        adminLine[adminLineLength++] = c;
      } else {
        adminLineLength = 0;
        sendAdminRaw("ERR COMMAND_TOO_LONG");
      }
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
      if (arclLineLength < sizeof(arclLine) - 1) {
        arclLine[arclLineLength++] = c;
      } else {
        arclLineLength = 0;
        Serial.println("ARCL_RX_LINE_TOO_LONG");
      }
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
    pendingRunRequested = false;  // no ARCL session to run it on anymore
    if (routeRunning) failActiveRoute("ARCL_DISCONNECTED");
  }
}

void monitorObjectSensor() {
  bool rawNow = digitalRead(OBJECT_SENSOR_PIN) == LOW;
  unsigned long now = millis();

  if (rawNow != rawObjectDetected) {
    rawObjectDetected = rawNow;
    lastSensorChangeAt = now;
    return;  // wait for the debounce window before trusting this transition
  }
  if (rawObjectDetected == lastObjectDetected) return;
  if (now - lastSensorChangeAt < SENSOR_DEBOUNCE_MS) return;

  lastObjectDetected = rawObjectDetected;
  sendAdminRaw(lastObjectDetected ? "STATUS OBJECT_DETECTED pin=D2 level=LOW"
                                  : "STATUS OBJECT_CLEARED pin=D2 level=HIGH");
}

void enforceTimeouts() {
  if (conveyorRunning && millis() - conveyorStartedAt >= CONVEYOR_RUN_MS) {
    stopConveyor();
    sendAdminRaw("STATUS CONVEYOR_STOP reason=TIMER_5S");
  }

  if (routeRunning && millis() - routeStartedAt >= ROUTE_TIMEOUT_MS) {
    if (arclClient.connected()) sendArclRaw("stop");
    failActiveRoute("ROUTE_TIMEOUT_10MIN");
  }

  if (faultCheckInProgress &&
      millis() - diagnosticsRequestedAt >= DIAGNOSTIC_TIMEOUT_MS) {
    faultCheckInProgress = false;
    faultCheckComplete = false;
    sendAdminRaw("ERR DIAGNOSTIC_TIMEOUT command=faultsGet_or_queryMotors");
  }
}

void setup() {
  pinMode(OBJECT_SENSOR_PIN, INPUT_PULLUP);
  pinMode(CONVEYOR_FWD_PIN, OUTPUT);
  pinMode(CONVEYOR_REV_PIN, OUTPUT);
  stopConveyor();

  Serial.begin(115200);
  delay(1000);
  Serial.print("FIRMWARE ");
  Serial.println(FIRMWARE_VERSION);
  Serial.println("SEQUENCE 1FWD 2REV 1REV 3FWD 2REV 3REV repeat=SUPPORTED");

  rawObjectDetected = digitalRead(OBJECT_SENSOR_PIN) == LOW;
  lastObjectDetected = rawObjectDetected;
  lastSensorChangeAt = millis();

  WiFi.begin(WIFI_SSID);  // open network, no password
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
  retryPendingRunIfReady();
  monitorConnections();
  monitorObjectSensor();
  enforceTimeouts();

  if (adminClient.connected() && millis() - lastHeartbeatAt >= HEARTBEAT_MS) {
    lastHeartbeatAt = millis();
    sendStatus();
  }
}
