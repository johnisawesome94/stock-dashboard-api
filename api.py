import flask
from flask import request, jsonify
from flask_cors import CORS
from uuid import uuid4
import os
from flask_pymongo import pymongo
from flask import make_response, jsonify
from bson.json_util import dumps
from bson.json_util import loads




MONGODB_URI = os.environ.get('MONGODB_URI', None)

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

client = pymongo.MongoClient("mongodb+srv://bob:iHigFJkUoaUfiCtR@cluster0.w7zd7.mongodb.net/stock-dashboard-api?retryWrites=true&w=majority", connect=False)
db = client.bob

####################
## Util Functions ##
####################
def generate_response(resp):
    return '{"message": "' + resp + '"}'

##################
## STOCKS API'S ##
##################
@app.route('/stocks', methods=['GET'])
def getStocks():
    stocks = db.stocks.find()
    stockList = []
    for stock in stocks:
        newStock = { 'id': stock['id'], 'ticker': stock['ticker'], 'numberShares': stock['numberShares'], 'avgPrice': stock['avgPrice'] }
        stockList.append(newStock)

    return jsonify(stockList)

@app.route('/stocks', methods=['POST'])
def postStock():
    try:
        # TODO: what if stock with ticker already exists? Merge? Keep separate?
        data = request.json
        id = str(uuid4())
        ticker = data['ticker']
        avgPrice = float(data['avgPrice'])
        numberShares = int(data['numberShares'])

        db.stocks.insert_one({ 'id': id, 'ticker': ticker, 'numberShares': numberShares, 'avgPrice': avgPrice })

        return generate_response('hi')
    except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'            }
            return make_response(jsonify(responseObject)), 500

@app.route('/stocks/<string:stockId>', methods=['PUT'])
def putStock(stockId):
    # TODO: can only modify avgPrice and numberShares
    data = request.json
    avgPrice = float(data['avgPrice'])
    numberShares = int(data['numberShares'])
    db.stocks.update({ "id": stockId }, { "$set": { 'avgPrice': avgPrice, 'numberShares': numberShares }})

    return generate_response('hi')

@app.route('/stocks/<string:stockId>', methods=['DELETE'])
def deleteStock(stockId):
    db.stocks.delete_one({ "id": stockId })
    resp = 'deleted member with id: ' + stockId
    return generate_response(resp)

if __name__ == '__main__':
    app.run(debug=True)
