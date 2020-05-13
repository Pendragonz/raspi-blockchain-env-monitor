import requests
import json
import plotly
import datetime
import plotly.express as px
import pandas as pd
import sys

import plotly.graph_objects as go
from plotly.subplots import make_subplots

#example input addresses:
#GDJELROP5MRTF5QXPW3AKGJSHQQXKEB5AKHTBBYVGOOSZLHPLH4QRBDU
#GDCCCKROG23MTXXDMMBZ7E2UIIGZJ3UYHU6CICWFPPJQ7CJ2NPO7XL4J
url="https://horizon.stellar.org/accounts/" + sys.argv[1] +"/transactions?limit=200"

print("making tx data request")
res=requests.get(url)
print("got response")
res_json=json.loads(res.text)

memos=[]
dates_md=[]#m-d
times_hms=[]#h:m:s
temps=[]
humids=[]

for txnrecord in res_json["_embedded"]["records"]:
    if txnrecord["memo_type"]=="text":
        try:
            memos.append(txnrecord["memo"])
        except Exception as e:
            print(e)
            print(txnrecord)


def tx_req():
    global res_json, memos, res
    res=requests.get(res_json["_links"]["next"]["href"])

    if res.status_code == 400 or res.status_code==404:
        print(res)
        print(res.status_code)
        return False
    res_json=json.loads(res.text)

    if res_json["_links"]["next"]["href"] == res_json["_links"]["prev"]["href"]:
        return False

    if res_json["_embedded"]["records"] is None:
        return False

    try:
        _throwaway=res_json["_embedded"]["records"][0]
    except:
        return False

    for txn in res_json["_embedded"]["records"]:
        if txn["memo_type"]=="text":
            memos.append(txn["memo"])
    return True

#get txsn recursively until all have been obtained
while tx_req() is True:
    #print("next called")
    pass


#process memo fields to obtain temp and humidity data
datetimes=[]
for memo in memos:
    d_md=memo[:5]
    dates_md.append(d_md)

    d_hms=memo[6:14]
    times_hms.append(d_hms)

    temp=memo[memo.index("t:")+2:memo.index("h")]
    temps.append(temp)

    humid=memo[memo.index("h:")+2:]
    humids.append(humid)

    dt=datetime.datetime.strptime("2020:"+d_md+":"+d_hms,"%Y:%d-%m:%H:%M:%S")
    datetimes.append(dt)


#build graphs and display
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(
    x=datetimes,
    y=temps,
    name="temperature"),
    secondary_y=False
)

fig.add_trace(go.Scatter(
    x=datetimes,
    y=humids,
    name="humidity"),
    secondary_y=True
)

titleString="Account: " + sys.argv[1]

fig.update_layout(
    title=titleString
)

fig.show()
