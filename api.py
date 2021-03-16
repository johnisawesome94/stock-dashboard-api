import flask
from flask import request, jsonify
from flask_cors import CORS
from uuid import uuid4

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

stocks = [
    {"id": 0,
     "ticker": 'AAPL',
     "avgPrice": '30.28',
     "numberShares": '33'},
    {"id": 1,
     "ticker": 'BOB',
     "avgPrice": '0.23',
     "numberShares": '3000'},
    {"id": 2,
      "ticker": 'HELLO',
      "avgPrice": '1700.19',
      "numberShares": '1'},
]

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
    return jsonify(stocks)

@app.route('/stocks', methods=['POST'])
def postStock():
    # TODO: what if stock with ticker already exists? Merge? Keep separate?
    data = request.json
    id = str(uuid4())
    ticker = data['ticker']
    avgPrice = float(data['avgPrice'])
    numberShares = int(data['numberShares'])
    stocks.append({
        'id': id,
         'ticker': ticker,
         'avgPrice': avgPrice,
         'numberShares': numberShares})
    return generate_response('hi')

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
