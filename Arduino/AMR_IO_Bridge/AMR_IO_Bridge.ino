// Arduino compiles every .ino file in this folder as one sketch. Keep the
// previous digital-I/O bridge available, but select Server_Amr.ino by default.
// Change this value to 0 only when rebuilding the previous bridge.
#define AMR_IO_BRIDGE_USE_SERVER_AMR 1

#include <WiFiS3.h>

#if !AMR_IO_BRIDGE_USE_SERVER_AMR

#include <ctype.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

/*
  AMR_IO_Bridge.ino

  Target board: Arduino UNO R4 WiFi

  Role:
    1) Connect to TestServer_admin.py as the TCP client named "AMR1".
    2) Receive newline-delimited commands from the admin server.
    3) Convert route/stop commands into short digital-output pulses.
    4) Read isolated LD-90 feedback signals and report changes to the server.

  IMPORTANT:
    - Arduino GPIO must NOT be connected directly to the LD-90 industrial I/O.
      Use correctly wired relay contacts, optocouplers, or an industrial I/O
      interface matched to the LD-90 input bank's NPN/PNP configuration.
    - STOP below is an ordinary process stop request. It is NOT an E-Stop and
      must never replace the LD-90 safety circuit or physical E-Stop.
    - The LD-90 must already be configured in MobilePlanner so each digital
      input starts the intended route/macro or performs the stop request.
*/

// ============================================================================
// User configuration
// ============================================================================

// ROBOT3_2G is currently an open network. Set a password here if one is added.
const char WIFI_SSID[] = "ROBOT3_2G";
const char WIFI_PASSWORD[] = "";

// This PC is currently 192.168.3.91 on ROBOT3_2G and TestServer_admin.py
// listens on 0.0.0.0:5000. Use the PC's Wi-Fi/LAN address here, not its
// Tailscale 100.x address, unless a separate subnet router provides that route.
IPAddress ADMIN_SERVER_IP(192, 168, 3, 91);
const uint16_t ADMIN_SERVER_PORT = 5000;
const char RELAY_NAME[] = "AMR1";

// Arduino -> isolated interface -> LD-90 DIGITAL INPUT
// Change these pins only after matching them to the completed AMR wiring.
const uint8_t PIN_ROUTE_1 = 2;
const uint8_t PIN_ROUTE_2 = 3;
const uint8_t PIN_ROUTE_3 = 4;
const uint8_t PIN_STOP_REQUEST = 5;

// LD-90 DIGITAL OUTPUT -> isolated interface -> Arduino
// Unconnected inputs remain inactive because INPUT_PULLUP is used by default.
const uint8_t PIN_FEEDBACK_READY = 6;
const uint8_t PIN_FEEDBACK_BUSY = 7;
const uint8_t PIN_FEEDBACK_DONE = 8;
const uint8_t PIN_FEEDBACK_FAULT = 9;

// Set LOW if the selected relay/opto input module is active-low.
const uint8_t COMMAND_ACTIVE_LEVEL = HIGH;
const uint8_t COMMAND_INACTIVE_LEVEL =
    (COMMAND_ACTIVE_LEVEL == HIGH) ? LOW : HIGH;

// Default feedback wiring assumes a dry contact/open-collector pulls the pin
// to GND when active. Change both values if the actual interface is different.
const uint8_t FEEDBACK_PIN_MODE = INPUT_PULLUP;
const uint8_t FEEDBACK_ACTIVE_LEVEL = LOW;

const unsigned long COMMAND_PULSE_MS = 300;
const unsigned long FEEDBACK_DEBOUNCE_MS = 30;
const unsigned long WIFI_RETRY_INTERVAL_MS = 10000;
const unsigned long WIFI_STATUS_CHECK_MS = 1000;
const unsigned long SERVER_RETRY_INTERVAL_MS = 2000;
const unsigned long WIFI_CONNECT_TIMEOUT_MS = 5000;
const int SERVER_CONNECT_TIMEOUT_MS = 3000;
const unsigned long HEARTBEAT_INTERVAL_MS = 30000;

// Leave false until PIN_STOP_REQUEST and the MobilePlanner stop input have
// both been verified. When true, a detected admin-server disconnect produces
// one ordinary STOP_REQUEST pulse.
const bool PULSE_STOP_ON_SERVER_LOSS = false;

