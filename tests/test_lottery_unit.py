from importlib.machinery import WindowsRegistryFinder
from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
    get_contract,
)
from scripts.deploy_lottery import deploy_lottery
import pytest

# first test to see if the entrance fee in Lottery.sol is correct
# 1 eth = 2,898$, fee = $50,  2,898/1 = 50/x = 0.017.
# note used this test in construction of smart contract & thus have edited out. Will have more robust unit testing below
"""
def test_get_entrance_fee():
    account = accounts[0]
    lottery = Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from":account})
    assert lottery.getEntranceFee() >  Web3.toWei(0.015, 'ether')
    assert lottery.getEntranceFee() <  Web3.toWei(0.030, "ether")
"""

def test_get_entrance_fee():
    # This is unit test, only run on local network > $ brownie test -k test_get_entrance_fee --network rinkeby
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # 2,800 eth/usd & usdEntryFee is $50
    # 1/2,800 = 0.000357
    # 50 * 0.000357 = 0.0178 = $50
    # Assert
    assert expected_entrance_fee == entrance_fee
    # $ brownie test -k test_get_entrace_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # Act / Assert
    # Essentially trying to "enter" the lottery before it has been opened should throw an error
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    # See that the first player is indeed this account that laucnhed the lottery
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2 # This is "Calculating winner state" is position 2 in smart contract


# Does lottery choose a winner, pay the winner & then reset to 0?
def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # enter with 1st, 2nd & 3rd accounts, ie diffrent people
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # break
    transaction = lottery.endLottery({"from": account})
    # note we made an "event" in the contract to witness this
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness( # dummy getting response from chainlink node
        request_id, 
        STATIC_RNG, # random number 777 
        lottery.address, 
        {"from": account} # note makes state change
    )
    starting_balance_of_account = account.balance() # see balance of the winning account
    balance_of_lottery = lottery.balance() # see balance of lottery contract 
    assert lottery.recentWinner() == account # 777 % 3 = 0 --> thus out account is the winner in this test!
    assert lottery.balance() == 0 # lottery should be empty once funds have been given to winner
    assert account.balance() == starting_balance_of_account + balance_of_lottery # acount should end with all winings
