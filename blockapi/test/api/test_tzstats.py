from pytest import mark

from blockapi.api.tzstats import TzStatsAPI
from blockapi.test_init import test_addresses


class TestTzscanAPI:

    ADDRESS = test_addresses["XTZ"][0]
    REWARD_ADDRESS = test_addresses["XTZ"][1]

    def test_init(self):
        api = TzStatsAPI(address=self.ADDRESS)
        assert api

    @mark.vcr()
    def test_get_account(self):
        api = TzStatsAPI(address=self.REWARD_ADDRESS)
        result = api.get_account()

        assert "address" in result
        assert "manager" in result
        assert "delegate" in result
