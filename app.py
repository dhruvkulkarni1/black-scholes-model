import numpy as np
from scipy.stats import norm
import yfinance as yf
import pandas as pd
from datetime import datetime, date
import pandas_datareader.data as web

# Price = Current Equity Price
# Strike = Strike Price of Option
# RFR = Risk Free Rate
# DTE = Option Days to Expiration
# Volatility = Annualized Volatility of the Asset's Returns 
# the interest rate on a three-month U.S. Treasury bill is often used as a stand-in for the short-term risk-free rate, since it has almost no risk of default

def call_BSM(Price, Strike, DTE, RFR, Volatility):
    d1 = (np.log(Price/Strike) + (RFR + Volatility**2/2)*DTE) / (Volatility*np.sqrt(DTE))
    d2 = d1 - Volatility * np.sqrt(DTE)
    return Price * norm.cdf(d1) - Strike * np.exp(-RFR*DTE)* norm.cdf(d2)

def put_BSM(Price, Strike, DTE, RFR, Volatility):
    d1 = (np.log(Price/Strike) + (RFR + Volatility**2/2)*DTE) / (Volatility*np.sqrt(DTE))
    d2 = d1 - Volatility * np.sqrt(DTE)
    return Strike*np.exp(-RFR*DTE)*norm.cdf(-d2) - Price*norm.cdf(-d1)

def find_volatility(stock):
  today = datetime.now()
  one_year_ago = today.replace(year=today.year-1)

  df = web.DataReader(stock, 'yahoo', one_year_ago, today)

  df = df.sort_values(by="Date")
  df = df.dropna()
  df = df.assign(close_day_before=df.Close.shift(1))
  df['returns'] = ((df.Close - df.close_day_before)/df.close_day_before)
  vol = np.sqrt(252) * df['returns'].std()
  return vol
  
def get_RFR():
  t = yf.Ticker("^IRX")
  b_info = t.get_info()
  rate = b_info.get("regularMarketPrice")
  risk_free_rate = rate * 0.01
  return risk_free_rate

def option_price(Stock, Strike, DTE, call_or_put):
  ticker = yf.Ticker(Stock)
  vol = find_volatility(Stock)
  info = ticker.info
  price = info.get("currentPrice")
  rate = get_RFR()

  if call_or_put == "call" or "Call" or "CALL":
    put_BSM(Price=price, Strike=Strike, DTE=DTE, RFR=rate, Volatility=vol)
  if call_or_put == "put" or "Put" or "PUT":
    call_BSM(Price=price, Strike=Strike, DTE=DTE, RFR=rate, Volatility=vol)