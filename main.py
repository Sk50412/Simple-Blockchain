from flask import Flask, jsonify, render_template
import datetime
import hashlib
import json
app = Flask(__name__, static_url_path='/static')

class MyBlockchain:

    def __init__(self):
        self.blocks = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.blocks) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.blocks.append(block)
        return block

    def get_previous_block(self):
        return self.blocks[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while not check_proof:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def calculate_hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.calculate_hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()

            if hash_operation[:5] != '00000':
                return False

            previous_block = block
            block_index += 1

        return True

app = Flask(__name__)
my_blockchain = MyBlockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = my_blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = my_blockchain.proof_of_work(previous_proof)
    previous_hash = my_blockchain.calculate_hash(previous_block)
    block = my_blockchain.create_block(proof, previous_hash)

    response = {
        'message': 'New block mined successfully',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': my_blockchain.blocks,
        'length': len(my_blockchain.blocks)
    }
    return jsonify(response), 200

@app.route('/validate_chain', methods=['GET'])
def validate_chain():
    is_valid = my_blockchain.is_chain_valid(my_blockchain.blocks)

    if is_valid:
        response = {'message': 'The blockchain is valid.'}
    else:
        response = {'message': 'The blockchain is not valid.'}

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)