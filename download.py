"""Download stock data
"""
import sys
import os
import datetime
import time
import random
import multiprocessing
import shutil

from util import wget, get_stock_list
from util import JoinableQueue


NUM_PROCESS = 5
DATA_BASE_URL = ('http://ichart.finance.yahoo.com/table.csv?s={}&d={}&e={}'
                 '&f={}&g=d&a={}&b={}&c={}&ignore=.csv')


def download_stock(args):
    stock, output_dir = args
    from_date = datetime.date(1900, 1, 1)
    to_date = datetime.date(2099, 1, 1)
    url = DATA_BASE_URL.format(stock,
                               to_date.month - 1,
                               to_date.day,
                               to_date.year,
                               from_date.month - 1,
                               from_date.day,
                               from_date.year)
    print(url)
    output_path = os.path.join(output_dir, stock + '.csv')
    wget(url, output_path)


def download_all(output_path):
    """Download all stock data into output_path
    """
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.mkdir(output_path)

    queue = JoinableQueue(NUM_PROCESS, download_stock)
    queue.prepare()
    for (symbol, stock) in get_stock_list():
        queue.put((symbol, output_path))
    queue.done()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        download_all(sys.argv[1])
    else:
        print("Please provide the path to store the data")
