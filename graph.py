import requests
import json
import plotly
import datetime
import plotly.express as px
import pandas as pd
import sys

#GDJELROP5MRTF5QXPW3AKGJSHQQXKEB5AKHTBBYVGOOSZLHPLH4QRBDU
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
c=0
for txnrecord in res_json["_embedded"]["records"]:
    if c!=0:
        memos.append(txnrecord["memo"])
    c=c+1

def tx_req():
    global res_json, memos, res
    #try:
    res=requests.get(res_json["_links"]["next"]["href"])
    #except Exception as e:
    #    print(e)
    #    return False

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



    inde=0
    for txn in res_json["_embedded"]["records"]:
        if inde!=0:
            memos.append(txn["memo"])
        inde=inde+1
    return True

while tx_req() is True:
    print("next called")


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

df=pd.DataFrame({'datetimes':datetimes, 'temps':temps})

fig = px.line(df, x="datetimes", y="temps")
fig.show()
