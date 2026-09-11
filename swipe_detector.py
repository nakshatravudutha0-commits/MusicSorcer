import time


class SwipeDetector:

    def __init__(
        self,
        threshold=0.20,
        cooldown=1.0
    ):

        self.threshold = threshold

        self.cooldown = cooldown

        self.start_x = None

        self.start_time = None

        self.last_swipe_time = 0


    # ========================================================
    # PROCESS HAND POSITION
    # ========================================================

    def update(self, wrist_x):

        current_time = time.time()


        # ----------------------------------------------------
        # Start tracking
        # ----------------------------------------------------

        if self.start_x is None:

            self.start_x = wrist_x

            self.start_time = current_time

            return None


        # ----------------------------------------------------
        # Check cooldown
        # ----------------------------------------------------

        if (
            current_time - self.last_swipe_time
            < self.cooldown
        ):

            return None


        # ----------------------------------------------------
        # Calculate movement
        # ----------------------------------------------------

        movement = wrist_x - self.start_x


        # ====================================================
        # SWIPE RIGHT
        # ====================================================

        if movement > self.threshold:

            self.last_swipe_time = current_time

            self.start_x = wrist_x

            return "SWIPE_RIGHT"


        # ====================================================
        # SWIPE LEFT
        # ====================================================

        if movement < -self.threshold:

            self.last_swipe_time = current_time

            self.start_x = wrist_x

            return "SWIPE_LEFT"


        # ----------------------------------------------------
        # Reset tracking after too much time
        # ----------------------------------------------------

        if (
            current_time - self.start_time
            > 1.0
        ):

            self.start_x = wrist_x

            self.start_time = current_time


        return None