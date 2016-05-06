"""Analyze functions
"""
import sys
import os

from datetime import datetime, timedelta
from config import DROP_THRESHOLD, COMEBACK_PERIOD


DATA_PATH = datetime.now().strftime('%Y-%m-%d')


def parse_data(symbol):
    """Parse daily price into a list
    """
    stock_file = os.path.join(DATA_PATH, symbol + '.csv')
    if not os.path.exists(stock_file):
        raise Exception("Cannot find {}".format(stock_file))

    result = []
    stock_reader = open(stock_file, 'r')
    skip_header = True
    for line in stock_reader:
        if skip_header:
            skip_header = False
            continue
        [Date, Open, High, Low, Close, Volume, AdjClose] = line.split(',')
        result.append((Date, float(Close)))
    stock_reader.close()
    return sorted(result, key=lambda e: e[0])


def analyze(symbol, detail=False):
    """How many times in history the price comes back to the same level
    before a big drop (10%) within 10 stock days
    """
    price_list = parse_data(symbol)
    if len(price_list) < COMEBACK_PERIOD:
        return

    t0, p0 = None, None
    big_drop_flag = False
    drop_count = 0
    recover_count = 0

    for t1, p1 in price_list:
        t1 = datetime.strptime(t1, "%Y-%m-%d")
        if t0 is None:
            t0 = t1
            p0 = p1
            continue

        if big_drop_flag:  # there was a big drop
            if t1 > t0 + timedelta(COMEBACK_PERIOD):
                # reset
                big_drop_flag = False
                p0 = p1
                t0 = t1
                if detail:
                    print("{}: more than {}% drop on {}"
                          .format(symbol,
                                  DROP_THRESHOLD,
                                  t0))
            elif p1 >= p0:
                recover_count += 1
                if detail:
                    print("{}: more than {}% drop on {} and recovered on {}"
                          .format(symbol,
                                  DROP_THRESHOLD,
                                  t0,
                                  t1))
                p0 = p1
                t0 = t1
                big_drop_flag = False

        else:  # check for big drop
            if (p0 - p1) / p0 * 100 > DROP_THRESHOLD:
                big_drop_flag = True
                drop_count += 1
                # import pdb; pdb.set_trace()
            else:
                p0 = p1
                t0 = t1

    if drop_count != 0:
        recover_rate = "{0:.2f}".format(recover_count * 100.0 / drop_count)
        report = ("{}: {} has {} big drop, {} recovered within {} days."
                  .format(
                      recover_rate,
                      symbol,
                      drop_count,
                      recover_count,
                      COMEBACK_PERIOD))

        if big_drop_flag:
            report += " And {} just had a big drop in last {} days".format(
                symbol,
                COMEBACK_PERIOD)

        print(report)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        DATA_PATH = sys.argv[2]
    symbol = sys.argv[1].upper()
    analyze(symbol, True)
