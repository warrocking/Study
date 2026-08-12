#ifndef AMR_IO_BRIDGE_USE_SERVER_AMR
#define AMR_IO_BRIDGE_USE_SERVER_AMR 1
#endif

#if AMR_IO_BRIDGE_USE_SERVER_AMR

#include <WiFiS3.h>

#include <ctype.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

/*
  Server_Amr.ino

  Target board: Arduino UNO R4 WiFi

  Network path:
    3abb (100.109.138.56) ---- Tailscale ----+
    5abb (100.114.77.47) ---- Tailscale -----+--> Server_admin.py
    4abb (100.102.179.115) --- Tailscale -----+    100.109.178.123 / TCP 5000
                                                ^
                                                | ROBOT_MA2_2G local Wi-Fi
                                                | 192.168.0.168 / TCP 5000
                                             Arduino (client name: amr)
                                                ^
                                                | LD-90 Outgoing ARCL / TCP 5353
                                                +---- LD-90

  The Tailscale addresses above are documentation only. UNO R4 WiFi does not
  run Tailscale, so it must connect to the admin laptop's ROBOT_MA2_2G address.

  Broadcast behavior:
    Server_admin.py sends "all Start" to every registered connection. This
    Arduino receives the line "Start" and maps it to "patrolOnce 경로1".

  Safety:
    - D7 controls an isolated conveyor relay/driver input. Never drive a motor
      directly from an Arduino GPIO pin.
    - ARCL "stop" is an ordinary process stop. It is not an E-Stop.
    - Configure LD-90 Outgoing ARCL > RequireConnectionToPathPlan as required
      by the project's safety assessment.
*/

// ============================================================================
// User configuration
// ============================================================================

// The currently observed SSID is ROBOT_MA2_2G and it is an open network.
// Add the real password if the access point is secured later.
const char WIFI_SSID[] = "ROBOT_MA2_2G";
const char WIFI_PASSWORD[] = "";

// The Arduino cannot normally reach the laptop's 100.109.178.123 Tailscale
// address. Reserve this LAN address for the admin laptop in the MA2 router.
IPAddress ADMIN_SERVER_IP(192, 168, 0, 168);
const uint16_t ADMIN_SERVER_PORT = 5000;
const char ADMIN_CLIENT_NAME[] = "amr";

// LD-90 MobilePlanner > Outgoing ARCL connection setup must point to the
// Arduino's reserved Wi-Fi address and this port.
const uint16_t ARCL_PORT = 5353;

// These names must exactly match the active LD-90 map.
const char ROUTE_1[] = "경로1";
const char ROUTE_2[] = "경로2";
const char ROUTE_3[] = "경로3";
const char MACRO_1[] = "MACRO_ST1";
const char MACRO_2[] = "MACRO_ST2";
const char MACRO_3[] = "MACRO_ST3";

// "Start" and therefore "all Start" execute this route once.
const char START_ROUTE[] = "경로1";

// Arduino -> isolated relay/driver -> AMR top conveyor controller.
const uint8_t CONVEYOR_PIN = 7;
const uint8_t CONVEYOR_ACTIVE_LEVEL = HIGH;
const uint8_t CONVEYOR_INACTIVE_LEVEL =
    (CONVEYOR_ACTIVE_LEVEL == HIGH) ? LOW : HIGH;

// The AMR macro is expected to contain one intentional wait(5) after
// PrecisionDrive. Other waits do not start the conveyor.
const char CONVEYOR_WAIT_PREFIX[] = "WaitState: Waiting 5 seconds";
const unsigned long CONVEYOR_MAX_ON_MS = 7000;
const unsigned long CONVEYOR_TEST_MS = 1000;

// Keep raw ARCL disabled during normal operation. Explicit getRoutes/getMacros
// diagnostic commands remain available.
const bool ALLOW_RAW_ARCL = false;
const bool STOP_AMR_ON_ADMIN_LOSS = true;

const unsigned long WIFI_RETRY_INTERVAL_MS = 10000;
const unsigned long WIFI_STATUS_CHECK_MS = 1000;
const unsigned long WIFI_CONNECT_TIMEOUT_MS = 5000;
const unsigned long ADMIN_RETRY_INTERVAL_MS = 2000;
const int ADMIN_CONNECT_TIMEOUT_MS = 1200;
const unsigned long HEARTBEAT_INTERVAL_MS = 30000;
const unsigned long AMR_STATUS_QUERY_INTERVAL_MS = 15000;
const unsigned long COMMAND_LED_MS = 500;

