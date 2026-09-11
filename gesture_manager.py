import time


class GestureManager:

    def __init__(self, cooldown=1.0):

        self.cooldown = cooldown

        self.last_trigger_time = 0

        self.gesture_locked = False


    def should_trigger(self, gesture):

        current_time = time.time()


        # No valid gesture
        if gesture in ["UNKNOWN", "NO HAND", None]:

            # Reset the lock when hand returns to neutral
            self.gesture_locked = False

            return False


        # Prevent repeated triggering
        if self.gesture_locked:

            return False


        # Check cooldown
        if (
            current_time - self.last_trigger_time
            < self.cooldown
        ):

            return False


        # Trigger this gesture
        self.last_trigger_time = current_time

        self.gesture_locked = True

        return True