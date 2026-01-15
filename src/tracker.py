import time
from collections import deque
from threading import Lock
from pynput import keyboard, mouse
from .config import TIME_RANGE

class InputTracker:
    def __init__(self):
        self.lock = Lock()
        self.start_time = time.time()
        
        self.events = deque() 
        self.active_keys = {'q': None, 'd': None}
        
        # Stats
        self.valid_count = 0
        self.invalid_count = 0
        self.threshold_ms = 175 
        
        self.kb_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.kb_listener.start()
        self.mouse_listener.start()

    def set_threshold(self, val):
        self.threshold_ms = val

    def reset_stats(self):
        with self.lock:
            self.valid_count = 0
            self.invalid_count = 0
            self.events.clear()

    def current_time(self):
        return time.time() - self.start_time

    def add_event(self, event_type, start, end=None, info=None, lane=None):
        with self.lock:
            self.events.append({'type': event_type, 'start': start, 'end': end, 'info': info, 'lane': lane})
            curr = time.time() - self.start_time
            while self.events and (self.events[0]['end'] is not None and curr - self.events[0]['end'] > TIME_RANGE + 1):
                self.events.popleft()

    def on_press(self, key):
        try: k = key.char.lower()
        except AttributeError: return
        if k in ['q', 'd']:
            if self.active_keys[k] is None:
                curr_t = self.current_time()
                self.active_keys[k] = curr_t
                self.add_event(k.upper(), curr_t, None)

    def on_release(self, key):
        try: k = key.char.lower()
        except AttributeError: return
        if k in ['q', 'd']:
            if self.active_keys[k] is not None:
                start_t = self.active_keys[k]
                end_t = self.current_time()
                self.active_keys[k] = None
                with self.lock:
                    for ev in reversed(self.events):
                        if ev['type'] == k.upper() and ev['start'] == start_t and ev['end'] is None:
                            ev['end'] = end_t
                            break

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            t = self.current_time()
            display_text = ""
            lane = 'MIDDLE'
            
            q_start = self.active_keys['q']
            d_start = self.active_keys['d']
            last_press_time = None
            
            if q_start is not None:
                last_press_time = q_start
                lane = 'Q'
            if d_start is not None:
                if last_press_time is None or d_start > last_press_time:
                    last_press_time = d_start
                    lane = 'D'

            ms = 0
            if last_press_time is not None:
                ms = int((t - last_press_time) * 1000)
                display_text = f"{ms}ms"
                
                if ms <= self.threshold_ms:
                    self.valid_count += 1
                else:
                    self.invalid_count += 1
            
            self.add_event('CLICK', t, t + 0.05, info=display_text, lane=lane)
