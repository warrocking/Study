const char WIFI_SSID[] = "ROBOT_MA2_2G";

IPAddress ARDUINO_IP(192, 168, 0, 182);
IPAddress DNS_IP(192, 168, 0, 1);
IPAddress GATEWAY_IP(192, 168, 0, 1);
IPAddress SUBNET_MASK(255, 255, 255, 0);

IPAddress LD90_IP(192, 168, 0, 10);
const uint16_t LD90_PORT = 7171;
const char ARCL_PASSWORD[] = "1234";
const char FIRMWARE_VERSION[] = "2026-08-05-plc-auto-cycle-final";

// ------------------------ MobilePlanner names ---------------------
const char MACRO_ST1[] = "MACRO_ST1";
const char MACRO_ST2[] = "MACRO_ST2";
const char MACRO_ST3[] = "MACRO_ST3";

// ----------------------------- I/O -------------------------------
const uint8_t PLC1_COMPLETE_PIN = 2;
const uint8_t PLC2_SIGNAL_PIN = 3;
const uint8_t PLC3_SIGNAL_PIN = 4;
const uint8_t PLC_SIGNAL_ACTIVE_LEVEL = LOW;

const uint8_t CONVEYOR_FORWARD_PIN = 10;
const uint8_t CONVEYOR_REVERSE_PIN = 11;

const uint8_t PRODUCT_OBJECT_ID = 1;

// ---------------------------- Timing -----------------------------
const unsigned long PLC_DEBOUNCE_MS = 80;
const unsigned long CONVEYOR_RUN_MS = 5000;
const unsigned long WIFI_RETRY_MS = 15000;
const unsigned long LD90_RETRY_MS = 5000;
const unsigned long ARCL_LOGIN_TIMEOUT_MS = 10000;
const unsigned long MOTOR_QUERY_MS = 3000;
const unsigned long NEXT_MACRO_DELAY_MS = 1500;
const unsigned long MOTION_TIMEOUT_MS = 180000;
const unsigned long HUSKY_RETRY_MS = 10000;
const unsigned long HUSKY_POLL_MS = 150;

WiFiClient ld90;
HUSKYLENS huskylens;
String ldRx;
String activeMacro;

enum ConveyorDirection : uint8_t {
  CONVEYOR_STOPPED,
  CONVEYOR_FORWARD,
  CONVEYOR_REVERSE
};

const char *CYCLE_MACROS[] = {
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

struct DebouncedInput {
  uint8_t pin;
  bool stableActive;
  bool rawActive;
  unsigned long changedAt;
};

DebouncedInput plc1 = {PLC1_COMPLETE_PIN, false, false, 0};
DebouncedInput plc2 = {PLC2_SIGNAL_PIN, false, false, 0};
DebouncedInput plc3 = {PLC3_SIGNAL_PIN, false, false, 0};

unsigned long lastWiFiAttempt = 0;
unsigned long lastLD90Attempt = 0;
unsigned long ld90ConnectedAt = 0;
unsigned long lastMotorQuery = 0;
unsigned long motionStartedAt = 0;
unsigned long nextMacroAt = 0;
unsigned long conveyorStartedAt = 0;
unsigned long lastHuskyAttempt = 0;
unsigned long lastHuskyPoll = 0;

bool wifiWasOnline = false;
bool arclAuthenticated = false;
bool motorsConfirmed = false;
bool autoEnableSent = false;
bool macroRunning = false;
bool waitRunning = false;
bool conveyorStartedInCurrentWait = false;
bool conveyorRunning = false;
bool cycleRunning = false;
bool nextMacroPending = false;
bool plc1RequestPending = false;
bool plc1CanTrigger = true;
bool huskyOnline = false;

uint8_t cycleStep = 0;
ConveyorDirection conveyorDirection = CONVEYOR_STOPPED;

void report(const String &line) {
  Serial.println(line);
}

void stopConveyor() {
  // Safety interlock: both pins go LOW before every stop or direction change.
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

bool sendARCL(const String &command) {
  if (!ld90.connected() || !arclAuthenticated) {
    report("ERROR LD90_NOT_READY command=\"" + command + "\"");
    return false;
  }

  ld90.println(command);
  report("ARCL_TX " + command);
  return true;
}

void clearMotionState() {
  stopConveyor();
  macroRunning = false;
  waitRunning = false;
  conveyorStartedInCurrentWait = false;
  cycleRunning = false;
  nextMacroPending = false;
  activeMacro = "";
  cycleStep = 0;
}

bool startMacro(const char *name) {
  if (!arclAuthenticated || !motorsConfirmed || macroRunning) return false;

  stopConveyor();
  waitRunning = false;
  conveyorStartedInCurrentWait = false;
  activeMacro = name;

  if (!sendARCL(String("executeMacro ") + name)) return false;

  macroRunning = true;
  motionStartedAt = millis();
  report("EVENT MACRO_REQUESTED name=\"" + activeMacro + "\"");
  return true;
}

void startCycle() {
  if (!arclAuthenticated || !motorsConfirmed || macroRunning || cycleRunning) {
    report("EVENT CYCLE_START_DEFERRED reason=AMR_NOT_READY");
    return;
  }

  cycleStep = 0;
  cycleRunning = true;
  report("EVENT CYCLE_START trigger=PLC1 sequence=ST1:FWD,ST2:REV,ST1:REV,ST3:FWD,ST2:REV,ST3:REV");

  if (!startMacro(CYCLE_MACROS[cycleStep])) {
    clearMotionState();
    report("EVENT CYCLE_ABORT reason=FIRST_MACRO_REJECTED");
  }