// ============================================================================
// Runtime state
// ============================================================================

WiFiClient adminClient;

const uint8_t COMMAND_PINS[] = {
    PIN_ROUTE_1,
    PIN_ROUTE_2,
    PIN_ROUTE_3,
    PIN_STOP_REQUEST,
};
const size_t COMMAND_PIN_COUNT = sizeof(COMMAND_PINS) / sizeof(COMMAND_PINS[0]);

enum FeedbackIndex
{
  FEEDBACK_READY = 0,
  FEEDBACK_BUSY,
  FEEDBACK_DONE,
  FEEDBACK_FAULT,
  FEEDBACK_COUNT
};

struct FeedbackChannel
{
  uint8_t pin;
  const char *name;
  bool rawActive;
  bool stableActive;
  unsigned long rawChangedAt;
};

FeedbackChannel feedbacks[FEEDBACK_COUNT] = {
    {PIN_FEEDBACK_READY, "READY", false, false, 0},
    {PIN_FEEDBACK_BUSY, "BUSY", false, false, 0},
    {PIN_FEEDBACK_DONE, "DONE", false, false, 0},
    {PIN_FEEDBACK_FAULT, "FAULT", false, false, 0},
};

const uint8_t NO_ACTIVE_PULSE_PIN = 0xFF;
uint8_t activePulsePin = NO_ACTIVE_PULSE_PIN;
const char *activePulseName = "NONE";
unsigned long activePulseStartedAt = 0;

const size_t RX_LINE_CAPACITY = 96;
char rxLine[RX_LINE_CAPACITY];
size_t rxLength = 0;
bool rxOverflow = false;

bool wifiConnected = false;
bool adminConnected = false;
unsigned long lastWiFiAttempt = 0;
unsigned long lastWiFiStatusCheck = 0;
unsigned long lastServerAttempt = 0;
unsigned long lastHeartbeat = 0;

// ============================================================================
// Forward declarations
// ============================================================================

void maintainWiFi();
void maintainAdminConnection();
void readAdminCommands();
void updateCommandPulse();
void updateFeedbackInputs();
void sendHeartbeatIfDue();
void handleCommand(char *line);
void sendStatus(const char *prefix);

// ============================================================================
// Setup / loop
// ============================================================================

void setup()
{
  Serial.begin(115200);
  delay(1200);

  Serial.println();
  Serial.println("AMR1 TCP-to-Digital-I/O bridge starting");

  for (size_t i = 0; i < COMMAND_PIN_COUNT; ++i)
  {
    pinMode(COMMAND_PINS[i], OUTPUT);
    digitalWrite(COMMAND_PINS[i], COMMAND_INACTIVE_LEVEL);
  }

  for (size_t i = 0; i < FEEDBACK_COUNT; ++i)
  {
    pinMode(feedbacks[i].pin, FEEDBACK_PIN_MODE);
    bool active = (digitalRead(feedbacks[i].pin) == FEEDBACK_ACTIVE_LEVEL);
    feedbacks[i].rawActive = active;
    feedbacks[i].stableActive = active;
    feedbacks[i].rawChangedAt = millis();
  }

  WiFi.setHostname("amr1-bridge");
  WiFi.setTimeout(WIFI_CONNECT_TIMEOUT_MS);
  adminClient.setConnectionTimeout(SERVER_CONNECT_TIMEOUT_MS);

  // Make both first connection attempts immediate.
  lastWiFiAttempt = millis() - WIFI_RETRY_INTERVAL_MS;
  lastServerAttempt = millis() - SERVER_RETRY_INTERVAL_MS;
}

void loop()
{
  // Time-critical local I/O is serviced before any network reconnect attempt.
  updateCommandPulse();
  updateFeedbackInputs();

  maintainWiFi();
  maintainAdminConnection();
  readAdminCommands();
  sendHeartbeatIfDue();
}

// ============================================================================
// Safe digital I/O
// ============================================================================

void setAllCommandOutputsInactive()
{
  for (size_t i = 0; i < COMMAND_PIN_COUNT; ++i)
  {
    digitalWrite(COMMAND_PINS[i], COMMAND_INACTIVE_LEVEL);
  }
}

