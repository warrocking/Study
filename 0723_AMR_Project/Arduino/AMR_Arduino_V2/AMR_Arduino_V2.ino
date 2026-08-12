#include <WiFiS3.h>
#include <Wire.h>
#include <HUSKYLENS.h>

#include <ctype.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

/*
  AMR_Arduino_V2

  Arduino UNO R4 WiFi bridge for:
    Server_admin_V2.py / Server_admin_V3.py <-> Arduino <-> Omron LD-90 ARCL

  Main differences from AMR_Arduino.ino:
    - Matches Server_admin_V2.py and V3 directly (TCP 5000, first line "amr").
    - Uses the confirmed Admin LAN address instead of unsupported UDP discovery.
    - Sends STATUS/HEARTBEAT, DONE and ERR messages understood by the Admin server.
    - Connects directly to the LD-90 ARCL server at TCP 7171.
    - Uses faultsGet (AMR command), not queryFaults (Fleet Manager command).
    - Starts the automatic conveyor only after both an ARCL WaitState and
      HUSKYLENS learned object ID 1 are confirmed.
    - Keeps both conveyor outputs inactive on boot and on communication faults.

  IMPORTANT:
    - D10/D11 must drive an isolated relay or motor driver input. Never connect a
      conveyor motor directly to Arduino pins.
    - The LD-90 safety system and physical emergency stop remain authoritative.
    - Keep this file in its own AMR_Arduino_V2 sketch folder.
*/

// ============================================================================
// User settings
// ============================================================================

const char WIFI_SSID[] = "ROBOT_MA2_2G";
const char WIFI_PASSWORD[] = "";  // Open Wi-Fi. Enter a password if one is added.

IPAddress ARDUINO_IP(192, 168, 0, 182);
IPAddress DNS_IP(192, 168, 0, 1);
IPAddress GATEWAY_IP(192, 168, 0, 1);
IPAddress SUBNET_MASK(255, 255, 255, 0);

// Server_admin_V2.py listens on 0.0.0.0:5000. Arduino reaches it through LAN.
IPAddress ADMIN_SERVER_IP(192, 168, 0, 168);
const uint16_t ADMIN_SERVER_PORT = 5000;
const char ADMIN_CLIENT_NAME[] = "amr";

// MobilePlanner > Robot Interface > ARCL Server Setup
IPAddress LD90_IP(192, 168, 0, 10);
const uint16_t LD90_ARCL_PORT = 7171;
const char ARCL_PASSWORD[] = "1234";

const char FIRMWARE_VERSION[] = "2026-08-04-server-admin-v6";

const char ROUTE_ST1[] = "ROUTE_ST1";
const char ROUTE_ST2[] = "ROUTE_ST2";
const char ROUTE_ST3[] = "ROUTE_ST3";
const char MACRO_ST1[] = "MACRO_ST1";
const char MACRO_ST2[] = "MACRO_ST2";
const char MACRO_ST3[] = "MACRO_ST3";

const uint8_t PRODUCT_OBJECT_ID = 1;
const uint8_t HUSKY_CONFIRM_COUNT = 2;

const uint8_t CONVEYOR_FORWARD_PIN = 10;
const uint8_t CONVEYOR_REVERSE_PIN = 11;
const uint8_t CONVEYOR_ACTIVE_LEVEL = HIGH;
const uint8_t CONVEYOR_INACTIVE_LEVEL = LOW;
const unsigned long CONVEYOR_RUN_MS = 5000;
const unsigned long CONVEYOR_DIRECTION_DEADTIME_MS = 100;

// Safety and diagnostic policy.
const bool STOP_MOTION_ON_ADMIN_LOSS = true;
const bool ALLOW_RAW_ARCL = false;

// "Start" remains the single movement test requested for all Start broadcasts.
// Use "amr Cycle" for the complete six-macro production sequence.

// ============================================================================
// Timing
// ============================================================================

const unsigned long WIFI_RETRY_MS = 10000;
const unsigned long WIFI_CHECK_MS = 1000;
const unsigned long ADMIN_RETRY_MS = 3000;
const unsigned long LD90_RETRY_MS = 5000;
const unsigned long ARCL_LOGIN_TIMEOUT_MS = 10000;
const unsigned long HEARTBEAT_MS = 30000;
const unsigned long LD90_STATUS_QUERY_MS = 15000;
const unsigned long MOTION_TIMEOUT_MS = 180000;
const unsigned long NEXT_MACRO_DELAY_MS = 1500;
const unsigned long HUSKY_RETRY_MS = 10000;
const unsigned long HUSKY_POLL_MS = 150;
const uint8_t HUSKY_MAX_REQUEST_FAILURES = 3;
const int CONNECTION_TIMEOUT_MS = 1200;

// ============================================================================
// Process configuration
// ============================================================================

enum ConveyorDirection : uint8_t {
  CONVEYOR_STOPPED,
  CONVEYOR_FORWARD,
  CONVEYOR_REVERSE
};

enum MotionKind : uint8_t {
  MOTION_NONE,
  MOTION_ROUTE,
  MOTION_MACRO
};

const char *const CYCLE_MACROS[] = {
  MACRO_ST1, MACRO_ST2, MACRO_ST1, MACRO_ST3, MACRO_ST2, MACRO_ST3
};

const ConveyorDirection CYCLE_CONVEYOR[] = {
  CONVEYOR_FORWARD,
  CONVEYOR_REVERSE,
  CONVEYOR_REVERSE,
  CONVEYOR_FORWARD,
  CONVEYOR_REVERSE,
  CONVEYOR_REVERSE
};

const uint8_t CYCLE_COUNT = sizeof(CYCLE_MACROS) / sizeof(CYCLE_MACROS[0]);

