# -*- coding: utf-8 -*-
# 区块链的常用方法
# author 贾红平
# date 2018-03-03
# function 创建一个简单的区块链实例
from flask import Flask
import hashlib
import json
from time import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import requests
from uuid import uuid4
from flask import Flask, jsonify, request
class BlockChian:

    # 初始化
    def __init__(self):
        self.current_transactions = [] # 初始化交易记录
        self.chain = [] # 初始化区块链
        self.nodes = set() # 用来做节点去重复的
        self.create_new_block (previous_hash ='001',proof = 100) # 初始化一个创世块


    #previous_hash 前一个块的hash proof 工作量证明
    #创建一个创世块
    #使用typing进行方法返回类型的检查
    def create_new_block (self,proof: int, previous_hash: Optional[str]) -> Dict[str, Any]:

        #实例化一个区块
        block = {
            'index':len(self.chain)+1,
            'timestamp':time(),
            'transactions':self.current_transactions,
            'proof':proof,
            'previous_hash':previous_hash or self.hash(self.chain[-1]), #从最后一个区块开始计算
        }
        self.current_transactions = [] #重新设置交易记录列表
        self.chain.append(block)
        return block

    #创建一个交易记录 sender:发送者 recipent:接收者 amount：交易金额
    def create_new_transaction(self,sender:str,recipient:str,amount:int)->int:
        #实例化一个交易记录
        new_transaction={
            'sender':hashlib.md5(sender.encode()).hexdigest(),
            'recipient':recipient,
            'amount':amount
        }
        self.current_transactions.append(new_transaction)
        return self.get_last_block['index']+1

    #计算hash算法
    @staticmethod
    def hash(block:Dict[str,Any])->str:
        block_str = json.dumps(block,sort_keys=True).encode()
        hash_value = hashlib.sha256(block_str).hexdigest()
        return hash_value

    #获取区块链中最后的一个块
    @property
    def get_last_block(self)->Dict[str,Any]:
        return self.chain[-1]

    #计算工作量证明 也就是求解hash的过程
    def proof_work(self,last_proof:int)->int:
        proof = 0
        while self.validate_proof(last_proof,proof)is False:
            proof+=1
        return proof

    #验证工作量证明 当前是验证计算的hash的值是否是以4个0开头 是就满足 不是淘汰
    #使用这个注解 代表该方法不需要传收self来和类进行绑定
    @staticmethod
    def validate_proof(last_proof:int,proof:int)->int:
        guess =f'{last_proof}{proof}'.encode() #直接获取参数值并且格式化
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] =='0000'


    #注册一个节点
    def register_node(self,address)->None:
        parse_url =urlparse(address)
        self.nodes.add(parse_url.netloc)


    #验证当前链的合法性 用来检查是否是有效链，遍历每个块验证hash和proof.
    def validate_block_chain(self,chain:List[Dict[str,Any]])->bool:
        pervious_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{pervious_block}')
            print(f'{block}')
            print("\n-----------\n")

            #hash不一致不是有效链
            if block['previous_hash'] != self.hash(pervious_block):
                return False

            #工作量证明不通过也不是有效的链
            if not self.valid_proof(pervious_block['proof'], block['proof']):
                return False

            pervious_block = block
            current_index += 1
        return True


    #共识算法 解决冲突
    #遍历所有的邻居节点，并用上一个方法检查链的有效性， 如果发现有效更长链，就替换掉自己的链
    def resolve_conflicts(self) -> bool:
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get('http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.validate_block_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        return False


