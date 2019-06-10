import os
import time
import sys
from datetime import datetime
from Robinhood import Robinhood
from datatype_tools.lib import Float
from file_tools.json_file import import_json

def flush_print(text, lines, flush=True):
    if flush:
        for i in range(lines):
            sys.stdout.write("\033[K")
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
    print(text, end='\r', flush=True)

t = Robinhood()
t.login()
runs = 0
lines = 0
options = import_json('../data/options_watch.json', path=os.path.abspath(__file__))

try:
    while True:
        cur_time = int(datetime.now().strftime('%H%M'))
        time_stamp = datetime.now().strftime('%H:%M:%S')
        spy = t.quote_data('SPY')
        spy_price = float(spy['last_trade_price']).round(3) if cur_time >= 930 else float(spy['last_extended_hours_trade_price']).round(3)
        print_str = f'{time_stamp} - SPY ({spy_price})\n'
        lines = 1
        runs += 1
        for i, option in enumerate(options):
            opt = t.find_option_by_strike(option['ticker'], option['date'], option['strike'], option['type'])
            opt_data = t.get_option_market_data(opt['id'])
            opt_type = 'C' if option['type'] == 'call' else 'P'
            opt_text = f"{option['ticker']}-{option['strike']}-{opt_type}-{option['date'].replace('-', '')}"
            quote_data = t.quote_data(option['ticker'])
            quote = float(quote_data['last_trade_price']).round(3) if cur_time >= 930 else float(quote_data['last_extended_hours_trade_price']).round(3)
            mark = float(opt_data['adjusted_mark_price']).round(3)
            ask_price = float(opt_data['ask_price']).round(3)
            ask_count = opt_data['ask_size']
            bid_price = float(opt_data['bid_price']).round(3)
            bid_count = opt_data['bid_size']
            delta = float(opt_data['delta']).round(3)
            theta = float(opt_data['theta']).round(3)
            volume = opt_data['volume']
            if i != (len(options) - 1):
                print_str += f'{opt_text} | {mark} | {quote} | Ask: {ask_price} - {ask_count} | Bid: {bid_price} - {bid_count} | Vol: {volume} | Δ{delta} | θ{theta}\n'
                lines += 1
            else:
                print_str += f'{opt_text} | {mark} | {quote} | Ask: {ask_price} - {ask_count} | Bid: {bid_price} - {bid_count} | Vol: {volume} | Δ{delta} | θ{theta}'
            if runs == 1:
                flush_print(print_str, lines, flush=False)
            else:
                flush_print(print_str, lines)
        time.sleep(3)
except KeyboardInterrupt:
    flush_print('', lines)
    print('Goodbye.')