// ============================================================================
// Network and device state
// ============================================================================

WiFiClient adminClient;
WiFiClient ld90Client;
HUSKYLENS huskylens;

bool wifiOnline = false;
bool adminOnline = false;
bool adminLossPending = false;
bool ld90TcpOnline = false;
bool arclAuthenticated = false;
bool motorsConfirmed = false;
bool faultDetected = false;
bool faultScanActive = false;
bool faultScanCompleted = false;

bool huskyOnline = false;
uint8_t huskyRequestFailures = 0;
uint8_t huskyDetectionCount = 0;

MotionKind motionKind = MOTION_NONE;
bool cycleRunning = false;
bool nextMacroPending = false;
bool stopRequested = false;
bool waitActive = false;
bool waitSeenThisMotion = false;
bool conveyorStartedThisWait = false;
bool conveyorRunning = false;
bool arrivalRequired = false;

uint8_t cycleStep = 0;
uint8_t manualSequenceStep = 0;
ConveyorDirection conveyorDirection = CONVEYOR_STOPPED;
ConveyorDirection pendingAutoDirection = CONVEYOR_STOPPED;

char activeMotionName[64] = "NONE";
char activeArrivalLabel[48] = "NONE";

unsigned long lastWiFiAttempt = 0;
unsigned long lastWiFiCheck = 0;
unsigned long lastAdminAttempt = 0;
unsigned long lastLD90Attempt = 0;
unsigned long ld90ConnectedAt = 0;
unsigned long lastHeartbeat = 0;
unsigned long lastLD90StatusQuery = 0;
unsigned long motionStartedAt = 0;
unsigned long nextMacroAt = 0;
unsigned long conveyorStartedAt = 0;
unsigned long lastHuskyAttempt = 0;
unsigned long lastHuskyPoll = 0;

const size_t ADMIN_RX_CAPACITY = 256;
char adminRx[ADMIN_RX_CAPACITY];
size_t adminRxLength = 0;
bool adminRxOverflow = false;

const size_t LD90_RX_CAPACITY = 768;
char ld90Rx[LD90_RX_CAPACITY];
size_t ld90RxLength = 0;
bool ld90RxOverflow = false;

// ============================================================================
// Forward declarations
// ============================================================================

void maintainWiFi();
void maintainAdminConnection();
void maintainLD90Connection();
void maintainHuskyLens();
void readAdminCommands();
void readLD90Lines();
void updateTimedActions();
void sendStatus(const char *prefix);
void handleAdminCommand(char *command);
void handleLD90Line(char *line);
void clearProcessState();
void abortProcess(const char *reason);
bool beginMacro(const char *name, bool fromCycle);
bool beginOrchestratedMacro(const char *name, const char *arrivalLabel);

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

const char *motionText() {
  if (motionKind == MOTION_ROUTE) return "ROUTE";
  if (motionKind == MOTION_MACRO) return "MACRO";
  return "NONE";
}

const char *conveyorText() {
  if (conveyorDirection == CONVEYOR_FORWARD) return "FORWARD";
  if (conveyorDirection == CONVEYOR_REVERSE) return "REVERSE";
  return "OFF";
}

// ============================================================================
// Reporting compatible with Server_admin_V2.py
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

  adminClient.stop();
  adminOnline = false;
  adminLossPending = true;
  return false;
}

void sendStatus(const char *prefix) {
  const IPAddress localIP = WiFi.localIP();
  reportAdmin(
    "%s firmware=%s WIFI=%s IP=%u.%u.%u.%u ADMIN=%s LD90=%s "
    "MOTORS=%s FAULT=%u FAULT_SCAN=%s MOTION=%s ACTIVE=%s CYCLE=%u STEP=%u/%u "
    "HUSKY=%s CONVEYOR=%s uptime_ms=%lu rssi_dbm=%ld",
    prefix,
    FIRMWARE_VERSION,
    wifiOnline ? "CONNECTED" : "DISCONNECTED",
    localIP[0], localIP[1], localIP[2], localIP[3],
    adminOnline ? "CONNECTED" : "DISCONNECTED",
    arclAuthenticated ? "CONNECTED" : "DISCONNECTED",
    motorsConfirmed ? "READY" : "NOT_CONFIRMED",
    faultDetected ? 1 : 0,
    faultScanCompleted ? "READY" : (faultScanActive ? "PENDING" : "UNKNOWN"),
    motionText(),
    activeMotionName,
    cycleRunning ? 1 : 0,
    cycleRunning ? static_cast<unsigned int>(cycleStep + 1) : 0,
    static_cast<unsigned int>(CYCLE_COUNT),
    huskyOnline ? "ONLINE" : "OFFLINE",
    conveyorText(),
    millis(),
    wifiOnline ? WiFi.RSSI() : 0L);
}

// ============================================================================
// Conveyor
// ============================================================================

void writeConveyorInactive() {
  digitalWrite(CONVEYOR_FORWARD_PIN, CONVEYOR_INACTIVE_LEVEL);
  digitalWrite(CONVEYOR_REVERSE_PIN, CONVEYOR_INACTIVE_LEVEL);
}

void stopConveyor(const char *reason) {
  const bool wasRunning = conveyorRunning;
  writeConveyorInactive();
  conveyorRunning = false;
  conveyorDirection = CONVEYOR_STOPPED;

  if (wasRunning) {
    reportAdmin("EVENT CONVEYOR_OFF reason=%s D10=%s D11=%s",
                reason,
                CONVEYOR_INACTIVE_LEVEL == HIGH ? "HIGH" : "LOW",
                CONVEYOR_INACTIVE_LEVEL == HIGH ? "HIGH" : "LOW");
  }
}

