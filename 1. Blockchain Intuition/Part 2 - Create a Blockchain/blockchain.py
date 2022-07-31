# Module 1 - Create a Blockchain

# To be installed:
# Flask: pip install Flask
# Postman HTTP Client: https://www.postman.com/

# Importing the libraries
import datetime  # 블록이 생성되고 채굴된 타임스탬프를 위해 사용
import hashlib  # 블록을 해시하기 위해 사용
import json  # 블록을 해시하기 전에 블록 인코딩을 위해 사용
# Flask: 웹 애플리케이션이 되는 Flask 객체를 생성을 위해, jsonify: Postman에서 블록체인과 상호 작용할 때 메세지를 보내기 위해
from flask import Flask, jsonify

# Part 1 - Building a Blockchain


class Blockchain:

    def __init__(self):
        self.chain = []  # 블록이 포함될 체인 초기화
        self.create_block(proof=1, previous_hash='0')  # genesis block 생성

# Part 2 - Mining our Blockchain