// ============================================================================
// Runtime state
// ============================================================================

WiFiServer arclServer(ARCL_PORT);
WiFiClient adminClient;
WiFiClient amrClient;

bool wifiConnected = false;
bool adminConnected = false;
bool amrConnected = false;

bool conveyorRunning = false;
unsigned long conveyorStartedAt = 0;
unsigned long conveyorLimitMs = 0;

bool commandLedActive = false;
unsigned long commandLedStartedAt = 0;

bool motionActive = false;
bool macroRunning = false;
char activeMotion[48] = "NONE";

unsigned long lastWiFiAttempt = 0;
unsigned long lastWiFiStatusCheck = 0;
unsigned long lastAdminAttempt = 0;
unsigned long lastHeartbeat = 0;
unsigned long lastAmrStatusQuery = 0;

const size_t ADMIN_RX_CAPACITY = 192;
char adminRx[ADMIN_RX_CAPACITY];
size_t adminRxLength = 0;
bool adminRxOverflow = false;

const size_t AMR_RX_CAPACITY = 640;
char amrRx[AMR_RX_CAPACITY];
size_t amrRxLength = 0;
bool amrRxOverflow = false;

// ============================================================================
// Forward declarations
// ============================================================================

void maintainWiFi();
void maintainAdminConnection();
void maintainAmrConnection();
void readAdminCommands();
void readAmrResponses();
void updateConveyorWatchdog();
void updateCommandLed();
void sendHeartbeatIfDue();
void queryAmrStatusIfDue();
void sendBridgeStatus(const char *prefix);
void handleAdminCommand(char *command);
void handleAmrLine(char *line);
bool writeLine(WiFiClient &client, const char *text);

// ============================================================================
// Small text helpers
// ============================================================================

void trimAsciiWhitespace(char *text)
{
  char *start = text;
  while (*start != '\0' && isspace(static_cast<unsigned char>(*start)))
  {
    ++start;
  }

  if (start != text)
  {
    memmove(text, start, strlen(start) + 1);
  }

  size_t length = strlen(text);
  while (length > 0 && isspace(static_cast<unsigned char>(text[length - 1])))
  {
    text[--length] = '\0';
  }
}

bool equalsIgnoreCaseAscii(const char *left, const char *right)
{
  while (*left != '\0' && *right != '\0')
  {
    if (tolower(static_cast<unsigned char>(*left)) !=
        tolower(static_cast<unsigned char>(*right)))
    {
      return false;
    }
    ++left;
    ++right;
  }
  return *left == '\0' && *right == '\0';
}

bool startsWith(const char *text, const char *prefix)
{
  return strncmp(text, prefix, strlen(prefix)) == 0;
}

bool startsWithIgnoreCaseAscii(const char *text, const char *prefix)
{
  while (*prefix != '\0')
  {
    if (*text == '\0' ||
        tolower(static_cast<unsigned char>(*text)) !=
            tolower(static_cast<unsigned char>(*prefix)))
    {
      return false;
    }
    ++text;
    ++prefix;
  }
  return true;
}

bool containsIgnoreCaseAscii(const char *text, const char *needle)
{
  if (*needle == '\0')
  {
    return true;
  }

  for (const char *candidate = text; *candidate != '\0'; ++candidate)
  {
    if (startsWithIgnoreCaseAscii(candidate, needle))
    {
      return true;
    }
  }
  return false;
}

void copyText(char *destination, size_t capacity, const char *source)
{
  if (capacity == 0)
  {
    return;
  }
  strncpy(destination, source, capacity - 1);
  destination[capacity - 1] = '\0';
}

// ============================================================================
// TCP line writers and reporting
// ============================================================================

bool writeLine(WiFiClient &client, const char *text)
{
  if (!client || !client.connected())
  {
    return false;
  }

  const size_t textLength = strlen(text);
  const uint8_t newline = '\n';
  const size_t textWritten =
      client.write(reinterpret_cast<const uint8_t *>(text), textLength);
  const size_t newlineWritten = client.write(&newline, 1);
  return textWritten == textLength && newlineWritten == 1;
}

void stopAmrWithoutReport()
{
  if (amrConnected && amrClient.connected())
  {
    writeLine(amrClient, "stop");
  }
}