bool startConveyor(ConveyorDirection direction, const char *reason) {
  if (direction == CONVEYOR_STOPPED) return false;

  const bool wasRunning = conveyorRunning;
  writeConveyorInactive();
  conveyorRunning = false;
  conveyorDirection = CONVEYOR_STOPPED;
  if (wasRunning) delay(CONVEYOR_DIRECTION_DEADTIME_MS);

  if (direction == CONVEYOR_FORWARD) {
    digitalWrite(CONVEYOR_REVERSE_PIN, CONVEYOR_INACTIVE_LEVEL);
    digitalWrite(CONVEYOR_FORWARD_PIN, CONVEYOR_ACTIVE_LEVEL);
    reportAdmin("EVENT CONVEYOR_FORWARD reason=%s duration_ms=%lu",
                reason, CONVEYOR_RUN_MS);
  } else {
    digitalWrite(CONVEYOR_FORWARD_PIN, CONVEYOR_INACTIVE_LEVEL);
    digitalWrite(CONVEYOR_REVERSE_PIN, CONVEYOR_ACTIVE_LEVEL);
    reportAdmin("EVENT CONVEYOR_REVERSE reason=%s duration_ms=%lu",
                reason, CONVEYOR_RUN_MS);
  }

  conveyorDirection = direction;
  conveyorRunning = true;
  conveyorStartedAt = millis();
  return true;
}

// ============================================================================
// ARCL commands and process state
// ============================================================================

bool sendARCL(const char *command, bool reportTransmission = true) {
  if (!ld90TcpOnline || !ld90Client.connected() || !arclAuthenticated) {
    reportAdmin("ERR LD90_NOT_READY command=\"%s\"", command);
    return false;
  }

  if (!writeLine(ld90Client, command)) {
    reportAdmin("ERR LD90_SEND_FAILED command=\"%s\"", command);
    return false;
  }

  if (reportTransmission) reportAdmin("EVENT ARCL_TX command=\"%s\"", command);
  else {
    Serial.print("ARCL_TX ");
    Serial.println(command);
  }
  return true;
}

void resetWaitState() {
  waitActive = false;
  waitSeenThisMotion = false;
  conveyorStartedThisWait = false;
  pendingAutoDirection = CONVEYOR_STOPPED;
  huskyDetectionCount = 0;
}

void clearProcessState() {
  stopConveyor("PROCESS_CLEAR");
  motionKind = MOTION_NONE;
  cycleRunning = false;
  nextMacroPending = false;
  stopRequested = false;
  cycleStep = 0;
  resetWaitState();
  copyText(activeMotionName, sizeof(activeMotionName), "NONE");
  arrivalRequired = false;
  copyText(activeArrivalLabel, sizeof(activeArrivalLabel), "NONE");
}

void abortProcess(const char *reason) {
  if (ld90TcpOnline && arclAuthenticated && ld90Client.connected()) {
    writeLine(ld90Client, "stop");
    Serial.println("ARCL_TX stop");
  }
  clearProcessState();
  reportAdmin("ERR PROCESS_ABORT reason=%s", reason);
}

bool motionAllowed(bool requireHusky) {
  if (!arclAuthenticated) {
    reportAdmin("ERR LD90_NOT_READY use=Prepare");
    return false;
  }
  if (!motorsConfirmed) {
    reportAdmin("ERR MOTORS_NOT_CONFIRMED use=Arm");
    return false;
  }
  if (!faultScanCompleted || faultScanActive) {
    reportAdmin("ERR DIAGNOSTICS_NOT_READY use=Prepare");
    return false;
  }
  if (faultDetected) {
    reportAdmin("ERR LD90_FAULT_PRESENT use=Prepare");
    return false;
  }
  if (motionKind != MOTION_NONE || cycleRunning || nextMacroPending) {
    reportAdmin("ERR AMR_BUSY active=%s", activeMotionName);
    return false;
  }
  if (requireHusky && !huskyOnline) {
    reportAdmin("ERR HUSKYLENS_REQUIRED action=Cycle");
    return false;
  }
  return true;
}

bool beginRoute(const char *name) {
  if (!motionAllowed(false)) return false;

  char command[96];
  snprintf(command, sizeof(command), "patrolOnce %s", name);
  if (!sendARCL(command)) return false;

  motionKind = MOTION_ROUTE;
  copyText(activeMotionName, sizeof(activeMotionName), name);
  motionStartedAt = millis();
  resetWaitState();
  reportAdmin("EVENT ROUTE_REQUESTED name=%s", name);
  return true;
}

bool beginMacro(const char *name, bool fromCycle) {
  if (!fromCycle && !motionAllowed(false)) return false;
  if (fromCycle) {
    if (!cycleRunning || !arclAuthenticated || !motorsConfirmed ||
        faultDetected || motionKind != MOTION_NONE) return false;
  }

  char command[96];
  snprintf(command, sizeof(command), "executeMacro %s", name);
  if (!sendARCL(command)) return false;

  motionKind = MOTION_MACRO;
  copyText(activeMotionName, sizeof(activeMotionName), name);
  arrivalRequired = false;
  copyText(activeArrivalLabel, sizeof(activeArrivalLabel), "NONE");
  motionStartedAt = millis();
  resetWaitState();
  reportAdmin("EVENT MACRO_REQUESTED name=%s cycle=%u",
              name, fromCycle ? 1 : 0);
  return true;
}

