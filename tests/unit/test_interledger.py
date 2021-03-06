from sofie_asset_transfer.interfaces import Initiator, Responder
from sofie_asset_transfer.interledger import Interledger, Transfer, State

def test_interledger_init():
    # Test initialization of interledger

    init = Initiator()
    resp = Responder()

    interledger = Interledger(init, resp)

    assert interledger.initiator == init
    assert interledger.responder == resp
    assert len(interledger.transfers) == 0
    assert len(interledger.transfers_sent) == 0
    assert interledger.pending == 0
    assert interledger.keep_running == True    


def test_interledger_stop():
    
    interledger = Interledger(None, None)

    interledger.stop()

    assert interledger.keep_running == False

def return_transfer_list():

    t1 = Transfer()
    t2 = Transfer()
    t3 = Transfer()
    t4 = Transfer()

    t2.state = State.SENT
    t3.state = State.RESPONDED
    t4.state = State.FINALIZED

    return [t1, t2, t3, t4]

def test_interledger_cleanuplist():

    interledger = Interledger(None, None)
    ts = return_transfer_list()
    ts = interledger.cleanlist(ts, State.FINALIZED)

    assert len(ts) is 3
    assert ts[0].state is State.READY
    assert ts[1].state is State.SENT
    assert ts[2].state is State.RESPONDED


def test_interledger_cleanup():

    interledger = Interledger(None, None)
    ts1 = return_transfer_list()

    interledger.transfers.extend(ts1)
    interledger.transfers_sent.extend(ts1)

    interledger.cleanup()

    assert len(interledger.transfers) is 3
    assert len(interledger.transfers_sent) is 3