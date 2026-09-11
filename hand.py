import cv2
import mediapipe as mp
import urllib.request
import os
import time

from gesture_detector import detect_gesture
from swipe_detector import SwipeDetector
from gesture_manager import GestureManager

from music_controller import (
    play_pause,
    next_song,
    previous_song,
    volume_up,
    volume_down,
    mute
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_FILE = "hand_landmarker.task"

MODEL_URL = (
    "https://storage.googleapis.com/"
    "mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/"
    "hand_landmarker.task"
)


# ============================================================
# DOWNLOAD MODEL IF NEEDED
# ============================================================

if not os.path.exists(MODEL_FILE):

    print("Hand model not found.")

    print("Downloading MediaPipe model...")

    try:

        urllib.request.urlretrieve(
            MODEL_URL,
            MODEL_FILE
        )

        print("Model downloaded successfully!")

    except Exception as error:

        print("Could not download model.")
        print("Error:", error)

        input("Press Enter to exit...")

        exit()


# ============================================================
# MEDIAPIPE
# ============================================================

BaseOptions = mp.tasks.BaseOptions

VisionRunningMode = (
    mp.tasks.vision.RunningMode
)

HandLandmarker = (
    mp.tasks.vision.HandLandmarker
)

HandLandmarkerOptions = (
    mp.tasks.vision.HandLandmarkerOptions
)


options = HandLandmarkerOptions(

    base_options=BaseOptions(
        model_asset_path=MODEL_FILE
    ),

    running_mode=VisionRunningMode.VIDEO,

    num_hands=1,

    min_hand_detection_confidence=0.5,

    min_hand_presence_confidence=0.5,

    min_tracking_confidence=0.5
)


# ============================================================
# CREATE LANDMARKER
# ============================================================

print("Loading hand detection model...")

landmarker = HandLandmarker.create_from_options(
    options
)

print("Hand detection model loaded!")


# ============================================================
# CREATE CONTROLLERS
# ============================================================

gesture_manager = GestureManager(
    cooldown=1.0
)


swipe_detector = SwipeDetector(
    threshold=0.20,
    cooldown=1.0
)


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)


if not camera.isOpened():

    print("Could not access camera.")

    landmarker.close()

    exit()


print("Camera connected!")
print()
print("======================================")
print("     AI GESTURE MUSIC CONTROLLER")
print("======================================")
print()
print("✋ Palm       → Play / Pause")
print("✊ Fist       → Mute")
print("👍 Thumb Up   → Volume Up")
print("👎 Thumb Down → Volume Down")
print("👉 Swipe Right → Next Song")
print("👈 Swipe Left  → Previous Song")
print()
print("Press Q to quit.")
print()


# ============================================================
# HAND CONNECTIONS
# ============================================================

connections = [

    # Thumb
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),

    # Index
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),

    # Middle
    (5, 9),
    (9, 10),
    (10, 11),
    (11, 12),

    # Ring
    (9, 13),
    (13, 14),
    (14, 15),
    (15, 16),

    # Pinky
    (13, 17),
    (17, 18),
    (18, 19),
    (19, 20),

    # Palm
    (0, 17)
]


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = camera.read()


    if not success:

        print("Could not read camera frame.")

        break


    # --------------------------------------------------------
    # Mirror camera
    # --------------------------------------------------------

    frame = cv2.flip(
        frame,
        1
    )


    # --------------------------------------------------------
    # Convert BGR → RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # --------------------------------------------------------
    # Create MediaPipe image
    # --------------------------------------------------------

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    timestamp_ms = (
        time.monotonic_ns() // 1_000_000
    )


    # --------------------------------------------------------
    # Detect hand
    # --------------------------------------------------------

    result = landmarker.detect_for_video(
        mp_image,
        timestamp_ms
    )


    # ========================================================
    # HAND FOUND
    # ========================================================

    if result.hand_landmarks:

        for hand_landmarks in result.hand_landmarks:


            # =================================================
            # GESTURE
            # =================================================

            gesture = detect_gesture(
                hand_landmarks
            )


            # =================================================
            # SWIPE
            # =================================================

            wrist_x = hand_landmarks[0].x

            swipe = swipe_detector.update(
                wrist_x
            )


            # =================================================
            # MUSIC COMMAND
            # =================================================

            action = None


            # -------------------------------------------------
            # SWIPE RIGHT → NEXT
            # -------------------------------------------------

            if swipe == "SWIPE_RIGHT":

                next_song()

                action = "NEXT SONG"


            # -------------------------------------------------
            # SWIPE LEFT → PREVIOUS
            # -------------------------------------------------

            elif swipe == "SWIPE_LEFT":

                previous_song()

                action = "PREVIOUS SONG"


            # -------------------------------------------------
            # STATIC GESTURES
            # -------------------------------------------------

            elif gesture_manager.should_trigger(
                gesture
            ):

                if gesture == "PALM":

                    play_pause()

                    action = "PLAY / PAUSE"


                elif gesture == "FIST":

                    mute()

                    action = "MUTE"


                elif gesture == "THUMB_UP":

                    volume_up()

                    action = "VOLUME UP"


                elif gesture == "THUMB_DOWN":

                    volume_down()

                    action = "VOLUME DOWN"


            # =================================================
            # DISPLAY
            # =================================================

            height, width, _ = frame.shape


            # -------------------------------------------------
            # Gesture text
            # -------------------------------------------------

            cv2.putText(
                frame,
                f"Gesture: {gesture}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2
            )


            # -------------------------------------------------
            # Action text
            # -------------------------------------------------

            if action:

                cv2.putText(
                    frame,
                    f"Action: {action}",
                    (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )


            # =================================================
            # DRAW LANDMARKS
            # =================================================

            for landmark in hand_landmarks:

                x = int(
                    landmark.x * width
                )

                y = int(
                    landmark.y * height
                )

                cv2.circle(
                    frame,
                    (x, y),
                    6,
                    (0, 255, 0),
                    -1
                )


            # =================================================
            # DRAW CONNECTIONS
            # =================================================

            for start, end in connections:

                x1 = int(
                    hand_landmarks[start].x * width
                )

                y1 = int(
                    hand_landmarks[start].y * height
                )

                x2 = int(
                    hand_landmarks[end].x * width
                )

                y2 = int(
                    hand_landmarks[end].y * height
                )

                cv2.line(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )


            # -------------------------------------------------
            # Status
            # -------------------------------------------------

            cv2.putText(
                frame,
                "21 Landmarks: ACTIVE",
                (20, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )


    # ========================================================
    # NO HAND
    # ========================================================

    else:

        cv2.putText(
            frame,
            "Show your hand",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            2
        )

        # Reset gesture lock
        gesture_manager.should_trigger(
            "NO HAND"
        )


    # ========================================================
    # DISPLAY CAMERA
    # ========================================================

    cv2.imshow(
        "AI Gesture Music Controller",
        frame
    )


    # ========================================================
    # QUIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

camera.release()

cv2.destroyAllWindows()

landmarker.close()

print()
print("Program closed.")