bool beginOrchestratedMacro(const char *name, const char *arrivalLabel) {
  if (!huskyOnline) {
    reportAdmin("ERR HUSKYLENS_REQUIRED action=%s", arrivalLabel);
    return false;
  }
  if (!beginMacro(name, false)) return false;
  arrivalRequired = true;
  copyText(activeArrivalLabel, sizeof(activeArrivalLabel), arrivalLabel);
  reportAdmin("EVENT ORCHESTRATED_LEG_REQUESTED leg=%s macro=%s",
              activeArrivalLabel, name);
  return true;
}

void startCycle() {
  if (!motionAllowed(true)) return;

  cycleStep = 0;
  manualSequenceStep = 0;
  cycleRunning = true;
  nextMacroPending = false;
  reportAdmin(
    "EVENT CYCLE_START sequence=ST1:FWD,ST2:REV,ST1:REV,ST3:FWD,ST2:REV,ST3:REV");

  if (!beginMacro(CYCLE_MACROS[cycleStep], true)) {
    clearProcessState();
    reportAdmin("ERR CYCLE_ABORT reason=FIRST_MACRO_REJECTED");
  }
}

ConveyorDirection directionForCurrentMacro() {
  const uint8_t step = cycleRunning ? cycleStep : manualSequenceStep;
  if (step >= CYCLE_COUNT) return CONVEYOR_STOPPED;
  if (!equalsIgnoreCase(activeMotionName, CYCLE_MACROS[step])) {
    reportAdmin("ERR SEQUENCE_MISMATCH expected=%s actual=%s step=%u",
                CYCLE_MACROS[step], activeMotionName,
                static_cast<unsigned int>(step + 1));
    return CONVEYOR_STOPPED;
  }
  return CYCLE_CONVEYOR[step];
}

void finishRoute() {
  char completed[sizeof(activeMotionName)];
  copyText(completed, sizeof(completed), activeMotionName);
  stopConveyor("ROUTE_COMPLETE");
  motionKind = MOTION_NONE;
  resetWaitState();
  copyText(activeMotionName, sizeof(activeMotionName), "NONE");
  reportAdmin("DONE ROUTE name=%s", completed);
}

void finishMacro() {
  char completed[sizeof(activeMotionName)];
  copyText(completed, sizeof(completed), activeMotionName);
  const bool wasCycle = cycleRunning;
  const bool mustReportArrival = arrivalRequired;
  char arrivalLabel[sizeof(activeArrivalLabel)];
  copyText(arrivalLabel, sizeof(arrivalLabel), activeArrivalLabel);
  const bool conveyorSucceeded = conveyorStartedThisWait;
  const bool waitWasSeen = waitSeenThisMotion;

  if (wasCycle && (!waitWasSeen || !conveyorSucceeded)) {
    abortProcess(!waitWasSeen ? "CYCLE_WAIT_NOT_SEEN" : "PRODUCT_NOT_DETECTED");
    return;
  }

  stopConveyor("MACRO_COMPLETE");
  motionKind = MOTION_NONE;
  resetWaitState();
  copyText(activeMotionName, sizeof(activeMotionName), "NONE");
  arrivalRequired = false;
  copyText(activeArrivalLabel, sizeof(activeArrivalLabel), "NONE");

  if (!wasCycle) {
    if (waitWasSeen && conveyorSucceeded) {
      manualSequenceStep = (manualSequenceStep + 1) % CYCLE_COUNT;
    }
    if (mustReportArrival) {
      // Server_admin_V3.py waits for the literal keyword "arrived".
      reportAdmin("ARRIVED leg=%s macro=%s", arrivalLabel, completed);
    } else {
      reportAdmin("DONE MACRO name=%s", completed);
    }
    return;
  }

  reportAdmin("EVENT CYCLE_STEP_COMPLETE step=%u/%u macro=%s",
              static_cast<unsigned int>(cycleStep + 1),
              static_cast<unsigned int>(CYCLE_COUNT), completed);
  cycleStep++;

  if (cycleStep >= CYCLE_COUNT) {
    cycleRunning = false;
    cycleStep = 0;
    reportAdmin("DONE CYCLE sequence_steps=%u",
                static_cast<unsigned int>(CYCLE_COUNT));
    return;
  }

  nextMacroPending = true;
  nextMacroAt = millis() + NEXT_MACRO_DELAY_MS;
}

void requestDiagnostics() {
  motorsConfirmed = false;
  faultDetected = false;
  faultScanActive = true;
  faultScanCompleted = false;

  if (!sendARCL("queryMotors")) return;
  sendARCL("oneLineStatus");
  sendARCL("getRoutes");
  sendARCL("getMacros");
  sendARCL("faultsGet");
  reportAdmin("EVENT DIAGNOSTICS_REQUESTED");
}

// ============================================================================
// LD-90 response parsing
// ============================================================================

bool isARCLCommandError(const char *line) {
  return startsWithIgnoreCase(line, "CommandError") ||
         startsWithIgnoreCase(line, "Unknown command") ||
         startsWithIgnoreCase(line, "Failed") ||
         startsWithIgnoreCase(line, "Cannot");
}

void beginMacroWait() {
  if (motionKind != MOTION_MACRO) {
    reportAdmin("EVENT ROUTE_WAIT_STARTED name=%s conveyor=DISABLED", activeMotionName);
    return;
  }

  waitSeenThisMotion = true;
  pendingAutoDirection = directionForCurrentMacro();
  conveyorStartedThisWait = false;
  huskyDetectionCount = 0;

  if (pendingAutoDirection == CONVEYOR_STOPPED) {
    abortProcess("CONVEYOR_SEQUENCE_MISMATCH");
    return;
  }
  if (!huskyOnline) {
    abortProcess("HUSKYLENS_OFFLINE_AT_WAIT");
    return;
  }

  reportAdmin("EVENT DOCK_WAIT_STARTED macro=%s husky_id=%u conveyor=PENDING",
              activeMotionName,
              static_cast<unsigned int>(PRODUCT_OBJECT_ID));
}

