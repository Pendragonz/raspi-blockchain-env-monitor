import requests
import json
import plotly
import datetime
import plotly.express as px
import pandas as pd
import sys

#example input addr GDJELROP5MRTF5QXPW3AKGJSHQQXKEB5AKHTBBYVGOOSZLHPLH4QRBDU
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
    print("next called")


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
df=pd.DataFrame({'datetimes':datetimes, 'temps':temps})
fig = px.line(df, x="datetimes", y="temps")
fig.show()
df = pd.DataFrame({'datetimes':datetimes, 'humids':humids})
fig = px.line(df, x="datetimes", y="humids")
fig.show()
