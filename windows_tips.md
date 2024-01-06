# window tips--窗口

首先，同时按alt+tab，激活目标窗口
然后按Windows键和上下左右可调整窗口

## win11右键默认显示更多选项

以管理员身份启动cmd, 执行以下命令

```cmd
reg.exe add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve

taskkill /f /im explorer.exe & start explorer.exe
```
