from sofie_asset_transfer.interfaces import ErrorCode
from sofie_asset_transfer.interledger import Transfer
from sofie_asset_transfer.ethereum import EthereumResponder
import pytest, asyncio
import os, json
import web3
from web3 import Web3

# Helper functions
def readContractData(path):
    with open(path) as obj:
        jsn = json.load(obj)
        return jsn["abi"], jsn["bytecode"]


def create_contract(w3, abi, bytecode, _from):

    # Create contract
    TokenContract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = TokenContract.constructor("GameToken", "GAME").transact({'from': _from})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    address = tx_receipt.contractAddress
    token_instance = w3.eth.contract(abi=abi, address=address)
    return token_instance

# current working directory changes if you run pytest in ./, or ./tests/ or ./tests/system
cwd = os.getcwd()
contract_path = "truffle/build/contracts/GameToken.json"

if "system" in cwd.split('/'):
    contract_path = "../../" + contract_path
elif "tests" in cwd.split('/'):
    contract_path = "../" + contract_path
else:
    contract_path = "./" + contract_path

# # # Local view
# #
# #  EthereumResponder -> Ledger
#
# # 
#

def test_init():

    # Setup web3 and state
    url = "HTTP://127.0.0.1"
    port = 8545

    resp = EthereumResponder("minter", "contract", url, port=port)

    assert resp.web3.isConnected()
    assert resp.minter == "minter"
    assert resp.contract_resp == "contract"
    assert resp.timeout == 120

    
#
# Test receive_transfer
#


def setUp():

    # Setup the state
        # Deploy contract
        # Mint token
        # Call accept() from the minter
        
    # Setup web3 and state
    url = "HTTP://127.0.0.1"
    port = 8545
    w3 = Web3(Web3.HTTPProvider(url+":"+str(port)))

    abi, bytecode = readContractData(contract_path)

    contract_minter = w3.eth.accounts[0]
    bob = w3.eth.accounts[1]

    token_instance = create_contract(w3, abi, bytecode, contract_minter)

    # Create a token
    tokenId = 123
    tokenURI = "weapons/"
    assetId = w3.toBytes(text="Vorpal Sword")

    tx_hash = token_instance.functions.mint(bob, tokenId, tokenURI, assetId).transact({'from': contract_minter})
    w3.eth.waitForTransactionReceipt(tx_hash)

    t = Transfer()
    t.data = dict()
    t.data["assetId"] = tokenId

    return (contract_minter, token_instance, url, port, t)


@pytest.mark.asyncio
async def test_responder_receive():

    (contract_minter, token_instance, url, port, t) = setUp()

    ### Test Ethereum Responder ###

    resp = EthereumResponder(contract_minter, token_instance, url, port=port)

    result = await resp.receive_transfer(t)

    assert result["status"] == True

@pytest.mark.asyncio
async def test_responder_receive_txerror():

    (contract_minter, token_instance, url, port, t) = setUp()
    t.data["assetId"] +=1 # <- fail

    ### Test Ethereum Responder ###

    resp = EthereumResponder(contract_minter, token_instance, url, port=port)

    result = await resp.receive_transfer(t)

    assert result["status"] == False
    assert result["error_code"] == ErrorCode.TRANSACTION_FAILURE
