from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, network, config
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
        # gets a verify from config, but if there is none, then False
    )
    print("Deployed lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]  # most recent deployment of the lottery
    starting_tx = lottery.startLottery({"from": account})  # adding starting_tx = &...
    starting_tx.wait(1)  # making it wait 1xblock for completion
    print("The lottery has started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]  # most recent deployment of the lottery
    value = lottery.getEntranceFee() + 1000000000  # add a little bit of gas to be sure
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)  # making it wait 1xblock for completion
    print("You have entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]  # most recent deployment of the lottery
    # fund the contract to call randomness
    tx = fund_with_link(lottery.address)
    tx.wait(1)  # to be sure it waits
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(180)
    # ^^kept time at 60secs
    print(f"{lottery.recentWinner()} is the Lottery Winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
