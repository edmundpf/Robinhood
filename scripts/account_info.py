from Robinhood import Robinhood
from datatype_tools.lib import *
from print_tools.printer import Printer

#::: Defs :::

#: Get Transfers

def get_transfers(transfers):

    withdraws = 0
    deposits = 0

    for transfer in transfers:
        if not transfer['scheduled'] and transfer['rhs_state'] == 'submitted' and transfer['direction'] == 'withdraw':
            withdraws += float(transfer['amount'])
        if not transfer['scheduled'] and transfer['rhs_state'] == 'submitted' and transfer['direction'] == 'deposit':
            deposits += float(transfer['amount'])
    return withdraws, deposits

#: Get Trades

def get_trades(options):

    gains = 0
    losses = 0
    wins = 0
    defeats = 0
    options_trades = {}

    for option in options:
        if option['state'] != 'cancelled':
            if option['direction'] == 'credit':
                amt = float(option['processed_premium'])
            elif option['direction'] == 'debit':
                amt = float(option['processed_premium']) * -1 if float(option['processed_premium']) != 0 else 0
            try:
                time = option['legs'][0]['executions'][0]['timestamp'].get_iso_date(date_format='yyyymmdd', delimiter='-')
            except:
                time = ''
            url = option['legs'][0]['option']
            option_id = url[(url.find_nth('/', 5) + 1):(len(url) - 1)]
            if option_id not in options_trades:
                options_trades[option_id] = {
                    'amt': amt,
                    'symbol': option['chain_symbol'],
                    'date': time['date'] if 'date' in time else '',
                    'time': time['time'] if 'time' in time else '',
                    'url': url
                }
            else:
                options_trades[option_id]['amt'] += amt
                if options_trades[option_id]['time'] == '':
                    options_trades[option_id]['time'] = time

    for trade in options_trades:
        data = t.get_url(options_trades[trade]['url'])
        options_trades[trade].update({
            'strike_price': data['strike_price'],
            'expiration_date': data['expiration_date'],
            'option_type': data['type']
        })
        if options_trades[trade]['amt'] >= 0:
            amt_color = '[bold:seaGreen]'
            gains += options_trades[trade]['amt']
            wins += 1
        elif options_trades[trade]['amt'] < 0:
            amt_color = '[bold:magenta]'
            losses += options_trades[trade]['amt']
            defeats += 1
        date = options_trades[trade]['expiration_date']
        symbol = options_trades[trade]['symbol']
        option_type = options_trades[trade]['option_type']
        amt = float(options_trades[trade]['amt']).round(2)
        p.bullet(p.format(f'{symbol} {date} {option_type}: {amt_color}{amt}', ret=True))
    net = gains + losses
    return gains, losses, net, wins, defeats

#::: Driver :::

p = Printer()
t = Robinhood()
t.login()

p.format('\n[bold:purple]Robinhood Account Info:', log=True)
p.chevron(f'User: {t.username}\n')

account_info = t.get_account()
margin = account_info['margin_balances']
transfers = t.consume_pages(t.get_transfers())
options = t.consume_pages(t.get_options_orders())
orders = t.consume_pages(t.order_history())

withdraws, deposits = get_transfers(transfers)
gains, losses, net, wins, defeats = get_trades(options)

buy_power = float(margin['day_trade_buying_power']).round(2)
av_withdraw = float(margin['cash_available_for_withdrawal']).round(2)
unsettled = float(margin['unsettled_funds']).round(2)

print('')
p.arrow(p.format(f"[bold:green]Buying Power: [reset]${buy_power}", ret=True))
p.arrow(p.format(f"[bold:purple]Available for Withdrawal: [reset]${av_withdraw}", ret=True))
p.arrow(p.format(f"[bold:yellow]Unsettled Funds: [reset]${unsettled}\n", ret=True))
p.arrow(p.format(f"[bold:orange]Deposits: [reset]${deposits.round(2)}", ret=True))
p.arrow(p.format(f"[bold:blue]Withdrawals: [reset]${withdraws.round(2)}\n", ret=True))
p.arrow(p.format(f"[bold:seaGreen]Gains: [reset]${gains.round(2)} ({wins} wins)", ret=True))
p.arrow(p.format(f"[bold:magenta]Losses: [reset]${losses.round(2)} ({defeats} losses)", ret=True))
p.arrow(p.format(f"[bold:orange]Net: [reset]${net.round(2)} ({wins}-{defeats})", ret=True))

#::: END PROGRAM :::