void finishWait() {
  if (!waitActive) return;
  waitActive = false;
  stopConveyor("WAIT_COMPLETE");

  if (motionKind == MOTION_MACRO &&
      pendingAutoDirection != CONVEYOR_STOPPED &&
      !conveyorStartedThisWait) {
    abortProcess("PRODUCT_NOT_DETECTED_BEFORE_WAIT_COMPLETE");
    return;
  }

  pendingAutoDirection = CONVEYOR_STOPPED;
  huskyDetectionCount = 0;
  reportAdmin("EVENT WAIT_COMPLETE name=%s", activeMotionName);
}

void handleLD90Line(char *line) {
  trimAscii(line);
  if (*line == '\0') return;

  Serial.print("ARCL_RX ");
  Serial.println(line);

  if (!arclAuthenticated) {
    if (containsIgnoreCase(line, "incorrect password") ||
        containsIgnoreCase(line, "invalid password")) {
      reportAdmin("ERR ARCL_AUTH_FAILED");
      ld90Client.stop();
      return;
    }

    // A successful login ends the ARCL command list with this line.
    if (equalsIgnoreCase(line, "End of commands")) {
      arclAuthenticated = true;
      reportAdmin("ONLINE LD90 ip=192.168.0.10 port=7171 ARCL=AUTHENTICATED");
      writeLine(ld90Client, "echo off");
      requestDiagnostics();
      lastLD90StatusQuery = millis();
    }
    return;
  }

  if (containsIgnoreCase(line, "motors enabled") ||
      containsIgnoreCase(line, "motors are enabled")) {
    motorsConfirmed = true;
    reportAdmin("EVENT MOTORS_READY");
  } else if (containsIgnoreCase(line, "motors disabled") ||
             containsIgnoreCase(line, "motors are disabled") ||
             (startsWithIgnoreCase(line, "Motors") &&
              containsIgnoreCase(line, "estop"))) {
    motorsConfirmed = false;
    stopConveyor("MOTORS_NOT_READY");
    reportAdmin("ERR SAFETY_STATE detail=\"%s\"", line);
  }

  if (startsWithIgnoreCase(line, "FaultList:")) {
    faultDetected = true;
    motorsConfirmed = false;
    reportAdmin("ERR LD90_FAULT detail=\"%s\"", line);
  } else if (equalsIgnoreCase(line, "End of FaultList")) {
    faultScanActive = false;
    faultScanCompleted = true;
    reportAdmin("EVENT FAULT_SCAN_COMPLETE faults=%u", faultDetected ? 1 : 0);
  }

  if (isARCLCommandError(line)) {
    if (motionKind != MOTION_NONE || cycleRunning) {
      abortProcess("ARCL_COMMAND_ERROR");
    }
    reportAdmin("ERR ARCL_COMMAND detail=\"%s\"", line);
    return;
  }

  if (startsWithIgnoreCase(line, "Executing macro ")) {
    reportAdmin("EVENT MACRO_RUNNING name=%s", activeMotionName);
    motionStartedAt = millis();
    return;
  }

  if (startsWithIgnoreCase(line, "WaitState: Waiting completed")) {
    finishWait();
    return;
  }

  if (startsWithIgnoreCase(line, "WaitState: Waiting interrupted") ||
      startsWithIgnoreCase(line, "WaitState: Waiting cancelled")) {
    if (stopRequested) {
      clearProcessState();
      reportAdmin("EVENT STOP_CONFIRMED");
    } else {
      abortProcess("WAIT_INTERRUPTED");
    }
    return;
  }

  if (startsWithIgnoreCase(line, "WaitState: Waiting") &&
      !containsIgnoreCase(line, "completed")) {
    if (!waitActive) {
      waitActive = true;
      beginMacroWait();
    }
    return;
  }

  if (motionKind == MOTION_MACRO &&
      (startsWithIgnoreCase(line, "Completed macro ") ||
       startsWithIgnoreCase(line, "Completed executing macro ") ||
       startsWithIgnoreCase(line, "Finished macro "))) {
    finishMacro();
    return;
  }

  if (startsWithIgnoreCase(line, "Patrolling route ") &&
      containsIgnoreCase(line, " once")) {
    reportAdmin("EVENT ROUTE_RUNNING name=%s", activeMotionName);
    motionStartedAt = millis();
    return;
  }

  if (motionKind == MOTION_ROUTE &&
      startsWithIgnoreCase(line, "Finished patrolling route ")) {
    finishRoute();
    return;
  }

  if (startsWithIgnoreCase(line, "Interrupted:")) {
    if (stopRequested) {
      clearProcessState();
      reportAdmin("EVENT STOP_CONFIRMED");
    } else if (motionKind != MOTION_NONE || cycleRunning) {
      abortProcess("MOTION_INTERRUPTED");
    }
    return;
  }

  if (equalsIgnoreCase(line, "Stopped") && stopRequested) {
    clearProcessState();
    reportAdmin("EVENT STOP_CONFIRMED");
  }
}

// ============================================================================
// Admin commands
// ============================================================================

