from utility.hash_util import hash_string265, hash_block
from wallete import Wallet

class Verification:

    @staticmethod #@staticmethod won't access methods inside a class
    def valid_proof(transactions, last_hash, proof):
        guess=(str([tx.to_order_dict() for tx in transactions])+ str(last_hash)+ str(proof)).encode()
        
        guess_hash= hash_string265(guess)
        
        return guess_hash[0:2] == '00'
    
    
    @classmethod  #used decorator# @classmethod can access methods inside a class
    def verify_chain(cls,blockchain):

        for (index, block) in enumerate(blockchain):
            if index==0:
                continue 
            if block.previous_hash != hash_block(blockchain[index-1]):
                return False 
            if not cls.valid_proof(block.transaction [:-1], block.previous_hash, block.proof):
                print('The proof of work is not valid!')
                return False     
        return True


    @staticmethod
    def verify_transacton(transaction, get_balance, check_funds=True):
        if check_funds:
            sender_bal=get_balance(transaction.sender)
            return sender_bal >= transaction.amount and Wallet.verify_transaction(transaction)

        else:
            return Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactons(cls, open_transactions, get_balance):
        return all([cls.verify_transacton(tx, get_balance, False) for tx in open_transactions])    


    