from Robinhood import Robinhood
from datatype_tools.lib import *
import datetime
import time
t = Robinhood()
t.login()
while True:
    quote = float(t.get_quote('ZNGA')['last_trade_price']).round(2)
    if quote < 6.5:
        option = t.get_option_market_data(t.find_option('ZNGA', '2019-06-14', 'call', 'otm', 0, False)['id'])
    else:
        option = t.get_option_market_data(t.find_option('ZNGA', '2019-06-14', 'call', 'itm', 0, False)['id'])
    cur_price = float(option['adjusted_mark_price']).round(2)
    bid_price = float(option['bid_price']).round(2)
    bidders = option['bid_size']
    ask_price = float(option['ask_price']).round(2)
    askers = option['ask_size']
    cur_time = datetime.datetime.now().strftime('%m/%d/%Y-%H:%M:%S')
    print(f'{cur_time}: Mark (${cur_price}) | Bid ({bidders} - ${bid_price}) | Ask ({askers} - ${ask_price}) | ${quote}', sep='', end='\r', flush=True)
    time.sleep(3)
