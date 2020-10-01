from datetime import datetime

import pytz

from blockapi.services import BlockchainAPI


class TrezorAPI(BlockchainAPI):
    """
    coins: bitcoin, litecoin
    API docs: https://github.com/trezor/blockbook/blob/master/docs/api.md
    Explorer:
    """

    active = True

    rate_limit = 0
    coef = 1e-8
    max_items_per_page = None
    page_offset_step = None
    confirmed_num = None
    xpub_support = True

    supported_requests = {
        'get_address': '/api/v2/address/{address}?page={page}&pageSize={page_size}&details={details}&contract= \
                         {contract_address}',
        'get_xpub': '/api/v2/xpub/{address}?page={page}&pageSize={page_size}&details={details}&tokens={tokens}',
        'get_tx': '/api/v2/tx/{tx_hash}',
    }

    def get_balance(self):
        if len(self.address) == 111:
            response = self.request('get_xpub',
                                    address=self.address,
                                    page = None,
                                    page_size=None,
                                    details=None,
                                    tokens=None)
        else:
            response = self.request('get_address',
                                    address=self.address,
                                    page=None,
                                    page_size=None,
                                    details=None,
                                    contract_address=None)

        if not response:
            return None

        retval = float(response.get('balance')) * self.coef
        return [{'symbol': self.symbol, 'amount': retval}]

    def get_txs(self, offset=None, limit=None, unconfirmed=False):
        if len(self.address) == 111:
            return self.request('get_xpub',
                                address=self.address,
                                page=offset,
                                page_size=limit,
                                details='txs',
                                tokens='used')
        else:
            response = self.request('get_address',
                                address=self.address,
                                page=offset,
                                page_size=limit,
                                details='txids',
                                contract_address=None)

            return [self.parse_tx(tx) for tx in response['txids']]

    def parse_tx(self, tx):
        txdata = self.request('get_tx',
                              tx_hash=tx)

        if self.address in txdata['vin'][0]['addresses']:
            direction = 'outgoing'
        else:
            direction = 'incoming'

        return {
            'date': datetime.fromtimestamp(txdata['blockTime'], pytz.utc),
            'from_address': txdata['vin'][0]['addresses'],
            'to_address': txdata['vout'][0]['addresses'],
            'amount': float(txdata['value']) * self.coef,
            'fee': float(txdata['fees']) * self.coef,
            'hash': tx,
            'confirmed': txdata['confirmations'],
            'is_error': False,
            'type': 'normal',
            'kind': 'transaction',
            'direction': direction,
            'status': 'confirmed' if txdata['confirmations'] > 0
            else 'unconfirmed',
            'raw': txdata
        }


class Btc1TrezorAPI(TrezorAPI):
    base_url = 'https://btc1.trezor.io'
    symbol = 'BTC'


class Btc2TrezorAPI(TrezorAPI):
    base_url = 'https://btc2.trezor.io'
    symbol = 'BTC'


class Ltc1TrezorAPI(TrezorAPI):
    base_url = 'https://ltc1.trezor.io'
    symbol = 'LTC'
