"""
Stock Prophet:
 - Gather historical daily price
 - Find what happens 7 days after a big drop occurs
 - Predict whether to buy when a big drop occurs
"""
import os
import sys

from datetime import datetime
from util import get_stock_list
from analyze import analyze


def main():
    for (symbol, stock) in get_stock_list():
        analyze(symbol)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        DATA_PATH = sys.argv[1]
    else:
        DATA_PATH = datetime.now().strftime('%Y-%m-%d')

    # download_all(DATA_PATH)
    main()