void cancelActivePulse()
{
  if (activePulsePin != NO_ACTIVE_PULSE_PIN)
  {
    digitalWrite(activePulsePin, COMMAND_INACTIVE_LEVEL);
  }

  activePulsePin = NO_ACTIVE_PULSE_PIN;
  activePulseName = "NONE";
  activePulseStartedAt = 0;
}

bool writeAdminLine(const char *message)
{
  if (!adminConnected || !adminClient.connected())
  {
    return false;
  }

  const size_t messageLength = strlen(message);
  const uint8_t newline = '\n';
  const size_t messageWritten =
      adminClient.write(reinterpret_cast<const uint8_t *>(message), messageLength);
  const size_t newlineWritten = adminClient.write(&newline, 1);

  if (messageWritten != messageLength || newlineWritten != 1)
  {
    Serial.println("Admin server write failed");
    adminClient.stop();
    adminConnected = false;
    cancelActivePulse();
    setAllCommandOutputsInactive();
    return false;
  }

  Serial.print("Server < ");
  Serial.println(message);
  return true;
}

bool writeAdminFormat(const char *format, ...)
{
  char message[220];

  va_list arguments;
  va_start(arguments, format);
  vsnprintf(message, sizeof(message), format, arguments);
  va_end(arguments);

  message[sizeof(message) - 1] = '\0';
  return writeAdminLine(message);
}

void startCommandPulse(uint8_t pin, const char *name, bool allowPreemption)
{
  if (activePulsePin != NO_ACTIVE_PULSE_PIN)
  {
    if (!allowPreemption)
    {
      writeAdminFormat("ERR OUTPUT_BUSY active=%s", activePulseName);
      return;
    }

    writeAdminFormat("EVENT PULSE_CANCELLED name=%s", activePulseName);
    cancelActivePulse();
  }

  setAllCommandOutputsInactive();
  digitalWrite(pin, COMMAND_ACTIVE_LEVEL);
  activePulsePin = pin;
  activePulseName = name;
  activePulseStartedAt = millis();

  writeAdminFormat("ACK %s PULSE_STARTED duration_ms=%lu", name, COMMAND_PULSE_MS);
}

void updateCommandPulse()
{
  if (activePulsePin == NO_ACTIVE_PULSE_PIN)
  {
    return;
  }

  if (millis() - activePulseStartedAt < COMMAND_PULSE_MS)
  {
    return;
  }

  const char *completedName = activePulseName;
  digitalWrite(activePulsePin, COMMAND_INACTIVE_LEVEL);
  activePulsePin = NO_ACTIVE_PULSE_PIN;
  activePulseName = "NONE";
  activePulseStartedAt = 0;

  writeAdminFormat("EVENT %s PULSE_FINISHED", completedName);
}

bool readFeedbackActive(const FeedbackChannel &channel)
{
  return digitalRead(channel.pin) == FEEDBACK_ACTIVE_LEVEL;
}

void updateFeedbackInputs()
{
  const unsigned long now = millis();

  for (size_t i = 0; i < FEEDBACK_COUNT; ++i)
  {
    FeedbackChannel &channel = feedbacks[i];
    const bool active = readFeedbackActive(channel);

    if (active != channel.rawActive)
    {
      channel.rawActive = active;
      channel.rawChangedAt = now;
    }

    if (channel.stableActive == channel.rawActive ||
        now - channel.rawChangedAt < FEEDBACK_DEBOUNCE_MS)
    {
      continue;
    }

    channel.stableActive = channel.rawActive;

    // A fault transition immediately removes any still-active command pulse.
    if (i == FEEDBACK_FAULT && channel.stableActive)
    {
      cancelActivePulse();
      setAllCommandOutputsInactive();
    }

    writeAdminFormat(
        "EVENT IO_CHANGED signal=%s active=%d READY=%d BUSY=%d DONE=%d FAULT=%d",
        channel.name,
        channel.stableActive ? 1 : 0,
        feedbacks[FEEDBACK_READY].stableActive ? 1 : 0,
        feedbacks[FEEDBACK_BUSY].stableActive ? 1 : 0,
        feedbacks[FEEDBACK_DONE].stableActive ? 1 : 0,
        feedbacks[FEEDBACK_FAULT].stableActive ? 1 : 0);
  }
}

