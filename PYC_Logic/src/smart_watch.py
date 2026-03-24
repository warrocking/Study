from dataclasses import dataclass
from enum import Enum, auto
from time import time

from pop import (
    Cds,
    Gesture,
    Leds,
    Oled,
    PiezoBuzzer,
    Potentiometer,
    Psd,
    Sht20,
    Sound,
    Switches,
    delay,
)


def clamp(value, low, high):
    if value < low:
        return low
    if value > high:
        return high
    return value


def now_ms():
    return int(time() * 1000)


class AppState(Enum):
    MAIN_MENU = auto()
    ENV_CHECK = auto()
    BATTERY = auto()
    STOPWATCH = auto()
    TIMER_SET_MIN = auto()
    TIMER_SET_SEC = auto()
    TIMER_READY = auto()
    TIMER_RUN = auto()
    NIGHT_ALERT = auto()
    EXIT = auto()


@dataclass
class SensorData:
    temp_c: float = 0.0
    humi_pct: float = 0.0
    cds_raw: int = 0
    sound_raw: int = 0
    psd_cm: float = 999.0
    pot_raw: int = 0
    pot_volt: float = 0.0


@dataclass
class InputEvent:
    sw0_click: bool = False
    sw1_click: bool = False
    gesture: str = None


@dataclass
class EnvResult:
    score: int
    grade: str
    led_level: int
    message: str


@dataclass
class BatteryResult:
    percent: int
    led_level: int
    low_alarm: bool


@dataclass
class NightAlertResult:
    active: bool
    distance_cm: float
    led_level: int
    buzzer_on: bool
    pattern: str


class HardwareIO:
    def __init__(self):
        try:
            self.oled = Oled(automode=False)
        except TypeError:
            self.oled = Oled()

        try:
            self.oled.init()
        except Exception:
            pass

        self.switches = Switches()
        self.leds = Leds()
        self.pot = Potentiometer()
        self.gesture = Gesture()
        self.buzzer = PiezoBuzzer()
        self.sht = Sht20()
        self.cds = Cds()
        self.sound = Sound()
        self.psd = Psd()

        self.buzzer.setTempo(120)
        self._sweep_idx = 0
        self._sweep_dir = 1

        self.leds.allOff()
        self._clear_oled()

    def _clear_oled(self):
        self.oled.clearDisplay()
        self.oled.display()

    def read_buttons(self):
        # pressed = False, released = True
        return self.switches[0].read(), self.switches[1].read()

    def read_gesture(self):
        try:
            if self.gesture.isAvailable():
                motion = self.gesture.readStr()
                if motion and motion != "None":
                    return motion
        except Exception:
            pass
        return None

    def read_sensors(self):
        data = SensorData()

        try:
            data.temp_c = float(self.sht.readTemp())
        except Exception:
            data.temp_c = 0.0

        try:
            data.humi_pct = float(self.sht.readHumi())
        except Exception:
            data.humi_pct = 0.0

        try:
            data.cds_raw = int(self.cds.read())
        except Exception:
            data.cds_raw = 0

        try:
            data.sound_raw = int(self.sound.read())
        except Exception:
            data.sound_raw = 0

        try:
            psd_raw = self.psd.readAverage()
            data.psd_cm = float(self.psd.calcDist(psd_raw))
        except Exception:
            try:
                data.psd_cm = float(self.psd.read())
            except Exception:
                data.psd_cm = 999.0

        try:
            data.pot_raw = int(self.pot.read())
        except Exception:
            data.pot_raw = 0

        try:
            data.pot_volt = float(self.pot.readVolt())
        except Exception:
            data.pot_volt = 0.0

        return data

    def set_led_bar(self, level):
        n = clamp(int(level), 0, 8)
        self.leds.allOff()
        for i in range(n):
            self.leds[i].on()

    def set_led_blink(self, on):
        if on:
            self.leds.allOn()
        else:
            self.leds.allOff()

    def set_led_sweep_step(self):
        self.leds.allOff()
        left = self._sweep_idx
        right = 7 - self._sweep_idx
        self.leds[left].on()
        self.leds[right].on()

        self._sweep_idx += self._sweep_dir
        if self._sweep_idx >= 3:
            self._sweep_idx = 3
            self._sweep_dir = -1
        elif self._sweep_idx <= 0:
            self._sweep_idx = 0
            self._sweep_dir = 1

    def _tone(self, a, b, c):
        try:
            self.buzzer.tone(a, b, c)
            return
        except TypeError:
            pass
        except Exception:
            return

        try:
            self.buzzer.tone(a, b)
        except Exception:
            pass

    def beep_short(self):
        self._tone(4, 4, 16)

    def beep_alert(self):
        self._tone(8, 8, 8)

    def stop_buzzer(self):
        if hasattr(self.buzzer, "stop"):
            try:
                self.buzzer.stop()
            except Exception:
                pass

    def clear_outputs(self):
        self.leds.allOff()
        self.stop_buzzer()

    def cleanup(self):
        self.clear_outputs()
        self._clear_oled()


