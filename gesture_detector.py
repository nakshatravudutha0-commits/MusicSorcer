import math


# ============================================================
# DISTANCE BETWEEN TWO POINTS
# ============================================================

def distance(p1, p2):

    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


# ============================================================
# CHECK WHETHER A FINGER IS OPEN
# ============================================================

def finger_is_open(landmarks, tip_id, pip_id):

    return landmarks[tip_id].y < landmarks[pip_id].y


# ============================================================
# GESTURE DETECTION
# ============================================================

def detect_gesture(hand_landmarks):

    lm = hand_landmarks


    # --------------------------------------------------------
    # Finger states
    # --------------------------------------------------------

    index_open = finger_is_open(lm, 8, 6)

    middle_open = finger_is_open(lm, 12, 10)

    ring_open = finger_is_open(lm, 16, 14)

    pinky_open = finger_is_open(lm, 20, 18)


    open_count = sum([
        index_open,
        middle_open,
        ring_open,
        pinky_open
    ])


    # ========================================================
    # ✋ OPEN PALM
    # ========================================================

    if open_count == 4:

        return "PALM"


    # ========================================================
    # ✌️ PEACE
    # ========================================================

    if (
        index_open
        and middle_open
        and not ring_open
        and not pinky_open
    ):

        return "PEACE"


    # ========================================================
    # ☝️ ONE FINGER
    # ========================================================

    if (
        index_open
        and not middle_open
        and not ring_open
        and not pinky_open
    ):

        return "ONE"


    # ========================================================
    # THUMB GESTURES
    # ========================================================

    if open_count == 0:

        thumb_tip = lm[4]

        thumb_ip = lm[3]

        wrist = lm[0]

        # -----------------------------------------------
        # 👍 THUMB UP
        # -----------------------------------------------

        if (
            thumb_tip.y < thumb_ip.y
            and
            thumb_tip.y < wrist.y - 0.05
        ):

            return "THUMB_UP"


        # -----------------------------------------------
        # 👎 THUMB DOWN
        # -----------------------------------------------

        if (
            thumb_tip.y > thumb_ip.y
            and
            thumb_tip.y > wrist.y + 0.05
        ):

            return "THUMB_DOWN"


        # -----------------------------------------------
        # ✊ FIST
        # -----------------------------------------------

        return "FIST"


    # ========================================================
    # UNKNOWN
    # ========================================================

    return "UNKNOWN"