void forceConveyorOff(const char *reason)
{
  digitalWrite(CONVEYOR_PIN, CONVEYOR_INACTIVE_LEVEL);
  if (!conveyorRunning)
  {
    return;
  }

  conveyorRunning = false;
  conveyorStartedAt = 0;
  conveyorLimitMs = 0;

  Serial.print("CONVEYOR OFF reason=");
  Serial.println(reason);

  if (adminConnected && adminClient.connected())
  {
    char message[128];
    snprintf(message, sizeof(message), "EVENT CONVEYOR_OFF reason=%s", reason);
    writeLine(adminClient, message);
  }
}

void handleAdminLoss(const char *reason)
{
  const bool wasConnected = adminConnected;

  adminClient.stop();
  adminConnected = false;
  adminRxLength = 0;
  adminRxOverflow = false;

  if (!wasConnected)
  {
    return;
  }

  forceConveyorOff("ADMIN_DISCONNECTED");
  digitalWrite(LED_BUILTIN, LOW);
  commandLedActive = false;

  if (STOP_AMR_ON_ADMIN_LOSS)
  {
    stopAmrWithoutReport();
    motionActive = false;
    macroRunning = false;
    copyText(activeMotion, sizeof(activeMotion), "NONE");
  }

  Serial.print("Admin disconnected: ");
  Serial.println(reason);
}

bool writeAdminLine(const char *text)
{
  if (!adminConnected || !writeLine(adminClient, text))
  {
    if (adminConnected)
    {
      handleAdminLoss("WRITE_FAILED");
    }
    return false;
  }

  Serial.print("Admin < ");
  Serial.println(text);
  return true;
}

bool reportAdmin(const char *format, ...)
{
  char message[256];
  va_list arguments;
  va_start(arguments, format);
  vsnprintf(message, sizeof(message), format, arguments);
  va_end(arguments);
  message[sizeof(message) - 1] = '\0';

  Serial.println(message);
  return writeAdminLine(message);
}

bool sendArclCommand(const char *command)
{
  if (!amrConnected || !amrClient.connected())
  {
    reportAdmin("ERR LD90_DISCONNECTED command=%s", command);
    return false;
  }

  if (!writeLine(amrClient, command))
  {
    reportAdmin("ERR ARCL_WRITE_FAILED command=%s", command);
    amrClient.stop();
    return false;
  }

  Serial.print("Arduino > LD90: ");
  Serial.println(command);
  reportAdmin("EVENT ARCL_SENT command=%s", command);
  return true;
}

// ============================================================================
// Safe local output handling
// ============================================================================

void startConveyor(unsigned long maximumOnMs, const char *reason)
{
  // A repeated ARCL status line must not extend an already-running conveyor
  // watchdog. Only the first matching wait event starts the timer.
  if (conveyorRunning)
  {
    reportAdmin("EVENT CONVEYOR_START_IGNORED reason=ALREADY_RUNNING");
    return;
  }

  digitalWrite(CONVEYOR_PIN, CONVEYOR_ACTIVE_LEVEL);
  conveyorRunning = true;
  conveyorStartedAt = millis();
  conveyorLimitMs = maximumOnMs;
  reportAdmin("EVENT CONVEYOR_ON reason=%s max_ms=%lu", reason, maximumOnMs);
}

void updateConveyorWatchdog()
{
  if (!conveyorRunning)
  {
    return;
  }

  if (millis() - conveyorStartedAt >= conveyorLimitMs)
  {
    const unsigned long expiredLimitMs = conveyorLimitMs;
    forceConveyorOff("WATCHDOG_TIMEOUT");
    reportAdmin("ERR CONVEYOR_TIMEOUT max_ms=%lu", expiredLimitMs);
  }
}

void pulseCommandLed()
{
  digitalWrite(LED_BUILTIN, HIGH);
  commandLedActive = true;
  commandLedStartedAt = millis();
}

void updateCommandLed()
{
  if (commandLedActive && millis() - commandLedStartedAt >= COMMAND_LED_MS)
  {
    digitalWrite(LED_BUILTIN, LOW);
    commandLedActive = false;
  }
}

// ============================================================================
// Motion command helpers
// ============================================================================

bool beginMotion(const char *arclCommand, const char *motionName)
{
  if (motionActive)
  {
    reportAdmin("ERR MOTION_BUSY active=%s", activeMotion);
    return false;
  }

  if (!sendArclCommand(arclCommand) || !adminConnected)
  {
    return false;
  }

  motionActive = true;
  copyText(activeMotion, sizeof(activeMotion), motionName);
  pulseCommandLed();
  reportAdmin("ACK MOTION_STARTED name=%s", motionName);
  return true;
}

