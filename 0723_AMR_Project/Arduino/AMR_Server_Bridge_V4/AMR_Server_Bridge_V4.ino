#include <WiFiS3.h>
#include <WiFiUdp.h>

#include <ctype.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

/*
  AMR_Server_Bridge_V4

  Arduino UNO R4 WiFi bridge for the current AMR integration package:

              Server_admin_Web_ver02.py
             UDP 5001 / TCP 5000
                     |
              Arduino UNO R4 WiFi
                     |
              LD-90 direct ARCL TCP 7171

  Server commands:
    RUN ROUTE_ST1 FWD
    RUN ROUTE_ST2 REV
    RUN ROUTE_ST1 REV
    RUN ROUTE_ST3 FWD
    RUN ROUTE_ST2 REV
    RUN ROUTE_ST3 REV
    RESET_SEQUENCE
    PREPARE
    ARM
    DISARM
    STOP
    STATUS

  Conveyor I/O:
    D10 HIGH / D11 LOW = FWD
    D10 LOW  / D11 HIGH = REV
    D10 LOW  / D11 LOW = STOP

  Object sensor:
    D2 LOW  = object detected
    D2 HIGH = clear

  Safety notes:
    - D10/D11 are control signals only. Use electrically isolated PLC/relay or
      motor-driver inputs. Never power a motor from an Arduino pin.
    - The LD-90 safety system and physical E-stop remain authoritative.
    - Verify the route names, ARCL password, I/O polarity, and conveyor
      direction with the AMR owner before a movement test.
*/

// ============================================================================
// Site settings
// ============================================================================

const char WIFI_SSID[] = "ROBOT_MA2_2G";
// ROBOT_MA2_2G is currently an open network. If security is later enabled,
// enter the password here; the connection code automatically changes mode.
const char WIFI_PASSWORD[] = "";

const uint16_t ADMIN_SERVER_PORT = 5000;
const uint16_t DISCOVERY_SERVER_PORT = 5001;
const uint16_t DISCOVERY_LOCAL_PORT = 5002;
const char ADMIN_CLIENT_NAME[] = "amr";
const char DISCOVERY_REQUEST[] = "AMR_SERVER_DISCOVER_V1 device=amr";
const char DISCOVERY_RESPONSE[] = "AMR_SERVER_V1 name=admin tcp_port=5000";

IPAddress LD90_IP(192, 168, 0, 10);
const uint16_t LD90_ARCL_PORT = 7171;
// Latest AMR-owner package value. Change only if MobilePlanner's ARCL Server
// Setup shows a different password.
const char ARCL_PASSWORD[] = "adept";

const char FIRMWARE_VERSION[] = "2026-08-06-amr-server-bridge-v4";

// true keeps the received package's automatic-operation behavior, but this
// version waits for successful authentication and a fault scan before sending
// enableMotors. RUN is still rejected until queryMotors confirms enabled.
// Set false if the operator must send ARM manually for every power-up.
const bool AUTO_ENABLE_MOTORS = true;

// All supplied routes are expected to contain one WaitState for transfer.
const bool REQUIRE_WAITSTATE_FOR_ARRIVAL = true;

// The sensor is used immediately for early conveyor stop on a valid transition.
// Keep false until D2 polarity and the physical detection point are verified.
// When true, a route cannot report "arrived" without a matching sensor change.
const bool REQUIRE_OBJECT_SENSOR_CONFIRMATION = false;

const bool STOP_AMR_ON_ADMIN_LOSS = true;

// ============================================================================
// I/O and timing
// ============================================================================

const uint8_t OBJECT_SENSOR_PIN = 2;
const uint8_t CONVEYOR_FWD_PIN = 10;
const uint8_t CONVEYOR_REV_PIN = 11;

const uint8_t OBJECT_DETECTED_LEVEL = LOW;
const uint8_t CONVEYOR_ACTIVE_LEVEL = HIGH;
const uint8_t CONVEYOR_INACTIVE_LEVEL = LOW;

const unsigned long SENSOR_DEBOUNCE_MS = 50;
const unsigned long CONVEYOR_DIRECTION_DEADTIME_MS = 100;
const unsigned long CONVEYOR_MAX_RUN_MS = 5000;
const unsigned long WIFI_RETRY_MS = 10000;
const unsigned long WIFI_CHECK_MS = 1000;
const unsigned long DISCOVERY_RETRY_MS = 3000;
const unsigned long ADMIN_RETRY_MS = 3000;
const unsigned long LD90_RETRY_MS = 5000;
const unsigned long ARCL_LOGIN_TIMEOUT_MS = 10000;
const unsigned long DIAGNOSTIC_TIMEOUT_MS = 10000;
// The AMR owner's latest sketch allowed long routes up to 10 minutes.
const unsigned long MOTION_TIMEOUT_MS = 10UL * 60UL * 1000UL;
const unsigned long HEARTBEAT_MS = 5000;
const unsigned long LD90_STATUS_QUERY_MS = 15000;
const int TCP_CONNECTION_TIMEOUT_MS = 1500;

// ============================================================================
// Production sequence
// ============================================================================

enum ConveyorDirection : uint8_t {
  CONVEYOR_STOPPED,
  CONVEYOR_FWD,
  CONVEYOR_REV
};

