# Module 2 - Create a Cryptocurrency

# To be installed:
# Flask: pip install Flask
# requests: pip install requests
# Postman HTTP Client: https://www.postman.com/

# Importing the libraries
import datetime  # 블록이 생성되고 채굴된 타임스탬프를 위해 사용
import hashlib  # 블록을 해시하기 위해 사용
import json  # 블록을 해시하기 전에 블록 인코딩을 위해 사용

from uuid import uuid4  # 네트워크의 각 노드에 대한 주소를 생성하기 위해 사용
from urllib.parse import urlparse  # 노드별 URL을 분석하기 위해 사용

# Flask: 웹 애플리케이션이 되는 Flask 객체를 생성을 위해
# jsonify: Postman에서 블록체인과 상호 작용할 때 메세지를 보내기 위해
# request: 탈중앙화된 블록체인 네트워크에 일부 노드를 연결시키고 이를 위해서 json 함수를 사용하기 위해
from flask import Flask, jsonify, request

# 탈중앙화된 블록체인 내의 모든 노드가 실제로 동일한 체인을 가지고 있는지 확인하며 이때 적용되는 합의에 사용하기 위해 사용
import requests


# Part 1 - Building a Blockchain
class Blockchain:
    def __init__(self):
        self.chain = []  # 블록이 포함될 체인 초기화
        self.transactions = []  # 블록에 추가하기 전의 트랜잭션을 포함하는 목록
        self.create_block(proof=1, previous_hash='0')  # genesis block 생성
        self.nodes = set()  # 블록체인 노드를 포함하는 집합(set)

    # 블록 생성 메서드
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        return block

    # 가장 마지막 블록을 가져오는 메서드
    def get_previous_block(self):
        return self.chain[-1]

    # 이전 증명값을 이용해 PoW를 수행하는 메서드
    def proof_of_work(self, previous_proof):
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

    # 블록을 해시화하는 메서드
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # 블록체인의 유효성 확인 메서드(이전 해시 동일한지 확인, PoW 만족하는지 확인)
    def is_chain_valid(self, chain):
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

    # 트랜잭션을 생성하고 트랜잭션 목록에 추가하는 메서드
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })

        previous_block = self.get_previous_block()
        # 트랜잭션을 수신하는 블록의 인덱스 반환
        return previous_block['index']

    # 노드 주소를 노드 집합에 추가하는 메서드
    def add_node(self, address):
        parse_url = urlparse(address)  # 노드 주소 파싱
        # 노드 집합에 추가 (parse_url.netloc => protocol, path, param, fragment를 제외한 url)
        self.nodes.add(parse_url.netloc)

    # 탈중앙화 네트워크에서 모든 노드를 살펴봐서 각 노드에서 가장 긴 체인을 찾고,
    # 가장 긴 체인보다 짧은 체인을 포함한 모든 노드에서 가장 긴 체인으로 체인을 교체하는 메서드
    # 해당 함수는 특정 노드에서만 호출한다.
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            # `/get_chain` 을 요청하여 해당 노드가 가지고 있는 블록체인의 길이를 가져옴
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
            if longest_chain:
                self.chain = longest_chain
                return True
            return False


# Part 2 - Mining Blockchain
# Creating a Web App
app = Flask(__name__)

# 코드 실행 중 500내부 서버 오류가 발생 할 경우를 대비
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()


# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transactions(sender=node_address,
                                receiver='Miner',
                                amount=1)
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions']
    }
    return jsonify(response), 200


# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'length': len(blockchain.chain), 'chain': blockchain.chain}
    return jsonify(response), 200


# Checking if the Blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {
            'message':
            'Houston, we have a problem. The Blockchain is not valid.'
        }
    return jsonify(response), 200


# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'],
                                       json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201


# Part 3 - Decentralizing Blockchain


# Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
        'message':
        'All the nodes are now connected. The BoleeChain now contains the following nodes',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201


# Replace blockchain
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {
            'message':
            'The nodes had different chains so the chain was replaced by the longest one.',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'All good. The chain is the largest one.',
            'actual_chain': blockchain.chain
        }
    return jsonify(response), 200


# Running the app
app.run(host='0.0.0.0', port=5000)