void beginRoute(const char *routeName, const char *motionName)
{
  char command[160];
  snprintf(command, sizeof(command), "patrolOnce %s", routeName);
  beginMotion(command, motionName);
}

void beginMacro(const char *macroName)
{
  char command[160];
  snprintf(command, sizeof(command), "executeMacro %s", macroName);
  if (beginMotion(command, macroName))
  {
    macroRunning = true;
  }
}

void stopProcess(const char *source)
{
  forceConveyorOff(source);
  digitalWrite(LED_BUILTIN, LOW);
  commandLedActive = false;
  motionActive = false;
  macroRunning = false;
  copyText(activeMotion, sizeof(activeMotion), "NONE");

  if (sendArclCommand("stop"))
  {
    reportAdmin("ACK STOP source=%s", source);
  }
}

// ============================================================================
// Wi-Fi and admin connection management
// ============================================================================

void handleWiFiLoss()
{
  const bool hadWiFi = wifiConnected;

  forceConveyorOff("WIFI_DISCONNECTED");
  digitalWrite(LED_BUILTIN, LOW);
  commandLedActive = false;
  motionActive = false;
  macroRunning = false;
  copyText(activeMotion, sizeof(activeMotion), "NONE");

  adminClient.stop();
  amrClient.stop();
  adminConnected = false;
  amrConnected = false;
  wifiConnected = false;
  adminRxLength = 0;
  adminRxOverflow = false;
  amrRxLength = 0;
  amrRxOverflow = false;

  if (hadWiFi)
  {
    Serial.println("Wi-Fi disconnected; outputs forced safe");
  }
}

void attemptWiFiConnection()
{
  lastWiFiAttempt = millis();

  if (WiFi.status() == WL_NO_MODULE)
  {
    Serial.println("UNO R4 WiFi module not found; retrying later");
    return;
  }

  Serial.print("Connecting Wi-Fi: ");
  Serial.println(WIFI_SSID);

  WiFi.disconnect();
  int result;
  if (WIFI_PASSWORD[0] == '\0')
  {
    result = WiFi.begin(WIFI_SSID);
  }
  else
  {
    result = WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  }

  wifiConnected = (result == WL_CONNECTED || WiFi.status() == WL_CONNECTED);
  lastWiFiStatusCheck = millis();

  if (!wifiConnected)
  {
    Serial.println("Wi-Fi unavailable; bridge will keep waiting");
    return;
  }

  arclServer.begin();
  lastAdminAttempt = millis() - ADMIN_RETRY_INTERVAL_MS;

  Serial.print("Wi-Fi online. Arduino IP: ");
  Serial.println(WiFi.localIP());
  Serial.print("Waiting for LD-90 Outgoing ARCL on port ");
  Serial.println(ARCL_PORT);
}

void maintainWiFi()
{
  const unsigned long now = millis();

  if (wifiConnected)
  {
    if (now - lastWiFiStatusCheck < WIFI_STATUS_CHECK_MS)
    {
      return;
    }

    lastWiFiStatusCheck = now;
    if (WiFi.status() == WL_CONNECTED)
    {
      return;
    }

    handleWiFiLoss();
  }

  if (now - lastWiFiAttempt >= WIFI_RETRY_INTERVAL_MS)
  {
    attemptWiFiConnection();
  }
}

void attemptAdminConnection()
{
  lastAdminAttempt = millis();
  adminClient.stop();
  adminClient.setConnectionTimeout(ADMIN_CONNECT_TIMEOUT_MS);

  Serial.print("Connecting admin: ");
  Serial.print(ADMIN_SERVER_IP);
  Serial.print(':');
  Serial.println(ADMIN_SERVER_PORT);

  if (!adminClient.connect(ADMIN_SERVER_IP, ADMIN_SERVER_PORT))
  {
    Serial.println("Admin unavailable; bridge will keep waiting");
    return;
  }

  adminConnected = true;
  adminRxLength = 0;
  adminRxOverflow = false;
  lastHeartbeat = millis();

  // Server_admin.py requires this to be the first received line.
  if (!writeAdminLine(ADMIN_CLIENT_NAME))
  {
    return;
  }

  const IPAddress localIP = WiFi.localIP();
  reportAdmin(
      "ONLINE device=%s wifi_ip=%u.%u.%u.%u arcl_port=%u start_action=ROUTE1",
      ADMIN_CLIENT_NAME,
      localIP[0],
      localIP[1],
      localIP[2],
      localIP[3],
      ARCL_PORT);
  sendBridgeStatus("STATUS");
}

