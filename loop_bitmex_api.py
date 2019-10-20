import requests
import time
import json
import queue

import numpy as np
from sklearn import svm
from sklearn.linear_model import SGDClassifier
from joblib import dump,load

joblib_filename="bitmex_anomaly_detector.joblib"

def createModel(select):    
    return svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)

def createSGDC():    
    return SGDClassifier(loss="hinge", penalty="l2", max_iter=5)

# Open if exist or create new the model
import os
clf = None
if os.path.isfile(joblib_filename):
    print("Loaded JobLib Model")
    clf = load(joblib_filename)
else:
    print("Created Model")    
    clf = createSGDC()
    
# Unsupervise Learning
def partial_fit_unsuper(model,X_minibatch):
    model.partial_fit(X_minibatch)

# Supervise Learning
def partial_fit_super(model,X_minibatch,Y_minibatch):
    model.partial_fit(X_minibatch,Y_minibatch,classes=[0,1])

# Base URI bitmex
base_uri_bitmex="https://testnet.bitmex.com/api/v1"

# Order Book URI bitmex
order_book_uri_bitmex=base_uri_bitmex+"/orderBook/L2?symbol=XBTUSD&depth=25"

def get_api_bitmex_book():
    '''
    Calling API to get current book
    '''
    print("Calling bitmex api")
    r = requests.get(order_book_uri_bitmex)
    if r.status_code == 200:
        return r.json()
    else:
        return []

## Target to predict
from collections import deque

seconds_on_the_horizon=900

prices_queue = deque(maxlen=seconds_on_the_horizon)
books_queue  = deque(maxlen=seconds_on_the_horizon)

#current_price = None
#current_book  = None
    
def calculate_features(book):
    buy_side=[]
    sell_side=[]

    # Run query book
    for item in book:
        if item["side"] == "Buy":
            buy_side.append([item["price"],item["size"]])
        if item["side"] == "Sell":
            sell_side.append([item["price"],item["size"]])

    buy_side = np.array(buy_side)
    sell_side = np.array(sell_side)            

    # Concatenating sells and buys
    current_book = np.concatenate((sell_side,buy_side))

    # Average Price considering volume
    avg_price    = np.dot(current_book[:,0],current_book[:,1]) / np.sum(current_book,axis=0)[1]
    
    current_mean_price = avg_price #(cheaper_sell + expensive_buy) / 2.0 
    
    return current_book, current_mean_price
    
def sleeper(num):
    while True:        
        
        
        # Run our time.sleep() command,        
        print("Sleeping for %d seconds" % num)
        time.sleep(num)
        print('Before API is called: %s' % time.ctime())
        book = get_api_bitmex_book()
        print(book)
        
        print('After API is called: %s\n' % time.ctime())

        if len(book) > 0:
            current_book, current_mean_price = calculate_features(book)

            #print(current_book, current_mean_price)
            prices_queue.append(current_mean_price)
            books_queue.append(current_book)
            #print("prices queue size:",prices_queue.qsize())
            #print("books queue size:",books_queue.qsize())
            #print(current_book)
            #print(prices_queue)
            print("Old  Price  ("+str(seconds_on_the_horizon)+" seconds) =>",prices_queue[0])
            print("Last Price  (  0 seconds) =>",prices_queue[-1])
            print("Acumulated Prices in Queue = ",len(prices_queue))
            # Calcute a compex momentum rather than a simple substration
            
            diff_prices_array = np.diff(np.array(prices_queue))
            average_first_diffs = np.mean(diff_prices_array)
            print("Average First  Differences => ",average_first_diffs)
            diff_diff_prices_array = np.diff(diff_prices_array)
            average_second_diffs = np.mean(diff_diff_prices_array)
            print("Average Second Differences => ",average_second_diffs)
                        
            #print("Price Direction (180) ",prices_queue[-1]-prices_queue[180])
            #print("Price Direction ( 60) ",prices_queue[-1]-prices_queue[240])

            import math
            if not math.isnan(average_first_diffs):
                
                X_minibatch = np.array(np.squeeze(books_queue[0].flatten())).reshape(1,-1)

                #X_minibatch = X_minibatch.reshape(1,-1) 
                Y_minibatch = [0]
                if average_first_diffs > 0.0:
                    Y_minibatch = [1]

                print(list(X_minibatch))
                #print(type(X_minibatch),X_minibatch)
                print(Y_minibatch)

                print("Adding more data to fit")
                partial_fit_super(clf,X_minibatch,Y_minibatch)

                
            X = np.array(np.squeeze(books_queue[-1].flatten())).reshape(1,-1)                
            print("ONLINE PREDICTION ==>",clf.predict(X))


            #print("Coeficients",list(clf.coef_))
            #print("Intercept",list(clf.intercept_))
            ## Estimate Metrics ##
            
            
        else:
            print("missed book")
        #partial_fit_svm(X_minibatch)
        #print("Book Len: %s ",len(book))

        

 
 
try:
    sleeper(5)
except KeyboardInterrupt:
    print('\n\nKeyboard exception received. Exiting.')
    if clf != None:
        print("Saved JobLib")
        dump(clf,joblib_filename)
    exit()


    
