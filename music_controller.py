import pyautogui
import time


def play_pause():
    print("▶️ Play/Pause")
    pyautogui.press("playpause")


def next_song():
    print("⏭️ Next Song")
    pyautogui.press("nexttrack")


def previous_song():
    print("⏮️ Previous Song")
    pyautogui.press("prevtrack")


def volume_up():
    print("🔊 Volume Up")
    pyautogui.press("volumeup")


def volume_down():
    print("🔉 Volume Down")
    pyautogui.press("volumedown")


def mute():
    print("🔇 Mute")
    pyautogui.press("volumemute")