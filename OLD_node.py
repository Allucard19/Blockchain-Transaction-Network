from blockchain import Blockchain
from uuid import uuid4 #gives unique id
from utility.verification import Verification
from wallete import Wallet


class Node:

    def __init__(self):
        #self.wallet= str(uuid4())
        self.wallet= Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)


    def get_transaction_value(self):
        """Takes the value input from the user.   """
        
        tx_reciver=input('Enter the name of the reciver: ')
        
        tx_amount=float(input('Enter your transaction amount:'))
        return tx_reciver,tx_amount    #used tuple here


    def get_user_Choice(self):
        user_input= input('Enter your Choice:')
        return user_input


    def display_blockchain(self):
        #Printing the Blocks
        for block in self.blockchain.chain:
            print('Outputting the block...\n:')
            print(block)       
        else:
            print('-'*25)


    def listen_for_input(self):

        waiting_for_input=True

        while waiting_for_input:
            
            print("select the option:")
            print("1: Add a transaction")
            print("2: Mine a new block")
            print("3: Displayy the block")
            print("4: Verify all the Transactions")
            print("5: Create wallet")
            print("6: load wallet") 
            print("7: Save keys")  
            print("q: Quit")
                
            user_choice = self.get_user_Choice()
            
            #To add transaction
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                reciver, amount = tx_data
                signature= self.wallet.sign_transaction(self.wallet.public_key, reciver, amount)
                if self.blockchain.add_tansaction(reciver, self.wallet.public_key, signature ,amount=amount):
                    print('Transaction Completeled!')
                else:
                    print('Transaction Failed!')
                
            #To Mine the block
            elif user_choice == '2':
               if not self.blockchain.mine_block():
                   print("Mining Failed!, maybe you don't have a wallet")
                
            #To display the block
            elif  user_choice == '3':
                self.display_blockchain() 
                
                    
            #To verify all the trasactions
            elif user_choice == '4':

                if Verification.verify_transactons(self.blockchain.get_open_transaction(),self.blockchain.get_balance):
                        print('The transaction is valid')
                else: 
                        print('The transaction is not valid ')
                    
            #Will create the wallet
            elif user_choice=='5':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
      

                    
            #LOads the wallet
            elif user_choice == '6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
                    
            elif user_choice =='7':
                self.wallet.save_keys()
                

            #To exit
            elif  user_choice == 'q':

                waiting_for_input = False            
                    
            else:
                print('Please enter a valid input!\n')
  
            if not Verification.verify_chain(self.blockchain.chain):
                
                print('The chain has been compromised!!') 
                self.display_blockchain() 
                break 


            print(' Balance of {} is: {:6.2f}'.format(self.wallet, self.blockchain.get_balance()))    

        else:
            print('user logged out!')




        print("done!")  
            


node= Node()
node.listen_for_input()