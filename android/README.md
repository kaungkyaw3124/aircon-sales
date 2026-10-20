# Aircon Sales (Android)

## Run on a phone or emulator

The debug app talks to `http://127.0.0.1:8000/`. Two links carry that to the VPS:
phone → PC (`adb reverse`) and PC → VPS (SSH tunnel).

1. **SSH tunnel** (PowerShell window, leave it open):
   ```
   ssh -p 10066 -N -L 127.0.0.1:8000:127.0.0.1:8000 administrator@93.127.132.69
   ```
2. **adb reverse.** Connect the phone by USB (or start the emulator), then in a second window from `D:\claude\p1\android`:
   ```
   .\run-on-phone.ps1
   ```
   Or by hand:
   ```
   & "D:\android studio\platform-tools\adb.exe" devices
   & "D:\android studio\platform-tools\adb.exe" reverse tcp:8000 tcp:8000
   ```
   Do this again after every reconnect or emulator restart.
3. **Xiaomi phones:** Settings → Additional settings → Developer options → turn on **Install via USB**
   (and **USB debugging**).
4. Press **Run ▶** in Android Studio. Log in with `owner` / `owner123` (dev data only).

### Common errors

| Error | Fix |
|---|---|
| "Can't reach the server" in the app | The SSH tunnel (step 1) is closed, or `adb reverse` (step 2) is missing. Redo both. |
| `INSTALL_FAILED_USER_RESTRICTED` | Xiaomi: turn on **Install via USB** (step 3), and tap Allow on the phone when asked. |
| `run-on-phone.ps1` says "No device connected" | Check the cable, unlock the phone, accept the "Allow USB debugging?" prompt. |
