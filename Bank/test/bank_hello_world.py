import playground
import getpass, sys, os, asyncio
sys.path.insert( 1,'../src/')#change dict
from CipherUtil import loadCertFromFile
from BankCore import LedgerLineStorage, LedgerLine
from OnlineBank import BankClientProtocol, OnlineBankConfig


# insert at 1, 0 is the script path (or '' in REPL)#


bankconfig = OnlineBankConfig()
bank_addr =     bankconfig.get_parameter("CLIENT", "bank_addr")
bank_port = int(bankconfig.get_parameter("CLIENT", "bank_port"))
bank_stack     =     bankconfig.get_parameter("CLIENT", "stack","default")
bank_username  =   "zlin32"  #bankconfig.get_parameter("CLIENT", "username")

certPath = os.path.join(bankconfig.path(), "20194_online_bank.cert")
bank_cert = loadCertFromFile(certPath)


async def example_transfer(bank_client, src, dst, amount, memo):
    print("transfer begin")
    await playground.create_connection(
            lambda: bank_client,
            bank_addr,
            bank_port,
            family='default'
        )
    print("Connected. Logging in.")
        
    try:
        await bank_client.loginToServer()
    except Exception as e:
        print("Login error. {}".format(e))
        
        return False

    try:
        await bank_client.switchAccount(src)
    except Exception as e:
        print("Could not set source account as {} because {}".format(
            src,
            e))
        return False
    
    try:
        result = await bank_client.transfer(dst, amount, memo)
    except Exception as e:
        print("Could not transfer because {}".format(e))
        return False

    return result

    
def example_verify(bank_client, receipt_bytes, signature_bytes, dst, amount, memo):
    if not bank_client.verify(receipt_bytes, signature_bytes):
        raise Exception("Bad receipt. Not correctly signed by bank")
    ledger_line = LedgerLineStorage.deserialize(receipt_bytes)
    if ledger_line.getTransactionAmount(dst) != amount:
        raise Exception("Invalid amount. Expected {} got {}".format(amount, ledger_line.getTransactionAmount(dst)))
    elif ledger_line.memo(dst) != memo:
        raise Exception("Invalid memo. Expected {} got {}".format(memo, ledger_line.memo()))
    return True
'''
if __name__=="__main__":
    src, dst, amount, memo = sys.argv[1:5]
    amount = int(amount)
    username = bank_username # could override at the command line
    password = getpass.getpass("Enter password for {}: ".format(username))
    bank_client = BankClientProtocol(bank_cert, username, password) 
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(
        example_transfer(bank_client, src, dst, amount, memo))
    if result:
        example_verify(bank_client, result.Receipt, result.ReceiptSignature, dst, amount, memo)
        print("Receipt verified.")
'''
