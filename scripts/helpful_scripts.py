from brownie import (
    network,
    config,
    accounts,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    # new way to get account is accounts.load("id")
    if index:
        return accounts[index]  # if there is an index from local or forked
    if id:
        return accounts.load(id)  # if there is an ID
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]  # if it is local just pass 0th account
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """This function will grab the contract addresses fro mthe brownie config if definrd otherwise it will deploy a mock of the contract and return the mock contract.

    Args:
        contract_name (string)

    Returns:
        brownie.network.contract.ProjectContract: The most recently deployed version of theis contract.

    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # for local only, no need for a mock in a fork
        if len(contract_type) <= 0:
            # check to see if 1 of the environments has already been deployed
            # MockV3Aggregators.length is checking how many V# Aggregators have been deployed, if none then deploy mocks
            deploy_mocks()
        contract = contract_type[-1]
        # same as doing MockV3Aggregator [-1], which is grabbing the most recent deployment of the MockV3Aggregator
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # always needing the address and ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
        # MockV3Aggregator has a '.abi' attribute that returns ABI
    return contract


DECIMALS = 8  # value hard coded for deploy_mocks()
INITIAL_VALUE = 200000000000  # value hard coded for deploy_mocks()

# A way to deploy the mock price fee (same as the one from brownie_fund_me).
def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=250000000000000000
):
    # .25 Link
    account = account if account else get_account()
    # ^^acc will be acc=none if acc doesn't exist, otherwise get account
    link_token = link_token if link_token else get_contract("link_token")
    # ^^same for the link token
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funded Contract!")
    return tx
