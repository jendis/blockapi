import blockapi
import sys

def get_transfer(my_addrs, txs):
    amount = 0
    for tx in txs:
        if tx['addresses'][0] in my_addrs:
            amount += int(tx['value'])
    return amount

def query(xpub):
    myapi = blockapi.api.Btc2TrezorAPI(xpub)
    return myapi.get_txs()

def get_balances(xpub_data):
    addresses = [t['name'] for t in xpub_data['tokens']]
    transactions = xpub_data['transactions']
    balances = []

    for tx in transactions:
        amount = 0
        time = tx['blockTime']
        amount = -get_transfer(addresses, tx['vin'])
        amount += get_transfer(addresses, tx['vout'])
        balances.append((time, 'BTC', amount))

    balances.sort(key=lambda tup: tup[0], reverse=False)

    return balances

xpub = sys.argv[1]
#'xpub6CUGRUonZSQ4TWtTMmzXdrXDtypWKiKrhko4egpiMZbpiaQL2jkwSB1icqYh2cfDfVxdx4df189oLKnC5fSwqPfgyP3hooxujYzAu3fDVmz'
xpub_data = query(xpub)
balances = get_balances(xpub_data)

assert int(xpub_data['balance']) == sum(e[2] for e in balances)

print(balances)




