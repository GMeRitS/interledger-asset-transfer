# Developing Interledger

## Go through the repository

The current directory contains the project of the Interledger component for SOFIE.

- The `src` directory contains the component source code. 
    - The `sofie_asset_transfer` directory contains the python code implementing the asset transfer protocol for SOFIE's use cases. The protocol is based on a state machine and is described by the README in that folder.
        - Currenlty only Ethereum is supported. To integrate another ledger is required to implement the Initiator and Responder interfaces in `interfaces.py`. For example, the `Initiator.get_transfers()` functions should implement an event listener to catch events fired by the ledger, meanwhile the other functions should call the smart contract functions as required by the protocol: transferOut(), commit(), abort() and accept().
    - The `StateInitiator` and `StateResponder` are subclasses storing the new states of transfers in a DB for future recovery. A description can be found [here](src/sofie_asset_transfer/README_STATE_IL.md).

    - The `db_manager` directory contains a simple wrapper of a sql_alchemy object providing the CRUD methods to the asset transfer protocol modules. A description can be found [here](src/sofie_asset_transfer/README_STATE_IL.md).

- The `tests` directory contains the tests for the Python modules, divided into:
    - `unit`, test the methods of the modules not depending on external objects;
    - `integration`, test the methods that interact with other objects. Such object are mocked;
    - `system`, test the modules with a running instance of Ethereum (Ganache).

- The `truffle` directory contains a truffle project to implement the smart contracts. The contracts available are `AssetTransferInterface` providing an interface of the protocol for Ethereum, and `GameToken`, an example of ERC721 contract implementing the aforementioned interface.

- The `doc` folder contains restructured text documentation for a sphinx project. _Last update: beginning of September 2019, demo in Terni._

- The `images` are made with the Google draw.io tool and can be found in the `imgs` directory. Moreover, the same images and **the draw.io xml** source file can be found in the SOFIE Google Drive under */WP2 - Architecture/Framework Components/Interledger/Images/Asset transfer*.

## Start working with it

Read the READMES: the [repository description](./README.md), the [asset transfer protocol](src/sofie_asset_transfer/README.md) the [state DB recovery](src/sofie_asset_transfer/README_STATE_IL.md) extension.

Here a guideline for the first setup:

- First of all you might want to install everything.
    - Start with the `truffle` directory. Go and install the `npm` dependencies with `npm install`. **It requires nodejs and npm**
    - Type `truffle test` to see if truffle has been installed correctly. The tests should pass even without running ganache-cli and `truffle-migrate`.
    - If truffle is correctly installed and tests works, create a `virtualenv` in the main project folder and `activate` it.
    - Install the requirements with `python setup.py develop` and `python setup.py test`.
    - Test the if everything has been correctly installed by running the tests as listed in the [tests readme](tests/README.md).
- If everything goes well, you can run the component. The script `start_interledger` needs as command line argument a configuration file in .ini format: it reads such file and sets up a one or two-sided Interledger: one sided Interledger means that the protocol works only one way: you can imagine the trasfer going "from the ledger referenced by the Initiator to the ledger referenced by the Responder"; two sided Interledger creates underneats two instances of `sofie_asset_transfer.interledger.Interledger`, each one with its pair of Initiator and Responder. 
- You can play with the IL protocol with the CLI application. You need to open 4 tabs:
    - Tab 1: run `ganache-cli -p 8545`;
    - Tab 2: run `ganache-cli -p 7545`;
    - Tab 3: run `make migrate-8545` and `make migrate-7545` to deploy the contracts one in each network, and finally run `python start_interledger.py local-config.cfg`: now IL should actively run in loop (it won't print anything apart from a single line to notify that it is running);
    - > The commands `make migrate-*` automatically updates the `local-config.cfg` with the user and contract addresses after the migration. Is important to run interledger and CLI app after the migration, otherwise the scripts may not find the right contract or no contract at all.
    - Tab 4: run CLI application with `python demo/cli/cli.py local-config.cfg` and do as suggested in the [CLI readme](demo/cli/Readme.md). Try to transfer_out an asset and check its state if changes.


## What's next

- The `sofie_asset_transfer.interledger.Interledger` class:
    - [X] The class uses internally two lists, `transfers` and `transfers_sent`, which iterates over continuosly, without never cleaning them when a transfer is finalized (it has its state set to FINALIZED). **Update: now the component has a cleanup method which is called at every iteration of the run() method.**
        - [ ] Is it needed a more sophisticated data structure instead of lists? For example a dictionary with key the State of a transfer object and as value the list of all transfers with that state: but in this case we would need to update these lists very frequently.
    - [ ] There is no closing procedure in case Interledger needs to be stopped (e.g. finish to process the remaining transfers or ignore them).
    - [ ] Interledger error handling:
        - [ ] Transaction timout error:
            - [X] Initiator and Responder return an error stating there was a transaction timeout error.
        - [ ] Transaction failure (unresolved requirement, EVM errors):
            - [X] Initiator and Responder return an error stating there was a transaction failure.
    - [ ] No rollback method in case one of the above errors occurr. For example, if the `commit()` function is somehow impossible due to external factors, the asset will end up in a state which is not possible to roll back, but only commit (sooner or later). This **may or may not** need to define new methods in the interface and the protocol to handle this rollback. Needs more investigation.
    
***
- The `sofie_asset_transfer.interfaces` module:
    - [ ] An implementation of Initiator and Responder able to interact with other ledgers. In SOFIE, Hyperledger Fabric (HF) is a ledger that is going to be used.
    - [x] Find a different return value from True / False, if needed.

***
- The `sofie_asset_transfer.db_manager` module:
    - [ ] Design a better DB composition if needed: at the moment there are two un-related tables.
    - [ ] Improve the `DBManager` class or provide another one, if needed.

***
- Smart contracts:
    - [ ] Alongside the implemetation of Initiator and Responder for a different ledger, the related smart contract providing the protocol methods needs to be implemented as well (e.g. Chaincode for HF).

***
- User interaction / demo:
    - [ ] Extend CLI application;
    - [ ] Provide GUI application;


#### Do not forget to update the test suite by providing tests (unit, integration and system) for any new feature.
