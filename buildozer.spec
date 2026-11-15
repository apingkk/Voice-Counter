[app]
title = VoiceCounter
package.name = voicecounter
package.domain = org.voice.counter
source.dir = .
source.include_exts = py
requirements = python3,kivy,vosk,android
android.permissions = RECORD_AUDIO
android.api = 33
android.ndk = 25b
android.sdk = 24
android.accept_sdk_license = True
android.add_assets =
