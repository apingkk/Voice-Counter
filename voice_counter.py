from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
import vosk
import json
import threading
import os
import sys

# 安卓模型路径适配
if os.path.exists("/data/data/org.voice.counter/files/app/vosk-model-small-cn-0.22"):
    MODEL_PATH = "/data/data/org.voice.counter/files/app/vosk-model-small-cn-0.22"
else:
    MODEL_PATH = "vosk-model-small-cn-0.22"

# 中文数字映射
cn_map = {
    "零":0,"一":1,"二":2,"三":3,"四":4,"五":5,
    "六":6,"七":7,"八":8,"九":9,"十":10
}

# 安卓动态权限
if sys.platform == "android":
    from android import AndroidService
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.RECORD_AUDIO])

class CounterLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 16
        self.padding = 32
        self.count = 0
        self.listening = False
        self.use_vad = False  # 默认关闭VAD，极致低延迟
        self.rec = None

        # UI组件
        self.num_label = Label(text="0", font_size=110, bold=True)
        self.tip_label = Label(text="就绪，点击开始监听", font_size=18)
        self.btn_start = Button(text="开始监听", font_size=20, size_hint_y=0.18)
        self.btn_vad = Button(text="VAD:关闭(低延迟)", font_size=18, size_hint_y=0.15)
        self.btn_clear = Button(text="清零", font_size=20, size_hint_y=0.18)

        self.btn_start.bind(on_press=self.toggle_listen)
        self.btn_vad.bind(on_press=self.switch_vad)
        self.btn_clear.bind(on_press=self.clear_num)

        self.add_widget(self.num_label)
        self.add_widget(self.tip_label)
        self.add_widget(self.btn_start)
        self.add_widget(self.btn_vad)
        self.add_widget(self.btn_clear)

    def switch_vad(self, inst):
        self.use_vad = not self.use_vad
        if self.use_vad:
            self.btn_vad.text = "VAD:开启(等停顿)"
            self.tip_label.text = "VAD开启，识别会有停顿延迟"
        else:
            self.btn_vad.text = "VAD:关闭(低延迟)"
            self.tip_label.text = "VAD关闭，极致低延迟"

    def parse_text(self, txt):
        txt = txt.strip()
        if txt in ("清零", "归零"):
            return 0
        if txt.isdigit():
            return int(txt)
        if txt in cn_map:
            return cn_map[txt]
        return None

    def listen_thread(self):
        self.tip_label.text = "🟢 正在监听"
        model = vosk.Model(MODEL_PATH)
        rec = vosk.KaldiRecognizer(model, 16000)
        rec.SetMaxAlternatives(0)
        rec.SetWords(False)
        if not self.use_vad:
            rec.SetVadMode(False)

        # 安卓原生AudioRecord，16k 单声道 PCM
        if sys.platform == "android":
            from android.audio import AudioRecord
            recorder = AudioRecord(
                samplingRate=16000,
                channelConfig=1,
                audioFormat=2,
                bufferSize=2048
            )
            recorder.startRecording()
        else:
            recorder = None

        while self.listening:
            if sys.platform == "android":
                data = recorder.read(2048)
            else:
                break

            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text = res.get("text","").strip()
                if text:
                    self.tip_label.text = f"识别：{text}"
                    val = self.parse_text(text)
                    if val is not None:
                        self.count = val
                        self.num_label.text = str(self.count)
        # 停止
        if sys.platform == "android":
            recorder.stop()
            recorder.release()
        self.tip_label.text = "已停止监听"

    def toggle_listen(self, inst):
        if not self.listening:
            self.listening = True
            self.btn_start.text = "停止监听"
            t = threading.Thread(target=self.listen_thread, daemon=True)
            t.start()
        else:
            self.listening = False
            self.btn_start.text = "开始监听"

    def clear_num(self, inst):
        self.count = 0
        self.num_label.text = "0"
        self.tip_label.text = "已清零"

class VoiceCounterApp(App):
    def build(self):
        Window.size = (360,720)
        return CounterLayout()

if __name__ == "__main__":
    VoiceCounterApp().run()
