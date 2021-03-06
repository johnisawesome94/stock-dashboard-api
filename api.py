import flask
from flask import request, jsonify, make_response
from flask_cors import CORS
from uuid import uuid4
import os
from flask_pymongo import pymongo
from yahooquery import Ticker

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
    search = request.args.get('search')
    sortKey = request.args.get('sortKey')
    sortDir = request.args.get('sortDir')

    if (sortDir is None and sortKey is not None) or (sortDir is not None and sortKey is None):
        responseObject = { 'status': 'fail', 'message': 'Must have both sortDir and sortKey set, or neither set.' }
        return make_response(jsonify(responseObject)), 500


    if search is None and sortDir is None:
        stocks = db.stocks.find()
    elif search is None and sortDir is not None:
        stocks = db.stocks.find().sort([(str(sortKey), int(sortDir))])
    elif search is not None and sortDir is None:
        stocks = db.stocks.find({"ticker": {"$regex": "(?i).*" + search + ".*"}})
    else:
        stocks = db.stocks.find({"ticker": {"$regex": "(?i).*" + search + ".*"}}).sort([(str(sortKey), int(sortDir))])


    stockList = []
    for stock in stocks:
        print(stock)
        ticker = stock['ticker']
        newStock = Ticker(ticker).summary_detail[ticker]
        newStock['id'] = stock['id']
        newStock['ticker'] = ticker
        newStock['numberShares'] = stock['numberShares']
        newStock['avgPrice'] = stock['avgPrice']
        stockList.append(newStock)

    return jsonify(stockList)


@app.route('/stocks/chart', methods=['GET'])
def getStockChart():

    ticker = request.args.get('ticker')
    period = request.args.get('period')

    # set default period if none passed to API
    if period is None:
        period = '1d'

    switcher = {
        '1d': "5m",
        '7d': "30m",
        '1mo': "1h",
        '1y': "1d",
        'ytd': "1d", # TODO: this varies based on the date
        'max': "3mo" # TODO: this varies based on the stock
    }

    interval = switcher.get(period, "Invalid interval")

    if interval == 'Invalid interval':
        responseObject = { 'status': 'fail', 'message': 'Period of ' + str(period) + ' is not supported' }
        return make_response(jsonify(responseObject)), 500

     # if ticker isn't passed return avg stock data for all tickers user has added
    if ticker is None:
        stocks = db.stocks.find()
        tickerString = ''
        for stock in stocks:
            tickerString = tickerString + stock['ticker'] + ' '

        tickers = Ticker(tickerString.strip(), asynchronous=True)
        df = tickers.history(period=period, interval=interval)
        df = df.groupby('date').sum()
    else:
        tickers = Ticker(ticker, asynchronous=True)
        df = tickers.history(period=period, interval=interval)

    newList = df.to_records()
    someOtherList = []
    for bob in newList:
        someOtherList.append({
            'date': str(bob['date']),
            'low': float(bob['low']),
            'high': float(bob['high']),
            'volume': float(bob['volume']),
            'close': float(bob['close']),
            'open': float(bob['open'])
        })
    return jsonify(someOtherList)


@app.route('/stocks', methods=['POST'])
def postStock():
    # TODO: what if stock with ticker already exists? Merge? Keep separate?
    data = request.json
    ticker = data['ticker']

    if isinstance(Ticker(ticker).summary_detail[ticker], str):
        responseObject = { 'status': 'fail', 'message': 'Could not find a stock with the ticker: ' + ticker }
        return make_response(jsonify(responseObject)), 500
    else:
        id = str(uuid4())
        avgPrice = float(data['avgPrice'])
        numberShares = int(data['numberShares'])

        db.stocks.insert_one({ 'id': id, 'ticker': ticker, 'numberShares': numberShares, 'avgPrice': avgPrice })

        return generate_response('successfully added stock')

@app.route('/stocks/<string:stockId>', methods=['PUT'])
def putStock(stockId):
    # TODO: can only modify avgPrice and numberShares
    data = request.json
    avgPrice = float(data['avgPrice'])
    numberShares = int(data['numberShares'])
    db.stocks.update({ "id": stockId }, { "$set": { 'avgPrice': avgPrice, 'numberShares': numberShares }})

    return generate_response('updated stock with id: ' + stockId
)

@app.route('/stocks/<string:stockId>', methods=['DELETE'])
def deleteStock(stockId):
    db.stocks.delete_one({ "id": stockId })

    return generate_response('deleted stock with id: ' + stockId)


#####################
## DARK-MODE API'S ##
#####################
@app.route('/dark-mode', methods=['GET'])
def getDarkMode():
    darkMode = db.darkMode.find()
    if darkMode is None:
        return jsonify({ 'darkMode': True })
    for dM in darkMode:
        dark = dM['darkMode']
        return jsonify({ 'darkMode': dark })
    return jsonify('error happened')

@app.route('/dark-mode', methods=['PUT'])
def putDarkMode():
    data = request.json
    newDarkMode = data['darkMode']

    darkMode = db.darkMode.find()
    if darkMode is None:
        db.darkMode.insert_one({ 'darkMode': newDarkMode })
    else:
        for dark in darkMode:
            id = dark['_id']
            db.darkMode.update({ "_id": id }, { "$set": { 'darkMode': newDarkMode }})

    return generate_response('successfully updated darkmode')


if __name__ == '__main__':
    app.run(debug=True)