struct ProcessStep {
  const char *route;
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

// ============================================================================
// Network and process state
// ============================================================================

WiFiClient adminClient;
WiFiClient arclClient;
WiFiUDP discoveryUdp;

IPAddress discoveredAdminIP(0, 0, 0, 0);
bool adminServerKnown = false;
bool discoveryUdpStarted = false;

bool wifiOnline = false;
bool adminOnline = false;
bool adminSendFailed = false;
bool ld90TcpOnline = false;
bool arclAuthenticated = false;

bool motorsConfirmed = false;
bool faultScanActive = false;
bool faultScanComplete = false;
bool faultDetected = false;
bool diagnosticTimeoutReported = false;
bool motorEnableRequested = false;

bool routeRunning = false;
bool waitActive = false;
bool waitSeenForRoute = false;
bool conveyorRunning = false;
bool conveyorStartedForRoute = false;
bool transferConfirmed = false;
bool sensorChangedDuringTransfer = false;

bool sensorRawDetected = false;
bool sensorStableDetected = false;
bool sensorStateAtConveyorStart = false;

uint8_t expectedStep = 0;
ConveyorDirection activeDirection = CONVEYOR_STOPPED;
char activeRoute[48] = "NONE";

bool pendingArrival = false;
char pendingArrivalLine[160] = "";

unsigned long lastWiFiAttemptAt = 0;
unsigned long lastWiFiCheckAt = 0;
unsigned long lastDiscoveryAt = 0;
unsigned long lastAdminAttemptAt = 0;
unsigned long lastArclAttemptAt = 0;
unsigned long arclConnectedAt = 0;
unsigned long diagnosticsRequestedAt = 0;
unsigned long routeStartedAt = 0;
unsigned long conveyorStartedAt = 0;
unsigned long sensorRawChangedAt = 0;
unsigned long lastHeartbeatAt = 0;
unsigned long lastArclStatusQueryAt = 0;

const size_t ADMIN_RX_CAPACITY = 256;
char adminRx[ADMIN_RX_CAPACITY];
size_t adminRxLength = 0;
bool adminRxOverflow = false;

const size_t DISCOVERY_RX_CAPACITY = 128;
char discoveryRx[DISCOVERY_RX_CAPACITY];

const size_t ARCL_RX_CAPACITY = 768;
char arclRx[ARCL_RX_CAPACITY];
size_t arclRxLength = 0;
bool arclRxOverflow = false;

// ============================================================================
// Forward declarations
// ============================================================================

void maintainWiFi();
void maintainServerDiscovery();
void maintainAdminConnection();
void maintainArclConnection();
void readAdminLines();
void readArclLines();
void monitorObjectSensor();
void updateTimers();
void sendStatus(const char *prefix);
void handleAdminCommand(char *command);
void handleArclLine(char *line);
void abortActiveRoute(const char *reason, bool sendStopCommand);

// ============================================================================
// Text helpers
// ============================================================================

void trimAscii(char *text) {
  if (text == nullptr) return;

  char *start = text;
  while (*start != '\0' && isspace(static_cast<unsigned char>(*start))) start++;
  if (start != text) memmove(text, start, strlen(start) + 1);

  size_t length = strlen(text);
  while (length > 0 && isspace(static_cast<unsigned char>(text[length - 1]))) {
    text[--length] = '\0';
  }
}

bool equalsIgnoreCase(const char *left, const char *right) {
  if (left == nullptr || right == nullptr) return false;
  while (*left != '\0' && *right != '\0') {
    if (tolower(static_cast<unsigned char>(*left)) !=
        tolower(static_cast<unsigned char>(*right))) return false;
    left++;
    right++;
  }
  return *left == '\0' && *right == '\0';
}

bool startsWithIgnoreCase(const char *text, const char *prefix) {
  if (text == nullptr || prefix == nullptr) return false;
  while (*prefix != '\0') {
    if (*text == '\0') return false;
    if (tolower(static_cast<unsigned char>(*text)) !=
        tolower(static_cast<unsigned char>(*prefix))) return false;
    text++;
    prefix++;
  }
  return true;
}

bool containsIgnoreCase(const char *text, const char *needle) {
  if (text == nullptr || needle == nullptr || *needle == '\0') return false;
  for (const char *position = text; *position != '\0'; position++) {
    if (startsWithIgnoreCase(position, needle)) return true;
  }
  return false;
}

void copyText(char *destination, size_t capacity, const char *source) {
  if (destination == nullptr || capacity == 0) return;
  if (source == nullptr) source = "";
  strncpy(destination, source, capacity - 1);
  destination[capacity - 1] = '\0';
}

const char *directionName(ConveyorDirection direction) {
  if (direction == CONVEYOR_FWD) return "FWD";
  if (direction == CONVEYOR_REV) return "REV";
  return "STOP";
}

// ============================================================================
// Reporting
// ============================================================================

bool writeLine(WiFiClient &client, const char *text) {
  if (!client.connected()) return false;
  return client.println(text) > 0;
}

bool reportAdmin(const char *format, ...) {
  char message[512];
  va_list arguments;
  va_start(arguments, format);
  vsnprintf(message, sizeof(message), format, arguments);
  va_end(arguments);

  Serial.println(message);
  if (!adminOnline || !adminClient.connected()) return false;
  if (writeLine(adminClient, message)) return true;

  adminSendFailed = true;
  return false;
}

void sendStatus(const char *prefix) {
  const IPAddress localIP = WiFi.localIP();
  reportAdmin(
      "%s firmware=%s WIFI=%s IP=%u.%u.%u.%u ADMIN=%s LD90_TCP=%s "
      "ARCL=%s MOTORS=%s FAULT_SCAN=%s FAULT=%u STEP=%u/%u "
      "ROUTE_RUNNING=%u ROUTE=%s WAIT=%u CONVEYOR=%s OBJECT=%s "
      "TRANSFER=%s uptime_ms=%lu rssi_dbm=%ld",
      prefix,
      FIRMWARE_VERSION,
      wifiOnline ? "CONNECTED" : "DISCONNECTED",
      localIP[0], localIP[1], localIP[2], localIP[3],
      adminOnline ? "CONNECTED" : "DISCONNECTED",
      ld90TcpOnline ? "CONNECTED" : "DISCONNECTED",
      arclAuthenticated ? "AUTHENTICATED" : "NOT_READY",
      motorsConfirmed ? "READY" : "NOT_CONFIRMED",
      faultScanComplete ? "COMPLETE" : (faultScanActive ? "PENDING" : "UNKNOWN"),
      faultDetected ? 1 : 0,
      static_cast<unsigned int>(expectedStep + 1),
      static_cast<unsigned int>(PROCESS_STEP_COUNT),
      routeRunning ? 1 : 0,
      activeRoute,
      waitActive ? 1 : 0,
      directionName(conveyorRunning ? activeDirection : CONVEYOR_STOPPED),
      sensorStableDetected ? "DETECTED" : "CLEAR",
      transferConfirmed ? "CONFIRMED" : "NOT_CONFIRMED",
      millis(),
      wifiOnline ? WiFi.RSSI() : 0L);
}

// ============================================================================
// Conveyor and sensor
// ============================================================================

void writeConveyorStopped() {
  digitalWrite(CONVEYOR_FWD_PIN, CONVEYOR_INACTIVE_LEVEL);
  digitalWrite(CONVEYOR_REV_PIN, CONVEYOR_INACTIVE_LEVEL);
}

void stopConveyor(const char *reason) {
  const bool wasRunning = conveyorRunning;
  writeConveyorStopped();
  conveyorRunning = false;
  if (wasRunning) reportAdmin("STATUS CONVEYOR_STOP reason=%s", reason);
}

bool startConveyor(ConveyorDirection direction, const char *reason) {
  if (direction == CONVEYOR_STOPPED) return false;

  const bool wasRunning = conveyorRunning;
  writeConveyorStopped();
  conveyorRunning = false;
  if (wasRunning) delay(CONVEYOR_DIRECTION_DEADTIME_MS);

  if (direction == CONVEYOR_FWD) {
    digitalWrite(CONVEYOR_REV_PIN, CONVEYOR_INACTIVE_LEVEL);
    digitalWrite(CONVEYOR_FWD_PIN, CONVEYOR_ACTIVE_LEVEL);
  } else {
    digitalWrite(CONVEYOR_FWD_PIN, CONVEYOR_INACTIVE_LEVEL);
    digitalWrite(CONVEYOR_REV_PIN, CONVEYOR_ACTIVE_LEVEL);
  }

  conveyorRunning = true;
  conveyorStartedAt = millis();
  conveyorStartedForRoute = routeRunning;
  sensorStateAtConveyorStart = sensorStableDetected;
  sensorChangedDuringTransfer = false;
  reportAdmin("STATUS CONVEYOR_START direction=%s reason=%s max_ms=%lu",
              directionName(direction), reason, CONVEYOR_MAX_RUN_MS);
  return true;
}

bool sensorTargetReached() {
  if (activeDirection == CONVEYOR_FWD) return sensorStableDetected;
  if (activeDirection == CONVEYOR_REV) return !sensorStableDetected;
  return false;
}

void monitorObjectSensor() {
  const bool rawDetected =
      digitalRead(OBJECT_SENSOR_PIN) == OBJECT_DETECTED_LEVEL;
  const unsigned long now = millis();

  if (rawDetected != sensorRawDetected) {
    sensorRawDetected = rawDetected;
    sensorRawChangedAt = now;
  }

  if (sensorStableDetected == sensorRawDetected ||
      now - sensorRawChangedAt < SENSOR_DEBOUNCE_MS) return;

  sensorStableDetected = sensorRawDetected;
  reportAdmin(sensorStableDetected
                  ? "STATUS OBJECT_DETECTED pin=D2 level=LOW"
                  : "STATUS OBJECT_CLEARED pin=D2 level=HIGH");

  if (!routeRunning || !waitActive || !conveyorRunning) return;
  if (sensorStableDetected != sensorStateAtConveyorStart) {
    sensorChangedDuringTransfer = true;
  }
  if (!sensorChangedDuringTransfer || !sensorTargetReached()) return;

  transferConfirmed = true;
  reportAdmin("STATUS TRANSFER_CONFIRMED direction=%s object=%s",
              directionName(activeDirection),
              sensorStableDetected ? "DETECTED" : "CLEAR");
  stopConveyor("OBJECT_SENSOR_TARGET");
}

// ============================================================================
// ARCL and route state
// ============================================================================

bool sendArclRaw(const char *command, bool reportTransmission = true) {
  if (!ld90TcpOnline || !arclClient.connected() || !arclAuthenticated) {
    reportAdmin("ERR LD90_ARCL_NOT_READY command=\"%s\"", command);
    return false;
  }
  if (!writeLine(arclClient, command)) {
    reportAdmin("ERR LD90_SEND_FAILED command=\"%s\"", command);
    return false;
  }
  if (reportTransmission) reportAdmin("STATUS ARCL_TX command=\"%s\"", command);
  else {
    Serial.print("ARCL_TX ");
    Serial.println(command);
  }
  return true;
}

void resetRouteState() {
  stopConveyor("ROUTE_STATE_CLEAR");
  routeRunning = false;
  waitActive = false;
  waitSeenForRoute = false;
  conveyorStartedForRoute = false;
  transferConfirmed = false;
  sensorChangedDuringTransfer = false;
  activeDirection = CONVEYOR_STOPPED;
  copyText(activeRoute, sizeof(activeRoute), "NONE");
}

void abortActiveRoute(const char *reason, bool sendStopCommand) {
  char failedRoute[sizeof(activeRoute)];
  copyText(failedRoute, sizeof(failedRoute), activeRoute);

  if (sendStopCommand && ld90TcpOnline && arclAuthenticated &&
      arclClient.connected()) {
    writeLine(arclClient, "stop");
    Serial.println("ARCL_TX stop");
  }

  resetRouteState();
  reportAdmin("ERR ROUTE_ABORTED route=%s detail=%s next_step=%u",
              failedRoute, reason,
              static_cast<unsigned int>(expectedStep + 1));
}

void requestDiagnostics() {
  if (!arclAuthenticated) {
    reportAdmin("ERR LD90_ARCL_NOT_READY action=PREPARE");
    return;
  }

  faultDetected = false;
  faultScanActive = true;
  faultScanComplete = false;
  diagnosticTimeoutReported = false;
  diagnosticsRequestedAt = millis();

  sendArclRaw("queryMotors", false);
  sendArclRaw("oneLineStatus", false);
  sendArclRaw("faultsGet", false);
  reportAdmin("STATUS DIAGNOSTICS_REQUESTED");
}

void requestMotorEnable() {
  if (!arclAuthenticated) {
    reportAdmin("ERR LD90_ARCL_NOT_READY action=ARM");
    return;
  }
  if (!faultScanComplete || faultScanActive) {
    reportAdmin("ERR DIAGNOSTICS_NOT_READY action=ARM use=PREPARE");
    return;
  }
  if (faultDetected) {
    reportAdmin("ERR LD90_FAULT_PRESENT action=ARM");
    return;
  }

  motorsConfirmed = false;
  motorEnableRequested = true;
  if (!sendArclRaw("enableMotors")) {
    motorEnableRequested = false;
    return;
  }
  sendArclRaw("queryMotors", false);
  reportAdmin("STATUS ARM_REQUESTED waiting=queryMotors");
}

bool routeAllowed() {
  if (!arclAuthenticated || !arclClient.connected()) {
    reportAdmin("ERR LD90_ARCL_NOT_READY");
    return false;
  }
  if (!faultScanComplete || faultScanActive) {
    reportAdmin("ERR DIAGNOSTICS_NOT_READY use=PREPARE");
    return false;
  }
  if (faultDetected) {
    reportAdmin("ERR LD90_FAULT_PRESENT use=PREPARE");
    return false;
  }
  if (!motorsConfirmed) {
    reportAdmin("ERR MOTORS_NOT_CONFIRMED use=ARM");
    return false;
  }
  if (routeRunning) {
    reportAdmin("ERR AMR_BUSY active=%s", activeRoute);
    return false;
  }
  return true;
}

void beginRoute(const char *route, ConveyorDirection direction) {
  if (!routeAllowed()) return;
  if (direction == CONVEYOR_STOPPED) {
    reportAdmin("ERR INVALID_DIRECTION");
    return;
  }

  const ProcessStep &expected = PROCESS_SEQUENCE[expectedStep];
  if (!equalsIgnoreCase(route, expected.route) || direction != expected.direction) {
    reportAdmin(
        "ERR SEQUENCE_MISMATCH expected=%s_%s received=%s_%s step=%u",
        expected.route, directionName(expected.direction), route,
        directionName(direction), static_cast<unsigned int>(expectedStep + 1));
    return;
  }

  char command[96];
  snprintf(command, sizeof(command), "patrolOnce %s", expected.route);
  if (!sendArclRaw(command)) return;

  routeRunning = true;
  waitActive = false;
  waitSeenForRoute = false;
  conveyorStartedForRoute = false;
  transferConfirmed = false;
  sensorChangedDuringTransfer = false;
  activeDirection = direction;
  copyText(activeRoute, sizeof(activeRoute), expected.route);
  routeStartedAt = millis();

  reportAdmin("STATUS ROUTE_START step=%u route=%s direction=%s",
              static_cast<unsigned int>(expectedStep + 1), activeRoute,
              directionName(activeDirection));
}

void finishActiveRoute() {
  char completedRoute[sizeof(activeRoute)];
  copyText(completedRoute, sizeof(completedRoute), activeRoute);
  const uint8_t completedStep = expectedStep + 1;
  const bool waitWasSeen = waitSeenForRoute;
  const bool conveyorWasStarted = conveyorStartedForRoute;
  const bool sensorWasConfirmed = transferConfirmed;

  stopConveyor("ROUTE_COMPLETE");

  if (REQUIRE_WAITSTATE_FOR_ARRIVAL && !waitWasSeen) {
    abortActiveRoute("WAITSTATE_NOT_SEEN", false);
    return;
  }
  if (REQUIRE_WAITSTATE_FOR_ARRIVAL && !conveyorWasStarted) {
    abortActiveRoute("CONVEYOR_NOT_STARTED", false);
    return;
  }
  if (REQUIRE_OBJECT_SENSOR_CONFIRMATION && !sensorWasConfirmed) {
    abortActiveRoute("OBJECT_SENSOR_NOT_CONFIRMED", false);
    return;
  }

  resetRouteState();
  expectedStep = (expectedStep + 1) % PROCESS_STEP_COUNT;

  snprintf(pendingArrivalLine, sizeof(pendingArrivalLine),
           "arrived route=%s step=%u transfer=%s",
           completedRoute, static_cast<unsigned int>(completedStep),
           sensorWasConfirmed ? "SENSOR_CONFIRMED" : "TIMER_OR_ROUTE_COMPLETE");
  pendingArrival = true;
  if (reportAdmin("%s", pendingArrivalLine)) pendingArrival = false;
}

void beginTransferWait() {
  if (!routeRunning || waitActive) return;

  waitActive = true;
  waitSeenForRoute = true;
  sensorChangedDuringTransfer = false;
  transferConfirmed = false;
  if (!startConveyor(activeDirection, "ARCL_WAITSTATE")) {
    abortActiveRoute("CONVEYOR_START_FAILED", true);
  }
}

void finishTransferWait() {
  if (!waitActive) return;
  waitActive = false;
  stopConveyor("WAITSTATE_COMPLETE");
  reportAdmin("STATUS WAITSTATE_COMPLETE transfer=%s",
              transferConfirmed ? "CONFIRMED" : "NOT_CONFIRMED");

  if (REQUIRE_OBJECT_SENSOR_CONFIRMATION && !transferConfirmed) {
    abortActiveRoute("WAIT_COMPLETED_WITHOUT_OBJECT_CONFIRMATION", true);
  }
}

bool isArclCommandError(const char *line) {
  return containsIgnoreCase(line, "commanderror") ||
         containsIgnoreCase(line, "command error") ||
         containsIgnoreCase(line, "unknown command") ||
         containsIgnoreCase(line, "unrecognized command") ||
         containsIgnoreCase(line, "invalid command");
}

void handleArclLine(char *line) {
  trimAscii(line);
  if (*line == '\0') return;

  Serial.print("ARCL_RX ");
  Serial.println(line);

  if (!arclAuthenticated) {
    if (containsIgnoreCase(line, "incorrect password") ||
        containsIgnoreCase(line, "invalid password") ||
        containsIgnoreCase(line, "login failed")) {
      reportAdmin("ERR ARCL_AUTH_FAILED check=ARCL_PASSWORD");
      arclClient.stop();
      return;
    }

    // A successful direct-robot ARCL login finishes its command list with this.
    if (equalsIgnoreCase(line, "End of commands")) {
      arclAuthenticated = true;
      writeLine(arclClient, "echo off");
      reportAdmin("STATUS LD90_ARCL_ONLINE auth=VERIFIED ip=192.168.0.10");
      requestDiagnostics();
      lastArclStatusQueryAt = millis();
    }
    return;
  }

  if (containsIgnoreCase(line, "motors enabled") ||
      containsIgnoreCase(line, "motors are enabled") ||
      containsIgnoreCase(line, "motorstate: enabled") ||
      containsIgnoreCase(line, "motor state: enabled")) {
    const bool wasReady = motorsConfirmed;
    motorsConfirmed = true;
    motorEnableRequested = false;
    if (!wasReady) reportAdmin("STATUS MOTORS_READY confirmed=queryMotors");
  } else if (containsIgnoreCase(line, "motors disabled") ||
             containsIgnoreCase(line, "motors are disabled") ||
             containsIgnoreCase(line, "motorstate: disabled") ||
             containsIgnoreCase(line, "motor state: disabled")) {
    const bool wasReady = motorsConfirmed;
    motorsConfirmed = false;
    motorEnableRequested = false;
    stopConveyor("MOTORS_DISABLED");
    if (routeRunning) abortActiveRoute("MOTORS_DISABLED", true);
    else if (wasReady) reportAdmin("ERR MOTORS_DISABLED");
  }

  if (startsWithIgnoreCase(line, "FaultList:")) {
    const char *detail = line + strlen("FaultList:");
    while (*detail != '\0' && isspace(static_cast<unsigned char>(*detail))) detail++;
    if (*detail != '\0' && !equalsIgnoreCase(detail, "none") &&
        !equalsIgnoreCase(detail, "0")) {
      faultDetected = true;
      motorsConfirmed = false;
      reportAdmin("ERR LD90_FAULT detail=\"%s\"", line);
    }
  } else if (equalsIgnoreCase(line, "End of FaultList")) {
    faultScanActive = false;
    faultScanComplete = true;
    diagnosticTimeoutReported = false;
    reportAdmin("STATUS FAULT_SCAN_COMPLETE faults=%u",
                faultDetected ? 1 : 0);
    if (AUTO_ENABLE_MOTORS && !faultDetected && !motorsConfirmed &&
        !motorEnableRequested) {
      requestMotorEnable();
    }
  }

  if (isArclCommandError(line)) {
    if (routeRunning) abortActiveRoute("ARCL_COMMAND_ERROR", true);
    reportAdmin("ERR ARCL_COMMAND detail=\"%s\"", line);
    return;
  }

  if (routeRunning &&
      startsWithIgnoreCase(line, "WaitState: Waiting completed")) {
    finishTransferWait();
    return;
  }

  if (routeRunning &&
      (startsWithIgnoreCase(line, "WaitState: Waiting interrupted") ||
       startsWithIgnoreCase(line, "WaitState: Waiting cancelled"))) {
    abortActiveRoute("WAITSTATE_INTERRUPTED", false);
    return;
  }

  if (routeRunning && startsWithIgnoreCase(line, "WaitState: Waiting") &&
      !containsIgnoreCase(line, "completed") &&
      !containsIgnoreCase(line, "interrupted") &&
      !containsIgnoreCase(line, "cancelled")) {
    beginTransferWait();
    return;
  }

  if (routeRunning && startsWithIgnoreCase(line, "Patrolling route ") &&
      containsIgnoreCase(line, " once")) {
    routeStartedAt = millis();
    reportAdmin("STATUS ROUTE_RUNNING route=%s", activeRoute);
    return;
  }

  if (routeRunning &&
      startsWithIgnoreCase(line, "Finished patrolling route ")) {
    if (!containsIgnoreCase(line, activeRoute)) {
      abortActiveRoute("ROUTE_COMPLETION_NAME_MISMATCH", false);
    } else {
      finishActiveRoute();
    }
    return;
  }

  if (routeRunning &&
      (containsIgnoreCase(line, "interrupted: patrolling") ||
       containsIgnoreCase(line, "failed patrolling") ||
       containsIgnoreCase(line, "cannot patrol") ||
       containsIgnoreCase(line, "route not found"))) {
    abortActiveRoute("LD90_REPORTED_ROUTE_FAILURE", false);
  }
}

// ============================================================================
// Admin commands
// ============================================================================

ConveyorDirection parseDirection(const char *text) {
  if (equalsIgnoreCase(text, "FWD")) return CONVEYOR_FWD;
  if (equalsIgnoreCase(text, "REV")) return CONVEYOR_REV;
  return CONVEYOR_STOPPED;
}

void handleRunCommand(char *command) {
  // Expected wire format: RUN ROUTE_ST1 FWD
  char *route = command + 4;
  while (*route == ' ') route++;
  char *space = strchr(route, ' ');
  if (space == nullptr) {
    reportAdmin("ERR COMMAND_FORMAT use=RUN_ROUTE_DIRECTION");
    return;
  }
  *space = '\0';
  char *directionText = space + 1;
  trimAscii(route);
  trimAscii(directionText);
  if (*route == '\0' || *directionText == '\0' || strchr(directionText, ' ')) {
    reportAdmin("ERR COMMAND_FORMAT use=RUN_ROUTE_DIRECTION");
    return;
  }
  beginRoute(route, parseDirection(directionText));
}

void handleAdminCommand(char *command) {
  trimAscii(command);
  if (*command == '\0') return;

  Serial.print("ADMIN_RX ");
  Serial.println(command);

  if (equalsIgnoreCase(command, "STOP") ||
      equalsIgnoreCase(command, "ESTOP")) {
    const bool wasRunning = routeRunning;
    if (ld90TcpOnline && arclAuthenticated && arclClient.connected()) {
      writeLine(arclClient, "stop");
      Serial.println("ARCL_TX stop");
    }
    resetRouteState();
    reportAdmin("STATUS STOPPED route_was_running=%u", wasRunning ? 1 : 0);
    return;
  }

  if (equalsIgnoreCase(command, "STATUS")) {
    sendStatus("STATUS");
    if (arclAuthenticated) {
      sendArclRaw("oneLineStatus", false);
      sendArclRaw("queryMotors", false);
    }
    return;
  }

  if (equalsIgnoreCase(command, "PREPARE") ||
      equalsIgnoreCase(command, "DIAGNOSE")) {
    if (routeRunning) reportAdmin("ERR AMR_BUSY action=PREPARE");
    else requestDiagnostics();
    return;
  }

  if (equalsIgnoreCase(command, "ARM")) {
    requestMotorEnable();
    return;
  }

  if (equalsIgnoreCase(command, "DISARM")) {
    if (routeRunning) abortActiveRoute("DISARM_REQUESTED", true);
    else stopConveyor("DISARM_REQUESTED");
    motorsConfirmed = false;
    motorEnableRequested = false;
    if (arclAuthenticated) sendArclRaw("disableMotors");
    reportAdmin("STATUS DISARM_REQUESTED");
    return;
  }

  if (equalsIgnoreCase(command, "RESET_SEQUENCE")) {
    if (routeRunning) {
      reportAdmin("ERR AMR_BUSY action=RESET_SEQUENCE");
    } else {
      expectedStep = 0;
      pendingArrival = false;
      pendingArrivalLine[0] = '\0';
      reportAdmin("STATUS SEQUENCE_RESET next_step=1 expected=ROUTE_ST1_FWD");
    }
    return;
  }

  if (startsWithIgnoreCase(command, "RUN ")) {
    handleRunCommand(command);
    return;
  }

  // Backward-compatible single-motion test used in earlier Admin versions.
  if (equalsIgnoreCase(command, "START")) {
    beginRoute(PROCESS_SEQUENCE[0].route, PROCESS_SEQUENCE[0].direction);
    return;
  }

  if (equalsIgnoreCase(command, "CONVEYOR_FWD") ||
      equalsIgnoreCase(command, "CONVEYOR_FORWARD")) {
    if (routeRunning) reportAdmin("ERR AMR_BUSY action=MANUAL_CONVEYOR");
    else {
      activeDirection = CONVEYOR_FWD;
      startConveyor(CONVEYOR_FWD, "MANUAL_TEST");
    }
    return;
  }

  if (equalsIgnoreCase(command, "CONVEYOR_REV") ||
      equalsIgnoreCase(command, "CONVEYOR_REVERSE")) {
    if (routeRunning) reportAdmin("ERR AMR_BUSY action=MANUAL_CONVEYOR");
    else {
      activeDirection = CONVEYOR_REV;
      startConveyor(CONVEYOR_REV, "MANUAL_TEST");
    }
    return;
  }

  if (equalsIgnoreCase(command, "CONVEYOR_OFF")) {
    stopConveyor("MANUAL_COMMAND");
    activeDirection = CONVEYOR_STOPPED;
    return;
  }

  reportAdmin(
      "ERR UNKNOWN_COMMAND use=RUN,RESET_SEQUENCE,PREPARE,ARM,DISARM,STOP,STATUS,START,CONVEYOR_FWD,CONVEYOR_REV,CONVEYOR_OFF");
}

// ============================================================================
// Central-server discovery
// ============================================================================

bool isSameSubnet(const IPAddress &left, const IPAddress &right,
                  const IPAddress &mask) {
  for (uint8_t i = 0; i < 4; ++i) {
    if ((left[i] & mask[i]) != (right[i] & mask[i])) return false;
  }
  return true;
}

IPAddress calculateBroadcast(const IPAddress &local, const IPAddress &mask) {
  return IPAddress(
      static_cast<uint8_t>(local[0] | static_cast<uint8_t>(~mask[0])),
      static_cast<uint8_t>(local[1] | static_cast<uint8_t>(~mask[1])),
      static_cast<uint8_t>(local[2] | static_cast<uint8_t>(~mask[2])),
      static_cast<uint8_t>(local[3] | static_cast<uint8_t>(~mask[3])));
}

void invalidateAdminServer() {
  adminServerKnown = false;
  discoveredAdminIP = IPAddress(0, 0, 0, 0);
  lastDiscoveryAt = millis() - DISCOVERY_RETRY_MS;
}

void stopDiscoveryUdp() {
  if (!discoveryUdpStarted) return;
  discoveryUdp.stop();
  discoveryUdpStarted = false;
}

bool startDiscoveryUdp() {
  if (discoveryUdpStarted) return true;

  discoveryUdpStarted = discoveryUdp.begin(DISCOVERY_LOCAL_PORT) == 1;
  if (discoveryUdpStarted) {
    Serial.print("DISCOVERY_READY local_port=");
    Serial.println(DISCOVERY_LOCAL_PORT);
  } else {
    Serial.println("ERR DISCOVERY_UDP_BIND_FAILED");
  }
  return discoveryUdpStarted;
}

void transmitDiscoveryTo(const IPAddress &destination) {
  if (!discoveryUdp.beginPacket(destination, DISCOVERY_SERVER_PORT)) return;
  discoveryUdp.write(reinterpret_cast<const uint8_t *>(DISCOVERY_REQUEST),
                     strlen(DISCOVERY_REQUEST));
  discoveryUdp.endPacket();
}

void sendDiscoveryRequest() {
  const IPAddress local = WiFi.localIP();
  const IPAddress mask = WiFi.subnetMask();
  const IPAddress directedBroadcast = calculateBroadcast(local, mask);

  transmitDiscoveryTo(directedBroadcast);
  const IPAddress limitedBroadcast(255, 255, 255, 255);
  if (directedBroadcast != limitedBroadcast) {
    transmitDiscoveryTo(limitedBroadcast);
  }

  Serial.print("DISCOVERY_TX target=");
  Serial.print(directedBroadcast);
  Serial.print(':');
  Serial.println(DISCOVERY_SERVER_PORT);
}

void readDiscoveryResponses() {
  int packetSize = discoveryUdp.parsePacket();
  while (packetSize > 0) {
    const IPAddress remote = discoveryUdp.remoteIP();
    size_t length = 0;

    while (discoveryUdp.available() && length + 1 < DISCOVERY_RX_CAPACITY) {
      const int value = discoveryUdp.read();
      if (value < 0) break;
      discoveryRx[length++] = static_cast<char>(value);
    }
    while (discoveryUdp.available()) discoveryUdp.read();
    discoveryRx[length] = '\0';
    trimAscii(discoveryRx);

    const IPAddress local = WiFi.localIP();
    const IPAddress mask = WiFi.subnetMask();
    if (strcmp(discoveryRx, DISCOVERY_RESPONSE) == 0 &&
        isSameSubnet(local, remote, mask)) {
      discoveredAdminIP = remote;
      adminServerKnown = true;
      lastAdminAttemptAt = millis() - ADMIN_RETRY_MS;
      Serial.print("DISCOVERY_OK admin=");
      Serial.print(discoveredAdminIP);
      Serial.print(':');
      Serial.println(ADMIN_SERVER_PORT);
      return;
    }

    Serial.print("DISCOVERY_IGNORED from=");
    Serial.print(remote);
    Serial.print(" message=");
    Serial.println(discoveryRx);
    packetSize = discoveryUdp.parsePacket();
  }
}

void maintainServerDiscovery() {
  if (!wifiOnline || adminOnline) return;

  const unsigned long now = millis();
  if (!discoveryUdpStarted) {
    if (now - lastDiscoveryAt < DISCOVERY_RETRY_MS) return;
    lastDiscoveryAt = now;
    if (!startDiscoveryUdp()) return;
    lastDiscoveryAt = now - DISCOVERY_RETRY_MS;
  }

  readDiscoveryResponses();
  if (adminServerKnown) return;

  if (now - lastDiscoveryAt >= DISCOVERY_RETRY_MS) {
    lastDiscoveryAt = now;
    sendDiscoveryRequest();
  }
}

// ============================================================================
// Connection management
// ============================================================================

void clearArclState() {
  arclClient.stop();
  ld90TcpOnline = false;
  arclAuthenticated = false;
  motorsConfirmed = false;
  faultScanActive = false;
  faultScanComplete = false;
  faultDetected = false;
  diagnosticTimeoutReported = false;
  motorEnableRequested = false;
  arclRxLength = 0;
  arclRxOverflow = false;
}

void handleArclLoss(const char *reason) {
  const bool wasOnline = ld90TcpOnline;
  if (routeRunning) abortActiveRoute(reason, false);
  clearArclState();
  if (wasOnline) reportAdmin("ERR LD90_DISCONNECTED reason=%s", reason);
}

void handleAdminLoss(const char *reason) {
  const bool wasOnline = adminOnline;
  adminClient.stop();
  adminOnline = false;
  adminSendFailed = false;
  adminRxLength = 0;
  adminRxOverflow = false;
  invalidateAdminServer();

  stopConveyor("ADMIN_DISCONNECTED");
  if (routeRunning && STOP_AMR_ON_ADMIN_LOSS) {
    if (ld90TcpOnline && arclAuthenticated && arclClient.connected()) {
      writeLine(arclClient, "stop");
      Serial.println("ARCL_TX stop (admin disconnected)");
    }
    resetRouteState();
  }

  if (wasOnline) {
    Serial.print("ERR ADMIN_DISCONNECTED reason=");
    Serial.println(reason);
  }
}

void handleWiFiLoss() {
  const bool wasOnline = wifiOnline;
  handleAdminLoss("WIFI_DISCONNECTED");
  handleArclLoss("WIFI_DISCONNECTED");
  stopDiscoveryUdp();
  wifiOnline = false;
  if (wasOnline) Serial.println("ERR WIFI_DISCONNECTED outputs=SAFE");
}

void beginWiFi() {
  lastWiFiAttemptAt = millis();
  WiFi.disconnect();
  delay(100);
  Serial.print("WIFI_CONNECTING ssid=");
  Serial.print(WIFI_SSID);
  Serial.println(WIFI_PASSWORD[0] == '\0' ? " security=OPEN" : " security=PASSWORD");

  if (WIFI_PASSWORD[0] == '\0') WiFi.begin(WIFI_SSID);
  else WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void maintainWiFi() {
  const unsigned long now = millis();

  if (wifiOnline) {
    if (now - lastWiFiCheckAt < WIFI_CHECK_MS) return;
    lastWiFiCheckAt = now;
    if (WiFi.status() == WL_CONNECTED) return;
    handleWiFiLoss();
  }

  if (WiFi.status() == WL_CONNECTED) {
    wifiOnline = true;
    lastWiFiCheckAt = now;
    invalidateAdminServer();
    lastAdminAttemptAt = now;
    lastArclAttemptAt = now - LD90_RETRY_MS;
    Serial.print("WIFI_CONNECTED ip=");
    Serial.println(WiFi.localIP());
    return;
  }

  if (lastWiFiAttemptAt == 0 || now - lastWiFiAttemptAt >= WIFI_RETRY_MS) {
    beginWiFi();
  }
}

void attemptAdminConnection() {
  if (!adminServerKnown) return;

  lastAdminAttemptAt = millis();
  adminClient.stop();
  adminClient.setConnectionTimeout(TCP_CONNECTION_TIMEOUT_MS);

  Serial.print("ADMIN_CONNECTING ");
  Serial.print(discoveredAdminIP);
  Serial.print(':');
  Serial.println(ADMIN_SERVER_PORT);

  if (!adminClient.connect(discoveredAdminIP, ADMIN_SERVER_PORT)) {
    Serial.println("ERR ADMIN_CONNECT_FAILED rediscovery=ON");
    invalidateAdminServer();
    return;
  }

  adminOnline = true;
  adminSendFailed = false;
  adminRxLength = 0;
  adminRxOverflow = false;
  lastHeartbeatAt = millis();

  if (!writeLine(adminClient, ADMIN_CLIENT_NAME)) {
    handleAdminLoss("REGISTRATION_FAILED");
    return;
  }

  const IPAddress localIP = WiFi.localIP();
  reportAdmin(
      "ONLINE device=amr firmware=%s wifi_ip=%u.%u.%u.%u admin=%u.%u.%u.%u:%u protocol=RUN_ROUTE_V4 discovery=UDP",
      FIRMWARE_VERSION, localIP[0], localIP[1], localIP[2], localIP[3],
      discoveredAdminIP[0], discoveredAdminIP[1], discoveredAdminIP[2],
      discoveredAdminIP[3], ADMIN_SERVER_PORT);
  sendStatus("STATUS");

  if (pendingArrival && writeLine(adminClient, pendingArrivalLine)) {
    Serial.print("ADMIN_REPLAY ");
    Serial.println(pendingArrivalLine);
    pendingArrival = false;
  }
}

void maintainAdminConnection() {
  if (!wifiOnline) return;

  if (adminSendFailed) {
    handleAdminLoss("SEND_FAILED");
  } else if (adminOnline && !adminClient.connected()) {
    handleAdminLoss("SOCKET_CLOSED");
  }

  if (adminOnline && adminClient.connected()) return;
  if (adminServerKnown && millis() - lastAdminAttemptAt >= ADMIN_RETRY_MS) {
    attemptAdminConnection();
  }
}

void attemptArclConnection() {
  lastArclAttemptAt = millis();
  clearArclState();
  arclClient.setConnectionTimeout(TCP_CONNECTION_TIMEOUT_MS);

  Serial.print("ARCL_CONNECTING ");
  Serial.print(LD90_IP);
  Serial.print(':');
  Serial.println(LD90_ARCL_PORT);

  if (!arclClient.connect(LD90_IP, LD90_ARCL_PORT)) return;

  ld90TcpOnline = true;
  arclConnectedAt = millis();
  if (!writeLine(arclClient, ARCL_PASSWORD)) {
    handleArclLoss("PASSWORD_SEND_FAILED");
    return;
  }
  reportAdmin("STATUS LD90_TCP_CONNECTED ARCL=AUTHENTICATING");
}

void maintainArclConnection() {
  if (!wifiOnline) return;

  if (ld90TcpOnline && !arclClient.connected()) {
    handleArclLoss("SOCKET_CLOSED");
  }

  if (!ld90TcpOnline) {
    if (millis() - lastArclAttemptAt >= LD90_RETRY_MS) {
      attemptArclConnection();
    }
    return;
  }

  if (!arclAuthenticated &&
      millis() - arclConnectedAt >= ARCL_LOGIN_TIMEOUT_MS) {
    reportAdmin("ERR ARCL_AUTH_TIMEOUT check=ARCL_PASSWORD");
    handleArclLoss("AUTH_TIMEOUT");
  }
}

// ============================================================================
// Line readers and timers
// ============================================================================

void readAdminLines() {
  while (adminOnline && adminClient.connected() && adminClient.available()) {
    const char character = static_cast<char>(adminClient.read());
    if (character == '\n') {
      if (adminRxOverflow) {
        reportAdmin("ERR ADMIN_LINE_TOO_LONG max=%u",
                    static_cast<unsigned int>(ADMIN_RX_CAPACITY - 1));
      } else {
        adminRx[adminRxLength] = '\0';
        handleAdminCommand(adminRx);
      }
      adminRxLength = 0;
      adminRxOverflow = false;
    } else if (character != '\r') {
      if (adminRxLength + 1 < ADMIN_RX_CAPACITY) {
        adminRx[adminRxLength++] = character;
      } else {
        adminRxOverflow = true;
      }
    }
  }
}

void readArclLines() {
  while (ld90TcpOnline && arclClient.connected() && arclClient.available()) {
    const char character = static_cast<char>(arclClient.read());
    if (character == '\n') {
      if (arclRxOverflow) {
        reportAdmin("ERR ARCL_LINE_TOO_LONG max=%u",
                    static_cast<unsigned int>(ARCL_RX_CAPACITY - 1));
      } else {
        arclRx[arclRxLength] = '\0';
        handleArclLine(arclRx);
      }
      arclRxLength = 0;
      arclRxOverflow = false;
    } else if (character != '\r') {
      if (arclRxLength + 1 < ARCL_RX_CAPACITY) {
        arclRx[arclRxLength++] = character;
      } else {
        arclRxOverflow = true;
      }
    }
  }
}

void updateTimers() {
  const unsigned long now = millis();

  if (conveyorRunning && now - conveyorStartedAt >= CONVEYOR_MAX_RUN_MS) {
    stopConveyor("WATCHDOG_5S");
    if (routeRunning && waitActive && REQUIRE_OBJECT_SENSOR_CONFIRMATION &&
        !transferConfirmed) {
      abortActiveRoute("OBJECT_SENSOR_TIMEOUT", true);
    }
  }

  if (routeRunning && now - routeStartedAt >= MOTION_TIMEOUT_MS) {
    abortActiveRoute("MOTION_TIMEOUT", true);
  }

  if (faultScanActive && !diagnosticTimeoutReported &&
      now - diagnosticsRequestedAt >= DIAGNOSTIC_TIMEOUT_MS) {
    diagnosticTimeoutReported = true;
    faultScanActive = false;
    faultScanComplete = false;
    reportAdmin("ERR DIAGNOSTIC_TIMEOUT command=faultsGet");
  }

  if (adminOnline && now - lastHeartbeatAt >= HEARTBEAT_MS) {
    lastHeartbeatAt = now;
    sendStatus("HEARTBEAT");
  }

  if (arclAuthenticated && now - lastArclStatusQueryAt >= LD90_STATUS_QUERY_MS) {
    lastArclStatusQueryAt = now;
    sendArclRaw("oneLineStatus", false);
    sendArclRaw("queryMotors", false);
  }
}

// ============================================================================
// Arduino entry points
// ============================================================================

void setup() {
  pinMode(OBJECT_SENSOR_PIN, INPUT_PULLUP);
  pinMode(CONVEYOR_FWD_PIN, OUTPUT);
  pinMode(CONVEYOR_REV_PIN, OUTPUT);
  writeConveyorStopped();

  Serial.begin(115200);
  delay(1200);

  sensorRawDetected =
      digitalRead(OBJECT_SENSOR_PIN) == OBJECT_DETECTED_LEVEL;
  sensorStableDetected = sensorRawDetected;
  sensorRawChangedAt = millis();

  Serial.println("AMR_Server_Bridge_V4 starting");
  Serial.print("FIRMWARE ");
  Serial.println(FIRMWARE_VERSION);
  Serial.println("ADMIN auto-discovery UDP:5001 -> TCP:5000 name=amr");
  Serial.println("LD90 192.168.0.10:7171 mode=direct_ARCL");
  Serial.println("WIFI ROBOT_MA2_2G security=OPEN dhcp=ON");

  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("ERR WIFI_MODULE_NOT_FOUND");
  }

  beginWiFi();
}

void loop() {
  maintainWiFi();
  maintainServerDiscovery();
  maintainAdminConnection();
  maintainArclConnection();
  readAdminLines();
  readArclLines();
  monitorObjectSensor();
  updateTimers();
}
