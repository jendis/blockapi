from blockapi.services import (
    BlockchainAPI
)
import json
import dateutil
from datetime import datetime
import pytz

class BlockonomicsAPI(BlockchainAPI):
    """
    Bitcoin
    API docs: https://www.blockonomics.co/views/api.html
    Explorer: https://www.blockonomics.co
    """

    active = True

    currency_id = 'bitcoin'
    base_url = 'https://www.blockonomics.co/api'
    rate_limit = 30
    coef = 1e-8
    max_items_per_page = None
    page_offset_step = None
    confirmed_num = None

    supported_requests = {
        'get_balance': '/balance',
        'get_txs': '/searchhistory',
        'get_tx': '/tx_detail?txid={txid}'
    }

    # def process_error_response(self, response):
    #     if response.text == 'Invalid Bitcoin Address':
    #         raise AddressNotExist()
    #     # else
    #     super().process_error_response(response)

    def get_balance(self):
        body = '{"addr": "' + self.address + '"}'
        response = self.request('get_balance', body=body)
        if not response.get('response'):
            return 0

        balance = sum(r['confirmed'] * self.coef for r in response['response'])
        return balance

    def get_txs(self, offset=None, limit=None, unconfirmed=False):
        body = '{"addr": "' + self.address + '"}'
        txs = self.request('get_txs',
                           body=body)

        return [self.parse_tx(t) for t in txs['history']]


    def parse_tx(self,tx):
        tx_data = self.request('get_tx', 
                               txid=tx['txid'])

        amount = tx['value']
        from_address = [adr['address'] for adr in tx_data['vin']]
        to_address = [adr['address'] for adr in tx_data['vout']]

        if amount < 0:
            direction = 'outgoing'
        else:
            direction = 'incoming'

        return {
            'date': datetime.fromtimestamp(tx['time'], pytz.utc),
            'from_address': from_address,
            'to_address': to_address,
            'amount': amount * self.coef,
            'fee': tx_data['fee'] * self.coef,
            'gas': {},
            'hash': tx['txid'],
            'confirmed': None,
            'is_error': False,
            'type': 'normal',
            'kind': 'transaction',
            'direction': direction,
            'raw': tx 
        }

