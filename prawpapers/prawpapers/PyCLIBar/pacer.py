import time


class Pacer:
    def __init__(self):
        """
        Tracks the pace of a 'process' and calculates estimated time remaining
        """
        self.start_time = None
        self.max = 0       # Maximum elements to be processed
        self.progress = 0  # Amount of elements processed
        self.pace = 0.0    # Current pace (Operations pr. second)
        self.running = False

    def start(self, start=None):
        """
        Start the pacer
        :param start: Optional, start the pacer with an amount of steps taken,
                      used for a continued process
                      (WARNING! Not yet implemented!)
        """
        assert self.max >= 1, "Max is less than zero (you cannot expect < 1 step)"

        # If it's a resumed process you might want to start somewhere not at 0
        if start:
            self.progress = start
        self.start_time = time.time()
        self.running = True

    def set_max(self, _max):
        """
        Set the amount of steps in the process to be timed
        :param _max: int amount of steps.
        """
        assert _max >= 1, "Max is less than zero (you cannot expect < 1 step)"
        self.max = _max

    def reset(self):
        """
        Shorthand making calling the initializer a bit prettier
         also stops the pacer
        """
        self.__init__()

    def step(self, amount=1):
        """
        Similar to TKinters progress bar, add one to progress
        :param amount: kwarg allowing for bigger steps (defaults to 1)
        """
        self.progress += amount

        # Once the process is finished we reset the pacer
        if self.progress >= self.max:
            self.reset()
            return

        if self.start_time:
            self.update_pace()

    def get_estimated_remaining(self):
        """
        Get the estimated remaining time for the 'process'
        :return: Estimated remaining time in seconds
        """
        # TODO: Consider resumed processes

        remaining_elements = self.max - self.progress
        if remaining_elements < 1:
            return 0
        else:
            self.update_pace()
            try:
                remaining = (self.max - self.progress) / self.pace
            except ZeroDivisionError:
                # It's a shot in the dark, but it's much prettier than 999
                remaining = self.max * 2

            return remaining

    def update_pace(self):
        """
        Update pace (steps pr. second)
        """
        elapsed = self.get_elapsed()
        if elapsed <= 0:
            self.pace = 0
        else:
            self.pace = self.progress / self.get_elapsed()

    def get_pace(self):
        """
        Get steps pr. second
        :return: steps pr. second as a float
        """
        return self.pace

    def get_elapsed(self):
        """
        Get elapsed time since pacer was started
        :return: Elapsed time as a float
        """
        if self.running:
            return time.time() - self.start_time
        else:
            return None