// ============================================================================
// Wi-Fi and admin-server connection management
// ============================================================================

void handleWiFiLoss()
{
  if (adminClient)
  {
    adminClient.stop();
  }

  adminConnected = false;
  cancelActivePulse();
  setAllCommandOutputsInactive();
  rxLength = 0;
  rxOverflow = false;

  Serial.println("Wi-Fi disconnected; command outputs forced inactive");
}

void attemptWiFiConnection()
{
  lastWiFiAttempt = millis();

  if (WiFi.status() == WL_NO_MODULE)
  {
    Serial.println("UNO R4 WiFi module not found");
    return;
  }

  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(WIFI_SSID);

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
    Serial.println("Wi-Fi connection failed; retry scheduled");
    return;
  }

  Serial.print("Wi-Fi connected. Arduino IP: ");
  Serial.println(WiFi.localIP());

  // Attempt the admin connection immediately after Wi-Fi comes back.
  lastServerAttempt = millis() - SERVER_RETRY_INTERVAL_MS;
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

    wifiConnected = false;
    handleWiFiLoss();
  }

  if (now - lastWiFiAttempt >= WIFI_RETRY_INTERVAL_MS)
  {
    attemptWiFiConnection();
  }
}

void handleAdminLoss()
{
  const bool wasConnected = adminConnected;

  if (adminClient)
  {
    adminClient.stop();
  }

  adminConnected = false;
  rxLength = 0;
  rxOverflow = false;
  cancelActivePulse();
  setAllCommandOutputsInactive();

  if (wasConnected)
  {
    Serial.println("Admin server disconnected; command outputs forced inactive");

    if (PULSE_STOP_ON_SERVER_LOSS)
    {
      digitalWrite(PIN_STOP_REQUEST, COMMAND_ACTIVE_LEVEL);
      activePulsePin = PIN_STOP_REQUEST;
      activePulseName = "STOP_REQUEST_SERVER_LOSS";
      activePulseStartedAt = millis();
    }
  }
}

void attemptAdminConnection()
{
  lastServerAttempt = millis();

  Serial.print("Connecting to admin server: ");
  Serial.print(ADMIN_SERVER_IP);
  Serial.print(':');
  Serial.println(ADMIN_SERVER_PORT);

  adminClient.stop();
  adminClient.setConnectionTimeout(SERVER_CONNECT_TIMEOUT_MS);

  if (!adminClient.connect(ADMIN_SERVER_IP, ADMIN_SERVER_PORT))
  {
    Serial.println("Admin server connection failed; retry scheduled");
    return;
  }

  adminConnected = true;
  rxLength = 0;
  rxOverflow = false;
  lastHeartbeat = millis();

  // TestServer_admin.py requires the relay name as the first received line.
  if (!writeAdminLine(RELAY_NAME))
  {
    return;
  }

  const IPAddress localIP = WiFi.localIP();
  writeAdminFormat(
      "ONLINE device=%s ip=%u.%u.%u.%u firmware=IO_BRIDGE_V1",
      RELAY_NAME,
      localIP[0],
      localIP[1],
      localIP[2],
      localIP[3]);
  sendStatus("STATUS");
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

  if (adminConnected || adminClient)
  {
    handleAdminLoss();
  }

  if (millis() - lastServerAttempt >= SERVER_RETRY_INTERVAL_MS)
  {
    attemptAdminConnection();
  }
}

// ============================================================================
// Line protocol and commands
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

void uppercaseAscii(char *text)
{
  for (size_t i = 0; text[i] != '\0'; ++i)
  {
    text[i] = static_cast<char>(toupper(static_cast<unsigned char>(text[i])));
  }
}

bool routeCommandBlocked()
{
  if (feedbacks[FEEDBACK_FAULT].stableActive)
  {
    writeAdminLine("ERR MOTION_BLOCKED reason=FAULT_INPUT_ACTIVE");
    return true;
  }

  if (feedbacks[FEEDBACK_BUSY].stableActive)
  {
    writeAdminLine("ERR MOTION_BLOCKED reason=BUSY_INPUT_ACTIVE");
    return true;
  }

  if (activePulsePin != NO_ACTIVE_PULSE_PIN)
  {
    writeAdminFormat("ERR OUTPUT_BUSY active=%s", activePulseName);
    return true;
  }

  return false;
}

