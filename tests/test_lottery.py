from brownie import Lottery, accounts, config, network
from web3 import Web3

# first test to see if the entrance fee in Lottery.sol is correct
# 1 eth = 2,898$, fee = $50,  2,898/1 = 50/x = 0.017.
def test_get_entrance_fee():
    account = accounts[0]
    lottery = Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from":account})
    assert lottery.getEntranceFee() >  Web3.toWei(0.015, 'ether')
    assert lottery.getEntranceFee() <  Web3.toWei(0.030, "ether")



    # Act
    # 2,000 eth / usd
    # usdEntryFee is 50
    # 2000/1 == 50/x == 0.025
    # expected_entrance_fee = Web3.toWei(0.025, "ether")
    #entrance_fee = lottery.getEntranceFee()
    # Assert
    #assert expected_entrance_fee == entrance_fee