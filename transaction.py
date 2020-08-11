from collections import OrderedDict
from utility.printable import Printable

class Transaction(Printable):

    def __init__(self, sender, reciver, signature, amount):

        self.sender=sender
        self.reciver=reciver
        self.amount=amount
        self.signature = signature

    
    
    def to_order_dict(self):
        return OrderedDict([('Sender', self.sender), ('Reciver', self.reciver), ('amount', self.amount)])

    