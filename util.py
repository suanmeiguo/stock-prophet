"""Utility functions
"""
import os
import sys
import subprocess
import multiprocessing
import time


SYMBOL_LIST_PATH = 'static/NYSE.txt'


def wget(url, output_path):
    devnull = open(os.devnull, 'w')
    return_code = subprocess.call(['wget', '-O', output_path, url],
                                  stdout=devnull,
                                  stderr=devnull)
    if return_code == 0:
        return True
    return False


def get_stock_list():
    """Read stock symbol into a list
    """
    header = True

    stock_list = open(SYMBOL_LIST_PATH, 'r')
    result = []

    for line in stock_list:
        if header:
            header = False
            continue
        [symbol, company] = map(lambda x: x.strip(), line.split('\t'))
        result.append((symbol, company))

    stock_list.close()
    return result


class JoinableQueue:
    '''multiprocessing using joinable queue
    joinable queue example:
    http://stackoverflow.com/questions/6672525/multiprocessing-queue-in-python
    '''
    def __init__(self, num_proc, func, max_queue=None):
        '''num_proc: number of process to use
        func: the function that do the actual work
        max_queue: maximum number of items can be stored in the queue
        '''
        self.num_proc = num_proc
        self.func = func
        self.queue = multiprocessing.JoinableQueue()
        self.max_queue = max_queue
        self.proc = []  # list of all processes created

    def worker(self):
        '''fetch task from the queue'''
        for item in iter(self.queue.get, None):
            self.func(item)
            self.queue.task_done()
        self.queue.task_done()

    def prepare(self):
        '''prepare all process'''
        if self.num_proc > 1:
            for i in range(self.num_proc):
                self.proc.append(multiprocessing.Process(target=self.worker))
                self.proc[-1].daemon = True
                self.proc[-1].start()
            self.queue.join()

    def put(self, item):
        if self.num_proc > 1:
            if self.max_queue:
                while self.queue.qsize() > self.max_queue:
                    time.sleep(1)
            self.queue.put(item)
        else:
            self.func(item)

    def done(self):
        '''finalize all processes'''
        if self.num_proc > 1:
            for p in self.proc:
                self.queue.put(None)
            self.queue.join()
            for p in self.proc:
                p.join()