void handleAdminCommand(char *command) {
  trimAscii(command);
  if (*command == '\0') return;

  Serial.print("ADMIN_RX ");
  Serial.println(command);

  if (equalsIgnoreCase(command, "prepare") ||
      equalsIgnoreCase(command, "diagnose")) {
    if (motionKind != MOTION_NONE || cycleRunning) {
      reportAdmin("ERR AMR_BUSY action=Prepare");
      return;
    }
    manualSequenceStep = 0;
    requestDiagnostics();
    return;
  }

  if (equalsIgnoreCase(command, "arm")) {
    if (!arclAuthenticated) {
      reportAdmin("ERR LD90_NOT_READY action=Arm");
      return;
    }
    if (faultDetected) {
      reportAdmin("ERR LD90_FAULT_PRESENT action=Arm use=Prepare");
      return;
    }
    if (!faultScanCompleted || faultScanActive) {
      reportAdmin("ERR DIAGNOSTICS_NOT_READY action=Arm use=Prepare");
      return;
    }
    motorsConfirmed = false;
    if (sendARCL("enableMotors")) {
      sendARCL("queryMotors");
      reportAdmin("EVENT ARM_REQUESTED");
    }
    return;
  }

  if (equalsIgnoreCase(command, "start") ||
      equalsIgnoreCase(command, "route1")) {
    beginRoute(ROUTE_ST1);
  } else if (equalsIgnoreCase(command, "route2")) {
    beginRoute(ROUTE_ST2);
  } else if (equalsIgnoreCase(command, "route3")) {
    beginRoute(ROUTE_ST3);
  } else if (equalsIgnoreCase(command, "macro1")) {
    beginMacro(MACRO_ST1, false);
  } else if (equalsIgnoreCase(command, "macro2")) {
    beginMacro(MACRO_ST2, false);
  } else if (equalsIgnoreCase(command, "macro3")) {
    beginMacro(MACRO_ST3, false);
  } else if (equalsIgnoreCase(command, "GotoUpperPickup")) {
    beginOrchestratedMacro(MACRO_ST1, "UPPER_PICKUP_AT_3ABB");
  } else if (equalsIgnoreCase(command, "GotoDropoffUpper")) {
    beginOrchestratedMacro(MACRO_ST2, "UPPER_DROPOFF_AT_4ABB");
  } else if (equalsIgnoreCase(command, "GotoUpperReturn")) {
    beginOrchestratedMacro(MACRO_ST1, "UPPER_RETURN_AT_3ABB");
  } else if (equalsIgnoreCase(command, "GotoLowerPickup")) {
    beginOrchestratedMacro(MACRO_ST3, "LOWER_PICKUP_AT_5ABB");
  } else if (equalsIgnoreCase(command, "GotoDropoffLower")) {
    beginOrchestratedMacro(MACRO_ST2, "LOWER_DROPOFF_AT_4ABB");
  } else if (equalsIgnoreCase(command, "GotoLowerReturn")) {
    beginOrchestratedMacro(MACRO_ST3, "LOWER_RETURN_AT_5ABB");
  } else if (equalsIgnoreCase(command, "cycle")) {
    startCycle();
  } else if (equalsIgnoreCase(command, "stop")) {
    stopConveyor("ADMIN_STOP");
    cycleRunning = false;
    nextMacroPending = false;
    manualSequenceStep = 0;
    stopRequested = true;
    if (!sendARCL("stop")) clearProcessState();
    else reportAdmin("EVENT STOP_REQUESTED");
  } else if (equalsIgnoreCase(command, "status")) {
    sendStatus("STATUS");
    if (arclAuthenticated) {
      sendARCL("oneLineStatus", false);
      sendARCL("queryMotors", false);
    }
  } else if (equalsIgnoreCase(command, "reset_sequence")) {
    if (motionKind != MOTION_NONE || cycleRunning) {
      reportAdmin("ERR AMR_BUSY action=ResetSequence");
    } else {
      manualSequenceStep = 0;
      reportAdmin("EVENT SEQUENCE_RESET next_step=1");
    }
  } else if (equalsIgnoreCase(command, "conveyor_forward") ||
             equalsIgnoreCase(command, "conveyor_reverse")) {
    if (motionKind != MOTION_NONE || cycleRunning) {
      reportAdmin("ERR AMR_BUSY action=ManualConveyor");
      return;
    }
    startConveyor(equalsIgnoreCase(command, "conveyor_forward")
                      ? CONVEYOR_FORWARD : CONVEYOR_REVERSE,
                  "ADMIN_TEST");
  } else if (equalsIgnoreCase(command, "conveyor_off")) {
    stopConveyor("ADMIN_COMMAND");
  } else if (startsWithIgnoreCase(command, "raw ")) {
    if (!ALLOW_RAW_ARCL) {
      reportAdmin("ERR RAW_ARCL_DISABLED");
    } else {
      sendARCL(command + 4);
    }
  } else {
    reportAdmin(
      "ERR UNKNOWN_COMMAND use=Prepare,Arm,Start,Stop,Status,Route1-3,Macro1-3,Cycle,GotoUpperPickup,GotoDropoffUpper,GotoUpperReturn,GotoLowerPickup,GotoDropoffLower,GotoLowerReturn,Reset_Sequence,Conveyor_Forward,Conveyor_Reverse,Conveyor_Off");
  }
}

// ============================================================================
// Wi-Fi and TCP connection management
// ============================================================================

void handleAdminLoss(const char *reason) {
  const bool wasOnline = adminOnline;
  adminClient.stop();
  adminOnline = false;
  adminLossPending = false;
  adminRxLength = 0;
  adminRxOverflow = false;

  stopConveyor("ADMIN_DISCONNECTED");
  if (STOP_MOTION_ON_ADMIN_LOSS &&
      ld90TcpOnline && arclAuthenticated && ld90Client.connected() &&
      (motionKind != MOTION_NONE || cycleRunning)) {
    writeLine(ld90Client, "stop");
    Serial.println("ARCL_TX stop (admin disconnected)");
  }
  clearProcessState();
  motorsConfirmed = false;
  manualSequenceStep = 0;

  if (wasOnline) {
    Serial.print("ERR ADMIN_DISCONNECTED reason=");
    Serial.println(reason);
  }
}

