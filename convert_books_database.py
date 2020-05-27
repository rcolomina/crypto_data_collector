import pandas as pd
import ast,os
import datetime

#from sqlalchemy import create_engine
import sqlite3

db_name = "pythonsqlite.db"
conn = sqlite3.connect(db_name)
#database="//pythonsqlite.db"
#engine = create_engine("sqlite://"+database)
#print(engine)

path="./logs"

for name in os.listdir(path=path):
    print(name)
    fname = "{}/{}".format(path,name)
    myregs = [ast.literal_eval(s.replace("\n","")) for s in open(fname)]
    print("Moving registers into pandas data frame")
    df = pd.DataFrame(myregs)
    print("Inserting pandas into sql")
    #print(df.head())
    # {'symbol': 'XBTUSD', 'id': 15599283800, 'side': 'Buy', 'size': 580, 'price': 7162}
    sdatetime = name.split(".")[2]
    print("parsing file with datetime ",sdatetime)
    mydatetime = datetime.datetime.strptime(sdatetime,"%Y-%m-%d_%H-%M")

    #print(mydatetime)
    df1 = df[["id","side","size","price"]]
    df1["datetime"] = [mydatetime for _ in range(0,len(df))]
    df1.columns = ["bitmex_id","side","size","price","datetime"]
    #print(df1.head())

    # Insar pandas into data base
    print("inserting pandas into db")
    df1.to_sql("bookprices", con=conn, if_exists='replace', index_label="id")
    
conn.close()
