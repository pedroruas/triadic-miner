# -*- coding: utf-8 -*-
from timeit import default_timer


class Timer(object):
    DONE_MSG = "Done in {:.4f} seconds\n"
    start_time = None

    @staticmethod
    def start(begin_message):
        print(begin_message)
        Timer.start_time = default_timer()

    @staticmethod
    def stop():
        elapsed_time = default_timer() - Timer.start_time
        print(Timer.DONE_MSG.format(elapsed_time))

        return elapsed_time
