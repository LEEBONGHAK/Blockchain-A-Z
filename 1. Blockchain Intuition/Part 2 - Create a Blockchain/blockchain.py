# Module 1 - Create a Blockchain

# To be installed:
# Flask: pip install Flask
# Postman HTTP Client: https://www.postman.com/

# Importing the libraries
import datetime  # 블록이 생성되고 채굴된 타임스탬프를 위해 사용
import hashlib  # 블록을 해시하기 위해 사용
import json
from urllib import response  # 블록을 해시하기 전에 블록 인코딩을 위해 사용

# Flask: 웹 애플리케이션이 되는 Flask 객체를 생성을 위해, jsonify: Postman에서 블록체인과 상호 작용할 때 메세지를 보내기 위해
from flask import Flask, jsonify


# Part 1 - Building a Blockchain


class Blockchain:

    def __init__(self):
        self.chain = []  # 블록이 포함될 체인 초기화
        self.create_block(proof=1, previous_hash='0')  # genesis block 생성

    def create_block(self, proof, previous_hash):  # 블록생성 메서드
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.chain.append(block)
        return block

    def get_previous_block(self):   # 가장 마지막 블록을 가져오는 메서드
        return self.chain[-1]

    def proof_of_work(self, previous_proof):    # 이전 증명값을 이용해 PoW를 수행하는 메서드
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):  # 블럭을 해시화하는 메서드
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):  # 블록체인의 유효성 확인 메서드(이전 해시 동일한지 확인, PoW 만족하는지 확인)
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if self.hash(previous_block) != block['previous_hash']:
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

# Part 2 - Mining our Blockchain
# Creating a Web App
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200
