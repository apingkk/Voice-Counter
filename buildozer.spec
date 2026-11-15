[app]
title = VoiceCounter
package.name = voicecounter
package.domain = org.voice.counter
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.include_dirs = model
version = 0.1

requirements = python3,kivy,vosk,pyaudio
android.permissions = RECORD_AUDIO,INTERNET
android.api = 33
android.ndk = 25b
android.sdk = 24
android.ndk_api = 21

orientation = portrait
fullscreen = 0
log_level = 2