void maintainAdminConnection()
{
  if (!wifiConnected)
  {
    return;
  }

  if (adminConnected && adminClient.connected())
  {
    return;
  }

  if (adminConnected)
  {
    handleAdminLoss("SOCKET_CLOSED");
  }
  else
  {
    adminClient.stop();
  }

  if (millis() - lastAdminAttempt >= ADMIN_RETRY_INTERVAL_MS)
  {
    attemptAdminConnection();
  }
}

// ============================================================================
// LD-90 Outgoing ARCL connection and responses
// ============================================================================

void handleAmrLoss(const char *reason)
{
  const bool wasConnected = amrConnected;

  amrClient.stop();
  amrConnected = false;
  amrRxLength = 0;
  amrRxOverflow = false;
  forceConveyorOff("LD90_DISCONNECTED");
  motionActive = false;
  macroRunning = false;
  copyText(activeMotion, sizeof(activeMotion), "NONE");

  if (wasConnected)
  {
    reportAdmin("EVENT LD90_OFFLINE reason=%s", reason);
  }
}

void acceptAmrConnection()
{
  WiFiClient incoming = arclServer.available();
  if (!incoming)
  {
    return;
  }

  if (amrConnected)
  {
    handleAmrLoss("REPLACED_BY_NEW_CONNECTION");
  }

  amrClient = incoming;
  amrConnected = true;
  amrRxLength = 0;
  amrRxOverflow = false;
  motionActive = false;
  macroRunning = false;
  copyText(activeMotion, sizeof(activeMotion), "NONE");
  forceConveyorOff("LD90_NEW_CONNECTION");

  reportAdmin("EVENT LD90_ONLINE arcl_port=%u", ARCL_PORT);
  writeLine(amrClient, "echo off");
  writeLine(amrClient, "oneLineStatus");
  lastAmrStatusQuery = millis();
}

void maintainAmrConnection()
{
  if (!wifiConnected)
  {
    return;
  }

  if (amrConnected && !amrClient.connected())
  {
    handleAmrLoss("SOCKET_CLOSED");
  }

  if (!amrConnected)
  {
    acceptAmrConnection();
  }
}

void clearMotionState()
{
  motionActive = false;
  macroRunning = false;
  copyText(activeMotion, sizeof(activeMotion), "NONE");
}

void handleAmrLine(char *line)
{
  trimAsciiWhitespace(line);
  if (line[0] == '\0')
  {
    return;
  }

  Serial.print("LD90 > Arduino: ");
  Serial.println(line);
  reportAdmin("LD90 %s", line);

  if (startsWith(line, "Executing macro "))
  {
    macroRunning = true;
    motionActive = true;
    copyText(activeMotion, sizeof(activeMotion), line + strlen("Executing macro "));
  }
  else if (macroRunning && startsWith(line, CONVEYOR_WAIT_PREFIX) &&
           strstr(line, "completed") == nullptr)
  {
    startConveyor(CONVEYOR_MAX_ON_MS, "MACRO_WAIT_5_SECONDS");
  }
  else if (conveyorRunning && strstr(line, "WaitState: Waiting completed") != nullptr)
  {
    forceConveyorOff("MACRO_WAIT_COMPLETED");
  }
  else if (startsWith(line, "Completed macro "))
  {
    forceConveyorOff("MACRO_COMPLETED");
    clearMotionState();
    reportAdmin("EVENT MACRO_COMPLETED");
  }
  else if (startsWith(line, "Patrolling route "))
  {
    motionActive = true;
  }
  else if (startsWith(line, "Finished patrolling route "))
  {
    clearMotionState();
    reportAdmin("EVENT ROUTE_COMPLETED");
  }
  else if (containsIgnoreCaseAscii(line, "failed") ||
           containsIgnoreCaseAscii(line, "error") ||
           containsIgnoreCaseAscii(line, "interrupted") ||
           containsIgnoreCaseAscii(line, "unknown") ||
           containsIgnoreCaseAscii(line, "cannot") ||
           containsIgnoreCaseAscii(line, "could not") ||
           containsIgnoreCaseAscii(line, "invalid") ||
           equalsIgnoreCaseAscii(line, "stopped"))
  {
    forceConveyorOff("LD90_ERROR_OR_STOP");
    clearMotionState();
    reportAdmin("EVENT MOTION_CLEARED_BY_LD90_RESPONSE");
  }
}

