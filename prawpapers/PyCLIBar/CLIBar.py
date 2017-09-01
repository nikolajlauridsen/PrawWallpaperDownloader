from .pacer import Pacer


class CLIBar(Pacer):
    def __init__(self, bar_width=20, progress_char='=', fill_char=' ',
                 _max=0):
        super().__init__()
        self.max = _max

        self.bar_length = bar_width - 2
        self.progress_char = progress_char
        self.fill_char = fill_char

        # The widest bar returned, used to pad with spaces
        # Otherwise it will look weird when printed with \r as line end
        self.max_width = 0

    def start(self, _max=None):
        if _max:
            self.set_max(_max)

        super(CLIBar, self).start()

    def get_fraction(self):
        """
        Get progress as a fraction (number between 0.0 and 1.0)
        """
        if self.max == 0:
            fraction = 1.0
        else:
            try:
                fraction = self.progress / self.max
            except ZeroDivisionError:
                fraction = 0.0

        assert 0.0 <= fraction <= 1.0, 'Fraction must be between 0.0 and 1.0'
        return fraction

    def get_bar(self):
        """
        Returns progress bar as a string
        """
        if not self.running:
            # If the pacer isn't running, we're going to assume it's because
            # max steps has been reached and the pacer has reset automatically
            return "[{}]".format(self.progress_char*self.bar_length)

        # Remove 2 from bar length since we have [ and ]
        progress = int(self.bar_length * self.get_fraction())
        return "[{}{}]".format(self.progress_char * progress,
                               self.fill_char * (self.bar_length-progress))

    def get_progress(self):
        """
        Returns progress indicator I.e. 10/20
        """
        return "{}/{}".format(self.progress, self.max)

    def get_progress_bar(self, bar=True, progress=True, est=True):
        # String var to hold the bar
        pbar = ""

        if bar:
            pbar += self.get_bar()
            pbar += " "

        if progress:
            pbar += self.get_progress()
            pbar += " "

        if est:
            pbar += "est. Remaining: {} s"\
                .format(round(self.get_estimated_remaining()))

        if len(pbar) > self.max_width:
            self.max_width = len(pbar)
        else:
            pbar += " " * (self.max_width - len(pbar))

        return pbar