class InputManager:
    def __init__(self):
        self.prev_sw0_raw = True
        self.prev_sw1_raw = True
        self.last_gesture_ms = 0
        self.gesture_cooldown_ms = 250

    def update(self, sw0_raw, sw1_raw, gesture_raw, t_ms):
        ev = InputEvent()

        # Falling edge: released(True) -> pressed(False)
        ev.sw0_click = self.prev_sw0_raw and (not sw0_raw)
        ev.sw1_click = self.prev_sw1_raw and (not sw1_raw)
        self.prev_sw0_raw = sw0_raw
        self.prev_sw1_raw = sw1_raw

        if (
            gesture_raw
            and t_ms - self.last_gesture_ms >= self.gesture_cooldown_ms
        ):
            ev.gesture = gesture_raw
            self.last_gesture_ms = t_ms

        return ev


class EnvChecker:
    def evaluate(self, sensor):
        score = 0

        # Temperature: ideal 20~26 C
        score += min(30, int(abs(sensor.temp_c - 23) * 4))

        # Humidity: ideal 40~60 %
        if sensor.humi_pct < 40:
            score += min(20, int((40 - sensor.humi_pct) * 0.8))
        elif sensor.humi_pct > 60:
            score += min(20, int((sensor.humi_pct - 60) * 0.8))

        # Brightness: very dark or too bright -> penalty
        if sensor.cds_raw < 200:
            score += 12
        elif sensor.cds_raw > 3200:
            score += 12

        # Noise
        if sensor.sound_raw > 2000:
            score += 25
        elif sensor.sound_raw > 1500:
            score += 12

        score = clamp(score, 0, 100)
        led_level = clamp(int(round(score / 12.5)), 0, 8)

        if score >= 70:
            return EnvResult(score, "WARNING", led_level, "Need rest / ventilation")
        if score >= 40:
            return EnvResult(score, "CAUTION", led_level, "Check environment")
        return EnvResult(score, "GOOD", led_level, "Comfortable")


class BatteryMonitor:
    def evaluate(self, sensor):
        # PYC basic has no direct battery API in this project.
        # Use potentiometer as virtual battery source: 10% ~ 70%.
        percent = int(10 + (clamp(sensor.pot_volt, 0.0, 3.3) / 3.3) * 60)
        percent = clamp(percent, 10, 70)
        led_level = clamp(int(round((percent / 70.0) * 8)), 0, 8)
        low_alarm = percent <= 20
        return BatteryResult(percent, led_level, low_alarm)


class StopwatchFeature:
    def __init__(self):
        self.running = False
        self.base_elapsed_ms = 0
        self.start_ms = 0

    def reset(self):
        self.running = False
        self.base_elapsed_ms = 0
        self.start_ms = 0

    def toggle(self, t_ms):
        if self.running:
            self.base_elapsed_ms += t_ms - self.start_ms
            self.running = False
        else:
            self.start_ms = t_ms
            self.running = True

    def elapsed_ms(self, t_ms):
        if self.running:
            return self.base_elapsed_ms + (t_ms - self.start_ms)
        return self.base_elapsed_ms


