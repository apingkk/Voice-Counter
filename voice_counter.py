import os
import json
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
from vosk import Model, KaldiRecognizer
import pyaudio

# ========== 安卓模型路径适配（已经改成model）==========
if os.path.exists("/data/data/org.voice.counter/files/app/model"):
    MODEL_PATH = "/data/data/org.voice.counter/files/app/model"
else:
    MODEL_PATH = "model"

# 中文数字映射
cn_map = {
    "零":0, "一":1, "二":2, "三":3, "四":4, "五":5,
    "六":6, "七":7, "八":8, "九":9, "十":10
}

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 20
        self.padding = 40

        self.count = 0
        self.running = False
        self.recognizer = None
        self.pa = None
        self.stream = None

        self.label_num = Label(text=f"当前计数：{self.count}", font_size=48)
        self.label_text = Label(text="等待识别...", font_size=24)

        self.btn_start = Button(text="开始监听", font_size=26, size_hint_y=0.2)
        self.btn_reset = Button(text="重置计数", font_size=26, size_hint_y=0.2)

        self.btn_start.bind(on_press=self.toggle_listen)
        self.btn_reset.bind(on_press=self.reset_count)

        self.add_widget(self.label_num)
        self.add_widget(self.label_text)
        self.add_widget(self.btn_start)
        self.add_widget(self.btn_reset)

    def toggle_listen(self, instance):
        if not self.running:
            self.running = True
            self.btn_start.text = "停止监听"
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.running = False
            self.btn_start.text = "开始监听"

    def reset_count(self, instance):
        self.count = 0
        self.update_ui()

    def listen_loop(self):
        try:
            model = Model(MODEL_PATH)
            rec = KaldiRecognizer(model, 16000)
            self.pa = pyaudio.PyAudio()
            self.stream = self.pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
            self.stream.start_stream()
            self.set_text("识别已就绪，可以说话")

            while self.running:
                data = self.stream.read(4000, exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    txt = res.get("text", "").strip()
                    if txt:
                        self.parse_text(txt)
        except Exception as e:
            self.set_text(f"出错：{str(e)}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.pa:
                self.pa.terminate()

    def parse_text(self, txt):
        self.set_text(f"识别到：{txt}")
        for char in txt:
            if char in cn_map:
                num = cn_map[char]
                self.count += num
                self.update_ui()
                break

    @mainthread
    def update_ui(self):
        self.label_num.text = f"当前计数：{self.count}"

    @mainthread
    def set_text(self, s):
        self.label_text.text = s

class VoiceCounterApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    VoiceCounterApp().run()
