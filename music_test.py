from music_controller import (
    play_pause,
    next_song,
    previous_song,
    volume_up,
    volume_down,
    mute
)

print("Testing music controls...")

print("1. Play/Pause")
play_pause()

input("Press Enter for next song...")

print("2. Next Song")
next_song()

input("Press Enter for previous song...")

print("3. Previous Song")
previous_song()

input("Press Enter for volume up...")

print("4. Volume Up")
volume_up()

input("Press Enter for volume down...")

print("5. Volume Down")
volume_down()

input("Press Enter for mute...")

print("6. Mute")
mute()

print("Done!")