void handleLD90Loss(const char *reason) {
  const bool wasOnline = ld90TcpOnline;
  ld90Client.stop();
  ld90TcpOnline = false;
  arclAuthenticated = false;
  motorsConfirmed = false;
  faultDetected = false;
  faultScanActive = false;
  faultScanCompleted = false;
  ld90RxLength = 0;
  ld90RxOverflow = false;
  clearProcessState();

  if (wasOnline) reportAdmin("ERR LD90_DISCONNECTED reason=%s", reason);
}

void handleWiFiLoss() {
  const bool wasOnline = wifiOnline;
  handleAdminLoss("WIFI_DISCONNECTED");
  handleLD90Loss("WIFI_DISCONNECTED");
  wifiOnline = false;

  if (wasOnline) Serial.println("ERR WIFI_DISCONNECTED outputs=SAFE");
}

void beginWiFi() {
  lastWiFiAttempt = millis();
  WiFi.disconnect();
  delay(100);
  WiFi.config(ARDUINO_IP, DNS_IP, GATEWAY_IP, SUBNET_MASK);

  Serial.print("Connecting Wi-Fi: ");
  Serial.println(WIFI_SSID);
  if (WIFI_PASSWORD[0] == '\0') WiFi.begin(WIFI_SSID);
  else WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void maintainWiFi() {
  const unsigned long now = millis();

  if (wifiOnline) {
    if (now - lastWiFiCheck < WIFI_CHECK_MS) return;
    lastWiFiCheck = now;
    if (WiFi.status() == WL_CONNECTED && WiFi.localIP() == ARDUINO_IP) return;
    handleWiFiLoss();
  }

  if (WiFi.status() == WL_CONNECTED && WiFi.localIP() == ARDUINO_IP) {
    wifiOnline = true;
    lastWiFiCheck = now;
    lastAdminAttempt = now - ADMIN_RETRY_MS;
    lastLD90Attempt = now - LD90_RETRY_MS;
    const IPAddress ip = WiFi.localIP();
    Serial.print("ONLINE WIFI ip=");
    Serial.println(ip);
    return;
  }

  if (lastWiFiAttempt == 0 || now - lastWiFiAttempt >= WIFI_RETRY_MS) {
    beginWiFi();
  }
}

void attemptAdminConnection() {
  lastAdminAttempt = millis();
  adminClient.stop();
  adminClient.setConnectionTimeout(CONNECTION_TIMEOUT_MS);

  Serial.print("Connecting Admin ");
  Serial.print(ADMIN_SERVER_IP);
  Serial.print(':');
  Serial.println(ADMIN_SERVER_PORT);

  if (!adminClient.connect(ADMIN_SERVER_IP, ADMIN_SERVER_PORT)) return;

  adminOnline = true;
  adminLossPending = false;
  adminRxLength = 0;
  adminRxOverflow = false;
  lastHeartbeat = millis();

  // Server_admin_V2.py requires the device name as the first line.
  if (!writeLine(adminClient, ADMIN_CLIENT_NAME)) {
    handleAdminLoss("REGISTRATION_FAILED");
    return;
  }

  const IPAddress ip = WiFi.localIP();
  reportAdmin(
    "ONLINE device=amr firmware=%s wifi_ip=%u.%u.%u.%u admin=192.168.0.168:5000 start_action=ROUTE_ST1 orchestrator=V3_READY",
    FIRMWARE_VERSION, ip[0], ip[1], ip[2], ip[3]);
  sendStatus("STATUS");
}

void maintainAdminConnection() {
  if (!wifiOnline) return;

  if (adminLossPending) {
    handleAdminLoss("SEND_FAILED");
  }

  if (adminOnline && adminClient.connected()) return;
  if (adminOnline) handleAdminLoss("SOCKET_CLOSED");
  else adminClient.stop();

  if (millis() - lastAdminAttempt >= ADMIN_RETRY_MS) attemptAdminConnection();
}

void attemptLD90Connection() {
  lastLD90Attempt = millis();
  ld90Client.stop();
  ld90Client.setConnectionTimeout(CONNECTION_TIMEOUT_MS);

  Serial.print("Connecting LD-90 ");
  Serial.print(LD90_IP);
  Serial.print(':');
  Serial.println(LD90_ARCL_PORT);

  if (!ld90Client.connect(LD90_IP, LD90_ARCL_PORT)) return;

  ld90TcpOnline = true;
  arclAuthenticated = false;
  motorsConfirmed = false;
  ld90RxLength = 0;
  ld90RxOverflow = false;
  ld90ConnectedAt = millis();
  writeLine(ld90Client, ARCL_PASSWORD);
  reportAdmin("EVENT LD90_TCP_CONNECTED ip=192.168.0.10 port=7171");
  reportAdmin("STATUS ARCL=AUTHENTICATING");
}

void maintainLD90Connection() {
  if (!wifiOnline) return;

  if (ld90TcpOnline && !ld90Client.connected()) {
    handleLD90Loss("SOCKET_CLOSED");
  }

  if (!ld90TcpOnline) {
    if (millis() - lastLD90Attempt >= LD90_RETRY_MS) attemptLD90Connection();
    return;
  }

  if (!arclAuthenticated &&
      millis() - ld90ConnectedAt >= ARCL_LOGIN_TIMEOUT_MS) {
    reportAdmin("ERR ARCL_AUTH_TIMEOUT");
    handleLD90Loss("AUTH_TIMEOUT");
  }
}

// ============================================================================
// Line readers
// ============================================================================

void readAdminCommands() {
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
      if (adminRxLength + 1 < ADMIN_RX_CAPACITY) adminRx[adminRxLength++] = character;
      else adminRxOverflow = true;
    }
  }
}

