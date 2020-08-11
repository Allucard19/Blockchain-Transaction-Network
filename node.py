from flask import Flask , request, send_from_directory  #request: used to extract data from the incoming request #used to create a server
from flask_json import jsonify
from wallete import Wallet
from flask_cors import CORS #it allow others clients to connect to our sever
from blockchain import Blockchain

app= Flask(__name__)
#wallet= Wallet()     ##comenting them as if we have too many nodes all the nodes will overwrite the same blockchain and wallet .txt file
#blockchain= Blockchain(wallet.public_key)     ##Commenting them for developmnt reson won't be a problem if we have different computers
CORS(app) #opens app to be used by other clients


#used when someone sends arequest to our the ip and port with 'GET' and '/'
@app.route('/', methods=['GET']) 
def get_node_ui():
    return send_from_directory('UI', 'node.html')


@app.route('/network', methods=['GET']) 
def get_network_UI():
    return send_from_directory('UI', 'network.html')




@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    
    if wallet.save_keys():
        global blockchain
        blockchain= Blockchain(wallet.public_key, port)
        
        response={
            'Public_key' : wallet.public_key,
            'Private_key' : wallet.private_key,
            'Wallet_Balance': blockchain.get_balance()
        }
       
        return (response), 201

    else:

        response={
            'message': 'Saving of keys failed!'
        }
        return jsonify(response), 500



@app.route('/wallet', methods=['GET'])
def load_keys():
    global blockchain
    blockchain= Blockchain(wallet.public_key, port)

    if wallet.load_keys():
        response={
            'Public_key' : wallet.public_key,
            'Private_key' : wallet.private_key,
            'Wallet_Balance': blockchain.get_balance()
        }
        
        return (response), 201

    else:

        response={
            'message': 'Loading of keys failed!'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance= blockchain.get_balance()
    if balance!=  None:
        response={
            'message': 'Fetched balance successfully!',
            'Wallet Balance': balance
        }
        return jsonify(response), 200
        
    else:
        response={
                'message': 'Loding balance failed!',
                'wallet status': wallet.public_key != None

        }
        return jsonify(response), 500


@app.route('/transaction',methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response={
            'message': 'Wallet not initialized!'
        }
        return jsonify(response),400

    
    values= request.get_json() #the incoming value should be an json format
    if not values:
        response={
            'message': 'No transaction data found'
        }
        return jsonify(response, 400)
    
    
    required_field= ['reciver', 'amount']
    if not all (field in values for field in required_field) : #for all fields in required fields if all the fields are part of values then true
        response={
            'message': 'Required data is missing'
        }   
        return jsonify(response, 400)

   
    reciver= values['reciver'] 
    amount= values['amount']
    signature = wallet.sign_transaction(wallet.public_key,reciver, amount)
    success= blockchain.add_tansaction(reciver, wallet.public_key, signature, amount)
    if success:
        response={
            'message': 'Transaction addded successfully!',
            'Transaction':{
                'Sender': wallet.public_key,
                'Reciver': reciver,
                'Amount':amount,
                'Signature': signature
            },
            
            'Remaining_balance': blockchain.get_balance()

        }
        return jsonify(response), 201

    else:
        response={
            'message': 'Transaction failed'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    if blockchain.resolve_conflict == True :
        response={'message': 'Resolve conflict first, block not added'}
        return jsonify(response), 409

    block = blockchain.mine_block()

    if block is not None:
        dict_block = block.__dict__.copy()
        dict_block['transaction']=  [tx.__dict__ for tx in dict_block['transaction']]
        
        response={
            'message': 'Block mined successfully!',
            'Block': dict_block,
            'Remaining_Balance': blockchain.get_balance()
            }
       
        return jsonify(response), 201 #201: creating resource i.e the server code googled it


    else:
        response= {
            'message': 'Mining of block failed!',
            'Wallet status': wallet.public_key!= None #true means wallet is aleady created
        }
        
        return jsonify(response), 500 



@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced = blockchain.resolve()
    if replaced:
        response = {'message': 'Chain was replaced!'}
    else:
        response = {'message': 'Local chain kept!'}
    return jsonify(response), 200



@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values= request.get_json()
    if not values:
        response={
            'message': 'No data found'
        }
        return jsonify(response), 400

    required=['sender','reciver', 'amount', 'signature'] 
    if not all(key in values for key in required)  :
        response={
            'message': 'Some of the data is missing'
        }
        return jsonify(response), 400
    success= blockchain.add_tansaction(values['reciver'], values['sender'], values['signature'], values['amount'], is_reciving= True)
   
    if success:
        response={
            'message': 'Transaction addded successfully!',
            'Transaction':{
                'Sender': values['sender'],
                'Reciver': values['reciver'],
                'Amount':values['amount'],
                'Signature': values['signature']
            }
            
        }
        return jsonify(response), 201  
        
        

    else:
        response={
            'message': 'Transaction failed'
        }
        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():

    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {'message': 'Block added'}
            return jsonify(response), 201
        else:
            response = {'message': 'Block seems invalid.'}
            return jsonify(response), 409
    elif block['index'] > blockchain.chain[-1].index:
        response = {'message': 'Blockchain seems to differ from local blockchain.'}
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else: 
        response = {'message': 'Blockchain seems to be shorter, block not added'}
        return jsonify(response), 409  #409:data sent is invalid



@app.route('/transaction', methods=['GET'])
def get_open_transactions():
    transaction= blockchain.get_open_transaction()
    dict_op_transaction = [tx.__dict__ for tx in transaction] 
    return jsonify(dict_op_transaction), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain= [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transaction']= [tx.__dict__ for tx in dict_block['transaction']]
        
    return jsonify(dict_chain), 200


@app.route('/node', methods=['POST'])
def add_node():
    values=request.get_json()

    if not values:
        response={    
            'message': 'NO data or response here! check line 181'
        }
        return jsonify(response), 400 

    if not 'node' in values:
        response={

            'message': 'no Node data found!'
        } 
        return jsonify(response), 400   

    node= values['node']
    blockchain.add_peer_node(node)
    response={
        'message': 'NOde added successully!',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201

@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):

    if node_url =='' or node_url== None:
        response={
            'message': 'no Node found to be removed! 211'
        }
        return jsonify(response),400

    blockchain.remove_peer_node(node_url)
    response={
        'message': 'Node removed!',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes= blockchain.get_peer_nodes()
    response={
        'all_nodes': nodes
    }
    return jsonify(response), 200

if __name__ =='__main__' :
    from argparse import ArgumentParser #allows the user to pass arguments along with node.py 
    parser= ArgumentParser()             #in termial which we can use to add multiple servers
    parser.add_argument('-p', '--port', type= int ,default=5000)     #add_argument will allow us to add the port no.: node.py -p 5010 or node.py --port 5010
    args= parser.parse_args() #parser.parse_args(): checks all te arguments passed in terminal and returns a list
    port= args.port
    wallet= Wallet(port)
    blockchain= Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port= port) #host: ip address, port: the listening port