import time
from datetime import datetime
from binance.client import Client
from BinanceKeys import BinanceKeySecretPair
api_key = BinanceKeySecretPair['api_key']
api_secret = BinanceKeySecretPair['api_secret']
client = Client(api_key, api_secret)


def get_symbol_to_index(tickers):
    map_symbol_to_index = {}
    for i in range(0, len(tickers)):
        map_symbol_to_index[tickers[i]['symbol']] = i
    return map_symbol_to_index


def get_potential_arbitrages(symbols, tickers):
    starting_currency = 'LTC'

    out_currencies = []

    triangles = []

    for ticker in tickers:
        if ticker['symbol'].startswith(starting_currency):
            out_currencies.append(ticker['symbol'][len(starting_currency):])

    for i in range(0, len(out_currencies)):
        for j in range(i+1, len(out_currencies)):
            forward_edge = out_currencies[i]+out_currencies[j]
            backward_edge = out_currencies[j]+out_currencies[i]

            if forward_edge in symbols:
                triangle = [starting_currency+out_currencies[j], starting_currency+out_currencies[i], forward_edge]
            else:
                triangle = [starting_currency+out_currencies[i], starting_currency+out_currencies[j], backward_edge]

            triangles.append(triangle)

    return triangles


def find_best_arbitrages(triangles, index_map, tickers):

    max_return_rate = -100

    while True:
        tickers = client.get_orderbook_tickers()
        for triangle in triangles:
            rate1 = float(tickers[index_map[triangle[0]]]['askPrice'])
            rate2 = float(tickers[index_map[triangle[1]]]['bidPrice'])*float(tickers[index_map[triangle[2]]]['bidPrice'])
            return_rate = (rate2-rate1)/rate1*100.0

            if return_rate > max_return_rate:
                max_return_rate = return_rate
                print("Maximum: " + str(max_return_rate) + "% arbitrage from " + triangle[1] + "->" + triangle[2])


conversions = client.get_orderbook_tickers()
conversion_to_index = get_symbol_to_index(conversions)
symbol_list = conversion_to_index.keys()
arb_triangles = get_potential_arbitrages(symbol_list, conversions)
find_best_arbitrages(arb_triangles, conversion_to_index, conversions)

