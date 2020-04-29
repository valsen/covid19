from flask import Flask, request
from pytrends.request import TrendReq

app = Flask(__name__)

@app.route('/trends', methods=['GET', 'POST'])
def getTrends():
    req = request.get_json()
    searchTerms = req["searchTerms"]
    iso = req["iso"]
    pytrends = TrendReq(hl='en-US')
    pytrends.build_payload(geo=iso, kw_list=searchTerms, timeframe='today 3-m')
    return pytrends.interest_over_time().to_json()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