void readLD90Lines() {
  while (ld90TcpOnline && ld90Client.connected() && ld90Client.available()) {
    const char character = static_cast<char>(ld90Client.read());
    if (character == '\n') {
      if (ld90RxOverflow) {
        reportAdmin("ERR LD90_LINE_TOO_LONG max=%u",
                    static_cast<unsigned int>(LD90_RX_CAPACITY - 1));
      } else {
        ld90Rx[ld90RxLength] = '\0';
        handleLD90Line(ld90Rx);
      }
      ld90RxLength = 0;
      ld90RxOverflow = false;
    } else if (character != '\r') {
      if (ld90RxLength + 1 < LD90_RX_CAPACITY) ld90Rx[ld90RxLength++] = character;
      else ld90RxOverflow = true;
    }
  }
}

// ============================================================================
// HUSKYLENS and timers
// ============================================================================

void markHuskyOffline(const char *reason) {
  if (huskyOnline) reportAdmin("ERR HUSKYLENS_OFFLINE reason=%s", reason);
  huskyOnline = false;
  huskyRequestFailures = 0;
  huskyDetectionCount = 0;

  if (waitActive && motionKind == MOTION_MACRO &&
      pendingAutoDirection != CONVEYOR_STOPPED &&
      !conveyorStartedThisWait) {
    abortProcess("HUSKYLENS_LOST_DURING_WAIT");
  }
}

void maintainHuskyLens() {
  const unsigned long now = millis();

  if (!huskyOnline) {
    if (lastHuskyAttempt != 0 && now - lastHuskyAttempt < HUSKY_RETRY_MS) return;
    lastHuskyAttempt = now;
    huskyOnline = huskylens.begin(Wire);
    if (huskyOnline) {
      huskyRequestFailures = 0;
      reportAdmin("EVENT HUSKYLENS_ONLINE protocol=I2C learned_id=%u",
                  static_cast<unsigned int>(PRODUCT_OBJECT_ID));
    } else {
      reportAdmin("STATUS HUSKYLENS=OFFLINE retry_ms=%lu", HUSKY_RETRY_MS);
    }
    return;
  }

  if (now - lastHuskyPoll < HUSKY_POLL_MS) return;
  lastHuskyPoll = now;

  if (!huskylens.request()) {
    huskyRequestFailures++;
    if (huskyRequestFailures >= HUSKY_MAX_REQUEST_FAILURES) {
      markHuskyOffline("REQUEST_FAILED");
    }
    return;
  }
  huskyRequestFailures = 0;

  bool productSeen = false;
  while (huskylens.available()) {
    HUSKYLENSResult result = huskylens.read();
    if (result.ID == PRODUCT_OBJECT_ID) productSeen = true;
  }

  if (!(motionKind == MOTION_MACRO && waitActive &&
        pendingAutoDirection != CONVEYOR_STOPPED &&
        !conveyorStartedThisWait)) {
    huskyDetectionCount = 0;
    return;
  }

  if (!productSeen) {
    huskyDetectionCount = 0;
    return;
  }

  if (huskyDetectionCount < HUSKY_CONFIRM_COUNT) huskyDetectionCount++;
  if (huskyDetectionCount < HUSKY_CONFIRM_COUNT) return;

  reportAdmin("EVENT PRODUCT_DETECTED husky_id=%u macro=%s",
              static_cast<unsigned int>(PRODUCT_OBJECT_ID), activeMotionName);
  if (startConveyor(pendingAutoDirection, "HUSKYLENS_PRODUCT")) {
    conveyorStartedThisWait = true;
  }
}

void updateTimedActions() {
  const unsigned long now = millis();

  if (conveyorRunning && now - conveyorStartedAt >= CONVEYOR_RUN_MS) {
    stopConveyor("WATCHDOG_TIMEOUT");
  }

  if (cycleRunning && nextMacroPending &&
      static_cast<long>(now - nextMacroAt) >= 0) {
    nextMacroPending = false;
    if (!beginMacro(CYCLE_MACROS[cycleStep], true)) {
      abortProcess("NEXT_MACRO_REJECTED");
    }
  }

  if (motionKind != MOTION_NONE &&
      now - motionStartedAt >= MOTION_TIMEOUT_MS) {
    abortProcess("MOTION_TIMEOUT");
  }

  if (adminOnline && now - lastHeartbeat >= HEARTBEAT_MS) {
    lastHeartbeat = now;
    sendStatus("HEARTBEAT");
  }

  if (arclAuthenticated && now - lastLD90StatusQuery >= LD90_STATUS_QUERY_MS) {
    lastLD90StatusQuery = now;
    sendARCL("oneLineStatus", false);
  }
}

// ============================================================================
// Arduino entry points
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(1200);

  pinMode(CONVEYOR_FORWARD_PIN, OUTPUT);
  pinMode(CONVEYOR_REVERSE_PIN, OUTPUT);
  writeConveyorInactive();
  Wire.begin();

  Serial.println("AMR_Arduino_V2 starting");
  Serial.print("FIRMWARE ");
  Serial.println(FIRMWARE_VERSION);
  Serial.println("Admin: 192.168.0.168:5000, device name: amr");
  Serial.println("LD-90: 192.168.0.10:7171, direct ARCL client mode");

  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("ERR WIFI_MODULE_NOT_FOUND");
  }

  beginWiFi();
}

void loop() {
  maintainWiFi();
  maintainAdminConnection();
  maintainLD90Connection();
  readAdminCommands();
  readLD90Lines();
  maintainHuskyLens();
  updateTimedActions();
}
