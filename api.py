import flask
from flask import request, jsonify
from flask_cors import CORS
from uuid import uuid4
import os
from flask_pymongo import pymongo
from flask import make_response, jsonify


#
# MONGODB_URI = os.environ.get('MONGODB_URI', None)
# print(MONGODB_URI)

app = flask.Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config["DEBUG"] = True

client = pymongo.MongoClient("mongodb+srv://jklundeen:clwa7YMEk7GIiVu7@cluster0.w7zd7.mongodb.net/bob?retryWrites=true&w=majority", connect=False)
db = client.bob
print(db.name)

# stocks = [
#     {"id": 0,
#      "ticker": 'AAPL',
#      "avgPrice": '30.28',
#      "numberShares": '33'},
#     {"id": 1,
#      "ticker": 'BOB',
#      "avgPrice": '0.23',
#      "numberShares": '3000'},
#     {"id": 2,
#       "ticker": 'HELLO',
#       "avgPrice": '1700.19',
#       "numberShares": '1'},
# ]

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
        stockList.append(stock)
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

    for i in range(len(stocks)):
        item = stocks[i]

        if str(item['id']) == str(stockId):
            stock = {
            'id': item['id'],
             'ticker': item['ticker'],
             'avgPrice': avgPrice,
             'numberShares': numberShares
            }
            stocks[i] = stock

    return generate_response('hi')

@app.route('/stocks/<string:stockId>', methods=['DELETE'])
def deleteStock(stockId):
    index = -1
    for i in range(len(stocks)):
        item = stocks[i]

        if str(item['id']) == str(stockId):
            index = i

    if index > -1:
        print(index)
        stocks.pop(index)

    return generate_response('hi')

if __name__ == '__main__':
    app.run(debug=True)
