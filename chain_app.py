from flask import Flask
from chain import BlockChian as ch
from uuid import uuid4
from flask import Flask, jsonify, request
app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

chain = ch()

#挖矿
@app.route('/mine',methods=['GET'])
def mine():
    block = chain.get_last_block  #获取到最后一个区块
    print('block',block)

    proof = block['proof'] #获取区块对应的proof
    print('block_proof',proof)

    proof = chain.proof_work(proof) #计算工作量证明
    print('proof_work',proof)

    chain.create_new_transaction(sender="jiahp",recipient=node_identifier,amount=1000,)
    print('create_new_transaction',block)

    block = chain.create_new_block(proof, None)  #创造一个新的块
    print('create_new_block',block)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response),200

#创建一个新的交易
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    # 检查POST数据
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    index = chain.create_new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response),201

#获取整个链的信息
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': chain.chain,
        'length': len(chain.chain),
    }
    return jsonify(response), 200

#注册一个新的节点
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        chain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(chain.nodes),
    }
    return jsonify(response), 201

#显示解决链之间的冲突
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = chain.resolve_conflicts()
    if replaced:
        response = {
            'message': '我们的区块链被替换了',
            'new_chain': chain.chain
        }
    else:
        response = {
            'message': '我们的区块链是有效的',
            'chain': chain.chain
        }
    return jsonify(response), 200


if __name__ == '__main__':
    #初始化参数
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    #启动应用
    app.run(host='127.0.0.1',port=port)
