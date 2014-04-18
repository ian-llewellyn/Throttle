#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
The Throttle module provides one class and one function that can be used to
set a maximum throughput on data passing between files or applications.
"""

def speed_str(speed):
    """
    speed_str(float speed) -> string with , separators and B/s | KiB/s | MiB/s
    """
    if speed > 1024*1024:
        return '{:,.4}'.format(speed/1024/1024) + ' MiB/s'
    elif speed > 1024:
        return '{:,.4}'.format(speed/1024) + ' KiB/s'
    else:
        return '{:,.4}'.format(speed) + ' B/s'

class Throttle(object):
    """
    The Throttle class implements a file copier that limits the throughput to a
    maximum value specified at the time of creation.

    Instantiate the class using the following syntax:
    Speedometer(in_fd, out_fd, info_fd, speed)

    For example:
    throttle = Throttle(sys.stdin, file('output.data'), sys.stderr, 9600)
    """

    def __init__(self, in_fd, out_fd, info_fd, speed_bps):
        """
        This method sets up the instance of Speedometer and runs it.
        """
        self.in_fd = in_fd
        self.out_fd = out_fd
        self.info_fd = info_fd
        self.total_bytes = 0
        self.start_time = None
        self.total_time = 0.0
        self.average_speed = 0.0
        self.speed_bps = speed_bps
        self.segments = 4
        self.chunk_size = speed_bps / self.segments or 1
        self.inner_loop_start_time = None

    def start(self):
        """
        This method actually starts the transfer and writes out the statistics.
        """
        import datetime, time

        with self.in_fd as in_file:
            with self.out_fd as out_file:
                with self.info_fd as info_file:
                    self.total_bytes = 0
                    self.start_time = datetime.datetime.now()
                    while 1:
                        data = in_file.read(1024*14)
                        data_len = len(data)
                        if data_len == 0:
                            break
                        while len(data) > 0:
                            self.inner_loop_start_time = datetime.datetime.now()

                            out_file.write(data[:self.chunk_size])

                            self.total_bytes += len(data[:self.chunk_size])
                            self.total_time = (datetime.datetime.now() -
                                self.start_time).total_seconds()
                            self.average_speed = self.total_bytes / self.total_time

                            info_file.write(
                                '\033[0GTotal bytes: %d ' % self.total_bytes +
                                'Total time: %.3f ' % self.total_time +
                                'Average speed: %s\033[K' % speed_str(
                                    self.average_speed)
                                )

                            data = data[self.chunk_size:]

                            duration = (datetime.datetime.now() - self.inner_loop_start_time).total_seconds()
                            sleep_time = (1.0 / self.segments) - duration
                            if sleep_time > 0:
                                time.sleep(sleep_time)

                    info_file.write('\n')

    def reset(self):
        """
        reset all counters to zero and bring the instance back to
        post-instantiate state.
        """
        self.__init__()

if __name__ == '__main__':
    import sys
    THROTTLE = Throttle(sys.stdin, sys.stdout, sys.stderr, int(sys.argv[1]))
    THROTTLE.start()
