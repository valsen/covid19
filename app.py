from flask import Flask, send_from_directory, request
from pytrends.request import TrendReq
from datetime import date
from dateutil.relativedelta import relativedelta

app = Flask(__name__)


@app.route('/')
def base():
    return send_from_directory('client/public', 'index.html')


@app.route('/trends', methods=['GET', 'POST'])
def getTrends():
    req = request.get_json()
    searchTerms = req["searchTerms"]
    iso = req["iso"]
    pytrends = TrendReq(hl='en-US')
    pytrends.build_payload(geo=iso, kw_list=searchTerms, timeframe='today 3-m')
    return pytrends.interest_over_time().to_json()

@app.route('/cases', methods=['GET', 'POST'])
def getCases():
    today = date.today()
    start_date = today - relativedelta(months=3)

    searchTerms = request.get_json()
    pytrends = TrendReq(hl='en-US')
    pytrends.build_payload(kw_list=searchTerms, timeframe='today 3-m')
    return pytrends.interest_over_time().to_json()

@app.route('/<path:path>')
def home(path):
    return send_from_directory('client/public', path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