void handleCommand(char *line)
{
  trimAsciiWhitespace(line);
  uppercaseAscii(line);

  if (line[0] == '\0')
  {
    return;
  }

  Serial.print("Server > ");
  Serial.println(line);

  if (strcmp(line, "PING") == 0)
  {
    writeAdminFormat("PONG uptime_ms=%lu", millis());
  }
  else if (strcmp(line, "STATUS") == 0)
  {
    sendStatus("STATUS");
  }
  else if (strcmp(line, "HELP") == 0)
  {
    writeAdminLine(
        "HELP ROUTE1|ROUTE2|ROUTE3|MOVE_ST1|MOVE_ST2|MOVE_ST3|STOP|END|STATUS|PING|ALL_OFF");
  }
  else if (strcmp(line, "STOP") == 0 || strcmp(line, "END") == 0)
  {
    // Stop always preempts another command pulse.
    startCommandPulse(PIN_STOP_REQUEST, "STOP_REQUEST", true);
  }
  else if (strcmp(line, "ALL_OFF") == 0)
  {
    cancelActivePulse();
    setAllCommandOutputsInactive();
    writeAdminLine("ACK ALL_OFF");
  }
  else if (strcmp(line, "ROUTE1") == 0 || strcmp(line, "MOVE_ST1") == 0)
  {
    if (!routeCommandBlocked())
    {
      startCommandPulse(PIN_ROUTE_1, "ROUTE1", false);
    }
  }
  else if (strcmp(line, "ROUTE2") == 0 || strcmp(line, "MOVE_ST2") == 0)
  {
    if (!routeCommandBlocked())
    {
      startCommandPulse(PIN_ROUTE_2, "ROUTE2", false);
    }
  }
  else if (strcmp(line, "ROUTE3") == 0 || strcmp(line, "MOVE_ST3") == 0)
  {
    if (!routeCommandBlocked())
    {
      startCommandPulse(PIN_ROUTE_3, "ROUTE3", false);
    }
  }
  else
  {
    writeAdminFormat("ERR UNKNOWN_COMMAND value=%s", line);
  }
}

void finishReceivedLine()
{
  if (rxOverflow)
  {
    writeAdminLine("ERR COMMAND_TOO_LONG max_bytes=95");
  }
  else
  {
    rxLine[rxLength] = '\0';
    handleCommand(rxLine);
  }

  rxLength = 0;
  rxOverflow = false;
}

void readAdminCommands()
{
  if (!adminConnected || !adminClient.connected())
  {
    return;
  }

  // Bound work per loop so local pulse timing and feedback remain responsive.
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
      finishReceivedLine();
    }
    else if (c == '\r')
    {
      // Accept both LF and CRLF line endings.
    }
    else if (!rxOverflow)
    {
      if (rxLength < RX_LINE_CAPACITY - 1)
      {
        rxLine[rxLength++] = c;
      }
      else
      {
        rxOverflow = true;
      }
    }
  }
}

// ============================================================================
// Status reporting
// ============================================================================

void sendStatus(const char *prefix)
{
  writeAdminFormat(
      "%s WIFI=%s SERVER=%s PULSE=%s READY=%d BUSY=%d DONE=%d FAULT=%d uptime_ms=%lu rssi_dbm=%ld",
      prefix,
      wifiConnected ? "CONNECTED" : "DISCONNECTED",
      adminConnected ? "CONNECTED" : "DISCONNECTED",
      activePulseName,
      feedbacks[FEEDBACK_READY].stableActive ? 1 : 0,
      feedbacks[FEEDBACK_BUSY].stableActive ? 1 : 0,
      feedbacks[FEEDBACK_DONE].stableActive ? 1 : 0,
      feedbacks[FEEDBACK_FAULT].stableActive ? 1 : 0,
      millis(),
      static_cast<long>(WiFi.RSSI()));
}

void sendHeartbeatIfDue()
{
  if (!adminConnected || !adminClient.connected())
  {
    return;
  }

  if (millis() - lastHeartbeat < HEARTBEAT_INTERVAL_MS)
  {
    return;
  }

  lastHeartbeat = millis();
  sendStatus("HEARTBEAT");
}

#endif // !AMR_IO_BRIDGE_USE_SERVER_AMR
