import hashlib
import json #Encodes complex datastructures into string

def hash_string265(string):
    return hashlib.sha256(string).hexdigest()

def hash_block(block):
    #sha256:Creates 64 charecter hash
    #dumps: converts the block into json format string 
    #encode: encodes it to UTF 8 format(an sha256 redable string i.e binary)
    #hexdigest(): converts byte hash into normal hash
    # .cpoy(): will create a new copy every time the code runs rater than to overwrite
    hashable_block= block.__dict__.copy()
    hashable_block['transaction']= [tx.to_order_dict() for tx in hashable_block['transaction']]
    return hash_string265(json.dumps(hashable_block, sort_keys=True).encode())