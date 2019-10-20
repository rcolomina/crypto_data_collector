import requests,os,time,sys

import logging
from logging.handlers import TimedRotatingFileHandler

# GET LOGGER FROM LOGGING
logger = logging.getLogger("Rotating Log")

# SETUP LOG HANDLER ON STDOUT
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)
simple_formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
console_handler.setFormatter(simple_formatter)
logger.addHandler(console_handler)

# SETUP LOG HANDLER ON OUTPUT FILE
logger.setLevel(logging.DEBUG)
path="/home/pi/trading_crypto_api/logs/books_bitmex.log"
handler = TimedRotatingFileHandler(path,when="m",interval=1)
logger.addHandler(handler)

base_uri_bitmex="https://testnet.bitmex.com/api/v1" # TODO

# Request data
def get_api_bitmex_book(depth="25"):
    '''
    Calling API to perform a request againts API getting the lattest exchange order book
    '''
    symbol = "XBTUSD"
    orderBookQuery = "/orderBook/L2?symbol={}&depth={}".format(symbol,depth)    
    order_book_uri_bitmex = "{}{}".format(base_uri_bitmex,orderBookQuery)

    try:
        r = requests.get(order_book_uri_bitmex)
        if r.status_code == 200:
            return r.json()
    except:
        logger.error("ERROR: Something was wrong requesting on "+order_book_uri_bitmex)
        return {"ERROR: No books could be returned"}
    

def process_bitmex_book(bitmex_book):
    '''
    For each item found logger them out
    '''
    for item in bitmex_book:
        logger.info(item)
    
# Close Data Frame
def sleeper(num):
    while True:
        print("Sleeping for %d seconds" % num)
        time.sleep(num)
        bitmex_book = get_api_bitmex_book(depth="25")
        #print("bitmex_book",bitmex_book)
        if bitmex_book != None:
            process_bitmex_book(bitmex_book)
        else:
            print("Error getting bitmex book")
            
try:
    sleeper(1)
    # Gather info each second
    
except KeyboardInterrupt:
    print('\n\nKeyboard exception received. Exiting.')
    # Save Everything into the data base
    exit()


