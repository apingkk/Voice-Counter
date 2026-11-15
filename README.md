# Voice Counter
低延迟离线语音计数器，基于 Vosk 离线语音识别 + Kivy，GitHub Actions 自动打包安卓APK。

## 功能
- 离线识别，**不需要联网**
- 两种模式切换：
  - VAD关闭：极致低延迟（目标 <100ms），适合快速计数
  - VAD开启：等待停顿再识别，体验更自然
- 支持指令：直接说数字、说「清零 / 归零」重置计数

## 打包说明
- 本仓库使用 GitHub Actions 云端自动构建APK
- 构建时自动下载 vosk-model-small-cn-0.22 中文离线模型，无需手动上传模型文件
- 产出：debug 版本安卓APK

## 权限
仅需要：麦克风录音权限

## 编译栈
- Kivy：图形界面
- Vosk：离线语音识别
- python-for-android / buildozer：安卓打包
