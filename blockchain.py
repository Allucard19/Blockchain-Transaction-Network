import json #here used to covert data struct into strings
from functools import reduce
import hashlib
import requests #used to send http request from python
import pickle #used to convert data into binary

from utility.hash_util import hash_block
from block import Block
from transaction import Transaction
from utility.verification import Verification
from wallete import Wallet


Mining_reward=100

class Blockchain:

    

    def __init__(self, public_key, node_id):

        #incase if the text file is not present or we are not able to access the data we'll create a new file        
        genesis_block= Block(0,'', [], 100, 0)
        #empty blockchain list
        self.chain=[genesis_block]
        #unprocessed transactions
        self.__open_transactions=[]
        self.public_key = public_key
        self.__peer_nodes= set() #using sets so that we'll get unique values i.e to avoid repetation
        self.node_id= node_id
        self.resolve_conflict = False
        self.load_data()

    @property    #acts as getter
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain=val
         

   # def get_chain(self):         #[:] : creates a copy
    #    return self.__chain[:]  #returns a copy of chain

    def get_open_transaction(self):
        return self.__open_transactions[:]

    
    
    def load_data(self):
          
    
        try:
        
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:

        #If we use pickling it it better in terms of security and uses less code
                
                #global blockchain
            # global open_transactions
            # file_content=pickle.loads(f.read())
            # blockchain= file_content['chain']
            # open_transactions= file_content['op_tx']

        #Json can be used to check the security mechanism as we can see and edit the text
            
                file_content= f.readlines()  
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain=[]

                
                for block in blockchain:
                
                    converted_tnx= [Transaction(tx['sender'], tx['reciver'], tx['signature'], tx['amount']) for tx in block['transaction']]
                    
                    updated_block= Block(block['index'], block['previous_hash'], converted_tnx, block['proof'], block['timestamp'])
                    
    #Used this code before using classes and objects               
                # updated_block={
                    #   'Previous hash': block['Previous hash'],
                    #   'Index': block['Index'],
                    #   'Transaction': [OrderedDict([('Sender', tx['Sender']),('Reciver', tx['Reciver']), ('amount', tx['amount'])]) for tx in block['Transaction']],
                    #   'Proof': block['Proof']  
                    #   }
                    
                    
                    
                    updated_blockchain.append(updated_block)

                self.chain=updated_blockchain        
                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions=[]
                
                for tx in open_transactions:
                    
                    updated_transaction= Transaction(tx['sender'],  tx['reciver'], tx['signature'], tx['amount'])
                    
                    updated_transactions.append(updated_transaction)
                
                self.__open_transactions= updated_transactions

                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes= set(peer_nodes)

        except (IOError, IndexError):
            print('Exception handeled!')



    def save_data(self):
        try:
        
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
            
        #using json here

                saveable_chain= [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transaction], block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx= [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx)) 
                #for peer nodes
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))


        #If we use pickling it it better in terms of security and uses less code 
            
            # save_data ={

                # 'chain': blockchain,
                #   'op_tx': open_transactions



                #}     
            #   f.write(pickle.dumps(save_data))
        except(IOError):
                    
                    print('Saving failed!')



    def proof_of_work(self):
        last_block=self.__chain[-1]
        last_hash= hash_block(last_block)
        proof=0
        
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof +=1
        return proof


    def get_balance(self, sender=None): 
        if sender == None:
            if self.public_key== None:
                return None
            participents= self.public_key

        else:
            participents=self.public_key


        tx_sender =[[tx.amount for tx in block.transaction 
            if tx.sender == participents] for block in self.__chain]
        
        open_tx_sender=[tx.amount
            for tx in self.__open_transactions if tx.sender == participents]
        
        tx_sender.append(open_tx_sender)
        
        amount_sent= reduce(lambda tx_sum, tx_amt : tx_sum+ sum(tx_amt) if len(tx_amt)>0 else tx_sum + 0, tx_sender ,0 )
        

        tx_reciver  =[[tx.amount
            for tx in block.transaction if tx.reciver== participents] for block in self.__chain]
        amount_recived=  reduce(lambda tx_sum, tx_amt : tx_sum+ sum(tx_amt) if len(tx_amt)>0 else tx_sum + 0, tx_reciver ,0 )

        return amount_recived-amount_sent


    def get_last_block(self):

        if len(self.__chain)<1:
            return None
        return self.__chain[-1]
     

    def add_tansaction(self, reciver, sender, signature, amount=1.0, is_reciving=False):
        
        #transaction={
        #   'Sender' : sender ,
        #  'Reciver' : reciver, 
        # 'amount':amount }
        #if self.public_key== None:
           # return False
        
        transaction= Transaction(sender, reciver, signature, amount)
        

        if Verification.verify_transactons(self.__open_transactions, self.get_balance):
            self.__open_transactions.append(transaction)
       
            self.save_data()
            if not is_reciving:
                for node in self.__peer_nodes:
                    url= 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response= requests.post(url, json={'sender': sender, 'reciver': reciver, 'amount':amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code==500:
                            print('Tranaction Declined! needs resolving ')
                            return False
                    except requests.exceptions.ConnectionError: #contains all connection error exceptions
                        continue  #we continue coz the error might be for one ofline node

            return True
        return False


    def mine_block(self):
        if self.public_key== None:
            return None

        last_block = self.__chain[-1]
        hashed_block=hash_block(last_block)
        
        proof= self.proof_of_work()

    #reward_transaction={
        #    'Sender': 'System',     #we change them into ordereddics 
        #   'Reciver': owner,       #as dictionaried are not arranged or sorted
        #  'amount' : Mining_reward, #so while hashing it could change the hash value
        #}
        
        reward_transaction= Transaction('Mining', self.public_key, '', Mining_reward)
        

        copied_transactions= self.__open_transactions[:]
        
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None

        copied_transactions.append(reward_transaction)
        
        
        block= Block(len(self.__chain), hashed_block, copied_transactions, proof)
        

        self.__chain.append(block)
        self.__open_transactions=[]
        self.save_data()

        for node in self.__peer_nodes:
            url='http://{}/broadcast-block'.format(node)
            converted_block= block.__dict__.copy()
            converted_block['transaction']= [tx.__dict__ for tx in converted_block['transaction']]
            try:
                response= requests.post(url, json= { 'block': converted_block})
                if response.status_code == 400 or response.status_code==500:
                    print('Tranaction Declined! needs resolving ')

                if response.status_code == 409:
                    self.resolve_conflict= True

            except requests.exceptions.ConnectionError:
                continue

        
        return block



    def add_block(self, block):
        transactions= [Transaction(tx['sender'], tx['reciver'], tx['signature'], tx['amount']) for tx in block['transaction']]
        proof_is_valid= Verification.valid_proof(transactions[:-1], block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False

        converted_block= Block(block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(converted_block)
        stored_transactions= self.__open_transactions[:]

        for itx in block['transaction']: #itx: incoming transaction
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.reciver == itx['reciver'] and opentx.amount == itx['amount'] and opentx.signature == itx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed!')


        self.save_data()
        return True


    def resolve(self):
        
        """Checks all peer nodes' blockchains and replaces the local one with longer valid ones."""
        # Initialize the winner chain with the local chain
        winner_chain = self.chain
        replace = False
        
        for node in self.__peer_nodes:
            url = 'http://{}/chain'.format(node)
            try:
                # Send a request and store the response
                response = requests.get(url)
                # Retrieve the JSON data as a dictionary
                node_chain = response.json()
                # Convert the dictionary list to a list of block AND transaction objects
                node_chain = [Block(block['index'], block['previous_hash'], [Transaction(
                    tx['sender'], tx['reciver'], tx['signature'], tx['amount']) for tx in block['transaction']],
                                    block['proof'], block['timestamp']) for block in node_chain]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                # Store the received chain as the current winner chain if it's longer AND valid
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        # Replace the local chain with the winner chain
        self.chain = winner_chain
        if replace:
            self.__open_transactions = []
        self.save_data()
        return replace
        
    
    def add_peer_node(self, node):

        self.__peer_nodes.add(node)
        self.save_data()


    def remove_peer_node(self, node):

        self.__peer_nodes.discard(node) 
        self.save_data() 


    def get_peer_nodes(self):
        return list(self.__peer_nodes)         















 














                            