class TimerFeature:
    def __init__(self):
        self.minute = 0
        self.second = 0
        self.running = False
        self.end_ms = 0

    def reset(self):
        self.minute = 0
        self.second = 0
        self.running = False
        self.end_ms = 0

    def set_minute_from_pot(self, pot_raw):
        self.minute = clamp(int((pot_raw / 4095.0) * 59), 0, 59)

    def set_second_from_pot(self, pot_raw):
        self.second = clamp(int((pot_raw / 4095.0) * 59), 0, 59)

    def start(self, t_ms):
        total = self.minute * 60 + self.second
        if total <= 0:
            return False
        self.end_ms = t_ms + total * 1000
        self.running = True
        return True

    def stop(self):
        self.running = False

    def remain_sec(self, t_ms):
        if not self.running:
            return self.minute * 60 + self.second, False

        if t_ms >= self.end_ms:
            self.running = False
            return 0, True

        remain = (self.end_ms - t_ms + 999) // 1000
        return int(remain), False


class NightAlertFeature:
    def __init__(self):
        self.active = True

    def reset(self):
        self.active = True

    def evaluate(self, sensor):
        d = sensor.psd_cm
        if not self.active:
            return NightAlertResult(False, d, 0, False, "none")

        if d <= 15:
            return NightAlertResult(True, d, 8, True, "sweep")
        if d <= 20:
            return NightAlertResult(True, d, 8, True, "fill")
        if d <= 25:
            return NightAlertResult(True, d, 7, False, "fill")
        if d <= 30:
            return NightAlertResult(True, d, 6, False, "fill")
        if d <= 40:
            return NightAlertResult(True, d, 5, False, "fill")
        if d <= 50:
            return NightAlertResult(True, d, 4, False, "fill")
        if d <= 60:
            return NightAlertResult(True, d, 3, False, "fill")
        if d <= 70:
            return NightAlertResult(True, d, 2, False, "fill")
        if d <= 80:
            return NightAlertResult(True, d, 1, False, "fill")
        return NightAlertResult(True, d, 0, False, "none")