void finishAmrLine()
{
  if (amrRxOverflow)
  {
    reportAdmin("ERR LD90_LINE_TOO_LONG max_bytes=%u", AMR_RX_CAPACITY - 1);
  }
  else
  {
    amrRx[amrRxLength] = '\0';
    handleAmrLine(amrRx);
  }

  amrRxLength = 0;
  amrRxOverflow = false;
}

void readAmrResponses()
{
  if (!amrConnected || !amrClient.connected())
  {
    return;
  }

  size_t processedBytes = 0;
  while (amrClient.available() && processedBytes < 768)
  {
    const int value = amrClient.read();
    if (value < 0)
    {
      break;
    }

    ++processedBytes;
    const char c = static_cast<char>(value);
    if (c == '\n')
    {
      finishAmrLine();
    }
    else if (c != '\r' && !amrRxOverflow)
    {
      if (amrRxLength < AMR_RX_CAPACITY - 1)
      {
        amrRx[amrRxLength++] = c;
      }
      else
      {
        amrRxOverflow = true;
      }
    }
  }
}

// ============================================================================
// Admin line protocol and commands
// ============================================================================

void handleAdminCommand(char *command)
{
  trimAsciiWhitespace(command);
  if (command[0] == '\0')
  {
    return;
  }

  Serial.print("Admin > ");
  Serial.println(command);

  if (equalsIgnoreCaseAscii(command, "START"))
  {
    beginRoute(START_ROUTE, "START_ROUTE1");
  }
  else if (equalsIgnoreCaseAscii(command, "ROUTE1") ||
           equalsIgnoreCaseAscii(command, "MOVE_ST1"))
  {
    beginRoute(ROUTE_1, "ROUTE1");
  }
  else if (equalsIgnoreCaseAscii(command, "ROUTE2") ||
           equalsIgnoreCaseAscii(command, "MOVE_ST2"))
  {
    beginRoute(ROUTE_2, "ROUTE2");
  }
  else if (equalsIgnoreCaseAscii(command, "ROUTE3") ||
           equalsIgnoreCaseAscii(command, "MOVE_ST3"))
  {
    beginRoute(ROUTE_3, "ROUTE3");
  }
  else if (equalsIgnoreCaseAscii(command, "MACRO1"))
  {
    beginMacro(MACRO_1);
  }
  else if (equalsIgnoreCaseAscii(command, "MACRO2"))
  {
    beginMacro(MACRO_2);
  }
  else if (equalsIgnoreCaseAscii(command, "MACRO3"))
  {
    beginMacro(MACRO_3);
  }
  else if (equalsIgnoreCaseAscii(command, "STOP") ||
           equalsIgnoreCaseAscii(command, "END") ||
           equalsIgnoreCaseAscii(command, "ALL_OFF"))
  {
    stopProcess("ADMIN_COMMAND");
  }
  else if (equalsIgnoreCaseAscii(command, "STATUS"))
  {
    sendBridgeStatus("STATUS");
    if (amrConnected)
    {
      sendArclCommand("oneLineStatus");
    }
  }
  else if (equalsIgnoreCaseAscii(command, "PING"))
  {
    reportAdmin("PONG uptime_ms=%lu", millis());
  }
  else if (equalsIgnoreCaseAscii(command, "GET_ROUTES"))
  {
    sendArclCommand("getRoutes");
  }
  else if (equalsIgnoreCaseAscii(command, "GET_MACROS"))
  {
    sendArclCommand("getMacros");
  }
  else if (equalsIgnoreCaseAscii(command, "CONVEYOR_TEST"))
  {
    if (!conveyorRunning)
    {
      startConveyor(CONVEYOR_TEST_MS, "ADMIN_TEST");
    }
    else
    {
      reportAdmin("ERR CONVEYOR_ALREADY_RUNNING");
    }
  }
  else if (equalsIgnoreCaseAscii(command, "CONVEYOR_OFF"))
  {
    forceConveyorOff("ADMIN_COMMAND");
    reportAdmin("ACK CONVEYOR_OFF");
  }
  else if (startsWithIgnoreCaseAscii(command, "RAW "))
  {
    if (ALLOW_RAW_ARCL)
    {
      sendArclCommand(command + 4);
    }
    else
    {
      reportAdmin("ERR RAW_ARCL_DISABLED");
    }
  }
  else if (equalsIgnoreCaseAscii(command, "HELP"))
  {
    reportAdmin(
        "HELP START|ROUTE1|ROUTE2|ROUTE3|MACRO1|MACRO2|MACRO3|STOP|STATUS|PING|GET_ROUTES|GET_MACROS|CONVEYOR_TEST|CONVEYOR_OFF");
  }
  else
  {
    reportAdmin("ERR UNKNOWN_COMMAND value=%s", command);
  }
}