class UIRenderer:
    def __init__(self, hw):
        self.hw = hw
        self.display = hw.oled

    def _draw_lines(self, lines, text_size=1):
        d = self.display
        d.clearDisplay()
        d.setTextSize(text_size)
        d.setCursor(0, 0)
        for line in lines:
            d.print(line + "\n")
        d.display()

    def draw_menu(self, idx, items):
        prev_idx = (idx - 1) % len(items)
        next_idx = (idx + 1) % len(items)
        lines = [
            "Smart Watch",
            "G:Move SW0:Enter",
            "SW1:Back",
            ">{}".format(items[idx]),
            " {} / {}".format(items[prev_idx], items[next_idx]),
        ]
        self._draw_lines(lines, 1)

    def draw_env(self, sensor, result):
        lines = [
            "ENV CHECK",
            "T:{:.1f}C H:{:.1f}%".format(sensor.temp_c, sensor.humi_pct),
            "Light:{} Sound:{}".format(sensor.cds_raw, sensor.sound_raw),
            "Score:{} {}".format(result.score, result.grade),
            "SW1:Back",
        ]
        self._draw_lines(lines, 1)

    def draw_battery(self, sensor, result):
        lines = [
            "BATTERY(Virtual)",
            "Poten:{:.2f}V".format(sensor.pot_volt),
            "Remain:{}%".format(result.percent),
            "Low Alert:{}".format("ON" if result.low_alarm else "OFF"),
            "SW1:Back",
        ]
        self._draw_lines(lines, 1)

    def draw_stopwatch(self, elapsed, running):
        ms = (elapsed // 10) % 100
        sec = (elapsed // 1000) % 60
        minute = elapsed // 60000
        lines = [
            "STOPWATCH",
            "{:02d}:{:02d}.{:02d}".format(minute, sec, ms),
            "SW0:Start/Stop",
            "SW1:Back",
            "State:{}".format("RUN" if running else "STOP"),
        ]
        self._draw_lines(lines, 1)

    def draw_timer_set(self, minute, second, focus):
        lines = [
            "TIMER SET",
            "Min:{:02d} Sec:{:02d}".format(minute, second),
            "Gesture L/R move",
            "Poten: value set",
            "SW0:Confirm SW1:Back",
            "Focus:{}".format(focus),
        ]
        self._draw_lines(lines, 1)

    def draw_timer_ready(self, minute, second):
        lines = [
            "TIMER READY",
            "{:02d}:{:02d}".format(minute, second),
            "SW0:Start",
            "SW1:Back",
        ]
        self._draw_lines(lines, 1)

    def draw_timer_run(self, remain_sec, done):
        mm = remain_sec // 60
        ss = remain_sec % 60
        lines = [
            "TIMER RUN",
            "{:02d}:{:02d}".format(mm, ss),
            "SW1:Back",
        ]
        if done:
            lines.append("DONE! SW0 or SW1")
        self._draw_lines(lines, 1)

    def draw_night_alert(self, result):
        lines = [
            "NIGHT ALERT",
            "Dist:{:.1f}cm".format(result.distance_cm),
            "Mode:{}".format("ON" if result.active else "OFF"),
            "Level:{} Pattern:{}".format(result.led_level, result.pattern),
            "SW0:On/Off SW1:Back",
        ]
        self._draw_lines(lines, 1)

    def draw_exit(self):
        self._draw_lines(["Good bye!"], 2)


class SmartWatchApp:
    def __init__(self):
        self.hw = HardwareIO()
        self.input = InputManager()
        self.ui = UIRenderer(self.hw)

        self.env_checker = EnvChecker()
        self.battery_monitor = BatteryMonitor()
        self.stopwatch = StopwatchFeature()
        self.timer = TimerFeature()
        self.night = NightAlertFeature()

        self.state = AppState.MAIN_MENU
        self.menu = [
            "1.Env",
            "2.Battery",
            "3.StopWatch",
            "4.Timer",
            "5.Night",
            "6.Exit",
        ]
        self.menu_idx = 0

        self.timer_done = False
        self.last_sensor_ms = 0
        self.sensor = SensorData()
        self.last_beep_ms = 0
        self.loop_ms = 20
        self.sensor_period_ms = 200

    def change_state(self, new_state):
        self.state = new_state
        self.last_beep_ms = 0

        if new_state == AppState.MAIN_MENU:
            self.hw.clear_outputs()
        elif new_state == AppState.TIMER_SET_MIN:
            self.timer.reset()
            self.timer_done = False
        elif new_state == AppState.STOPWATCH:
            self.stopwatch.reset()
        elif new_state == AppState.NIGHT_ALERT:
            self.night.reset()

    def _beep_every(self, t_ms, period_ms, alert=False):
        if t_ms - self.last_beep_ms >= period_ms:
            if alert:
                self.hw.beep_alert()
            else:
                self.hw.beep_short()
            self.last_beep_ms = t_ms

    def handle_main_menu(self, ev):
        if ev.gesture in ("Left", "Up"):
            self.menu_idx = (self.menu_idx - 1) % len(self.menu)
        elif ev.gesture in ("Right", "Down"):
            self.menu_idx = (self.menu_idx + 1) % len(self.menu)

        if ev.sw0_click:
            if self.menu_idx == 0:
                self.change_state(AppState.ENV_CHECK)
            elif self.menu_idx == 1:
                self.change_state(AppState.BATTERY)
            elif self.menu_idx == 2:
                self.change_state(AppState.STOPWATCH)
            elif self.menu_idx == 3:
                self.change_state(AppState.TIMER_SET_MIN)
            elif self.menu_idx == 4:
                self.change_state(AppState.NIGHT_ALERT)
            elif self.menu_idx == 5:
                self.change_state(AppState.EXIT)

        self.ui.draw_menu(self.menu_idx, self.menu)

    def handle_env_check(self, ev, t_ms):
        if ev.sw1_click:
            self.change_state(AppState.MAIN_MENU)
            return

        result = self.env_checker.evaluate(self.sensor)
        self.hw.set_led_bar(result.led_level)
        if result.grade == "WARNING":
            self._beep_every(t_ms, 1200, alert=True)
        self.ui.draw_env(self.sensor, result)

    def handle_battery(self, ev, t_ms):
        if ev.sw1_click:
            self.change_state(AppState.MAIN_MENU)
            return

        result = self.battery_monitor.evaluate(self.sensor)
        self.hw.set_led_bar(result.led_level)
        if result.low_alarm:
            self._beep_every(t_ms, 900, alert=True)
        self.ui.draw_battery(self.sensor, result)

    def handle_stopwatch(self, ev, t_ms):
        if ev.sw0_click:
            self.stopwatch.toggle(t_ms)

        if ev.sw1_click:
            self.change_state(AppState.MAIN_MENU)
            return

        elapsed = self.stopwatch.elapsed_ms(t_ms)
        self.ui.draw_stopwatch(elapsed, self.stopwatch.running)

    def handle_timer(self, ev, t_ms):
        if self.state == AppState.TIMER_SET_MIN:
            self.timer.set_minute_from_pot(self.sensor.pot_raw)
            if ev.gesture in ("Right", "Down") or ev.sw0_click:
                self.change_state(AppState.TIMER_SET_SEC)
                return
            if ev.sw1_click:
                self.change_state(AppState.MAIN_MENU)
                return
            self.ui.draw_timer_set(self.timer.minute, self.timer.second, "MIN")
            return

        if self.state == AppState.TIMER_SET_SEC:
            self.timer.set_second_from_pot(self.sensor.pot_raw)
            if ev.gesture in ("Left", "Up"):
                self.change_state(AppState.TIMER_SET_MIN)
                return
            if ev.sw0_click:
                self.change_state(AppState.TIMER_READY)
                return
            if ev.sw1_click:
                self.change_state(AppState.MAIN_MENU)
                return
            self.ui.draw_timer_set(self.timer.minute, self.timer.second, "SEC")
            return

        if self.state == AppState.TIMER_READY:
            if ev.sw0_click:
                if self.timer.start(t_ms):
                    self.timer_done = False
                    self.change_state(AppState.TIMER_RUN)
                else:
                    self.hw.beep_short()
                return
            if ev.sw1_click:
                self.change_state(AppState.MAIN_MENU)
                return
            self.ui.draw_timer_ready(self.timer.minute, self.timer.second)
            return

        if self.state == AppState.TIMER_RUN:
            remain, done = self.timer.remain_sec(t_ms)
            self.timer_done = done

            if done:
                self.hw.set_led_blink((t_ms // 300) % 2 == 0)
                self._beep_every(t_ms, 350, alert=True)
                if ev.sw0_click or ev.sw1_click:
                    self.hw.clear_outputs()
                    self.change_state(AppState.MAIN_MENU)
                    return
            else:
                if ev.sw1_click:
                    self.timer.stop()
                    self.change_state(AppState.MAIN_MENU)
                    return

            self.ui.draw_timer_run(remain, done)

    def handle_night_alert(self, ev, t_ms):
        if ev.sw1_click:
            self.change_state(AppState.MAIN_MENU)
            return

        if ev.sw0_click:
            self.night.active = not self.night.active
            self.hw.clear_outputs()

        result = self.night.evaluate(self.sensor)
        if not result.active:
            self.hw.clear_outputs()
        else:
            if result.pattern == "sweep":
                self.hw.set_led_sweep_step()
                self._beep_every(t_ms, 250, alert=True)
            else:
                self.hw.set_led_bar(result.led_level)
                if result.buzzer_on:
                    self._beep_every(t_ms, 500, alert=True)

        self.ui.draw_night_alert(result)

    def run(self):
        while self.state != AppState.EXIT:
            t_ms = now_ms()
            sw0_raw, sw1_raw = self.hw.read_buttons()
            gesture_raw = self.hw.read_gesture()
            ev = self.input.update(sw0_raw, sw1_raw, gesture_raw, t_ms)

            if t_ms - self.last_sensor_ms >= self.sensor_period_ms:
                self.sensor = self.hw.read_sensors()
                self.last_sensor_ms = t_ms

            if self.state == AppState.MAIN_MENU:
                self.handle_main_menu(ev)
            elif self.state == AppState.ENV_CHECK:
                self.handle_env_check(ev, t_ms)
            elif self.state == AppState.BATTERY:
                self.handle_battery(ev, t_ms)
            elif self.state == AppState.STOPWATCH:
                self.handle_stopwatch(ev, t_ms)
            elif self.state in (
                AppState.TIMER_SET_MIN,
                AppState.TIMER_SET_SEC,
                AppState.TIMER_READY,
                AppState.TIMER_RUN,
            ):
                self.handle_timer(ev, t_ms)
            elif self.state == AppState.NIGHT_ALERT:
                self.handle_night_alert(ev, t_ms)

            delay(self.loop_ms)

        self.ui.draw_exit()
        delay(600)
        self.hw.cleanup()


def main():
    app = SmartWatchApp()
    try:
        app.run()
    except KeyboardInterrupt:
        app.hw.cleanup()


if __name__ == "__main__":
    main()