void finishAdminLine()
{
  if (adminRxOverflow)
  {
    reportAdmin("ERR COMMAND_TOO_LONG max_bytes=%u", ADMIN_RX_CAPACITY - 1);
  }
  else
  {
    adminRx[adminRxLength] = '\0';
    handleAdminCommand(adminRx);
  }

  adminRxLength = 0;
  adminRxOverflow = false;
}

void readAdminCommands()
{
  if (!adminConnected || !adminClient.connected())
  {
    return;
  }

  size_t processedBytes = 0;
  while (adminClient.available() && processedBytes < 256)
  {
    const int value = adminClient.read();
    if (value < 0)
    {
      break;
    }

    ++processedBytes;
    const char c = static_cast<char>(value);
    if (c == '\n')
    {
      finishAdminLine();
    }
    else if (c != '\r' && !adminRxOverflow)
    {
      if (adminRxLength < ADMIN_RX_CAPACITY - 1)
      {
        adminRx[adminRxLength++] = c;
      }
      else
      {
        adminRxOverflow = true;
      }
    }
  }
}

// ============================================================================
// Status and main loop
// ============================================================================

void sendBridgeStatus(const char *prefix)
{
  reportAdmin(
      "%s WIFI=%s ADMIN=%s LD90=%s MOTION=%s MACRO=%d CONVEYOR=%d uptime_ms=%lu rssi_dbm=%ld",
      prefix,
      wifiConnected ? "CONNECTED" : "DISCONNECTED",
      adminConnected ? "CONNECTED" : "DISCONNECTED",
      amrConnected ? "CONNECTED" : "DISCONNECTED",
      activeMotion,
      macroRunning ? 1 : 0,
      conveyorRunning ? 1 : 0,
      millis(),
      wifiConnected ? static_cast<long>(WiFi.RSSI()) : 0L);
}

void sendHeartbeatIfDue()
{
  if (adminConnected &&
      millis() - lastHeartbeat >= HEARTBEAT_INTERVAL_MS)
  {
    lastHeartbeat = millis();
    sendBridgeStatus("HEARTBEAT");
  }
}

void queryAmrStatusIfDue()
{
  if (amrConnected &&
      millis() - lastAmrStatusQuery >= AMR_STATUS_QUERY_INTERVAL_MS)
  {
    lastAmrStatusQuery = millis();
    writeLine(amrClient, "oneLineStatus");
  }
}

void setup()
{
  pinMode(CONVEYOR_PIN, OUTPUT);
  digitalWrite(CONVEYOR_PIN, CONVEYOR_INACTIVE_LEVEL);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  Serial.begin(115200);
  delay(1200);
  Serial.println();
  Serial.println("Server_Amr bridge starting");
  Serial.println("Waiting indefinitely for Wi-Fi, admin server, and LD-90");

  WiFi.setHostname("server-amr");
  WiFi.setTimeout(WIFI_CONNECT_TIMEOUT_MS);
  adminClient.setConnectionTimeout(ADMIN_CONNECT_TIMEOUT_MS);

  lastWiFiAttempt = millis() - WIFI_RETRY_INTERVAL_MS;
  lastAdminAttempt = millis() - ADMIN_RETRY_INTERVAL_MS;
}

void loop()
{
  // Service safety timers and existing sockets before bounded reconnect work.
  updateConveyorWatchdog();
  updateCommandLed();
  maintainAmrConnection();
  readAdminCommands();
  readAmrResponses();

  maintainWiFi();
  maintainAdminConnection();
  maintainAmrConnection();

  queryAmrStatusIfDue();
  sendHeartbeatIfDue();
}

#endif // AMR_IO_BRIDGE_USE_SERVER_AMR
