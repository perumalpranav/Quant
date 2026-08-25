import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


ticker = "AAPL"

#Data Comes with Open, High, Low, Volume
data = yf.download(
    ticker,
    start="2020-01-01",
    end="2025-01-01",
    auto_adjust=True
)

#Drops days market is not open (weekends, holidays, etc)
data = data.dropna()

#Uses closing price
price = data["Close"]


#20 & 50 day moving average
data["SMA_20"] = price.rolling(20).mean()
data["SMA_50"] = price.rolling(50).mean()



# Position (the trading signal) - (NOTE: Nothing about number of stocks here)
# 1 = invested in stock
# 0 = out of stock

data["Position"] = np.where(
    data["SMA_20"] > data["SMA_50"],
    1,
    0
)


#Calculate percent change for every day using this strategy
data["Stock_Return"] = price.pct_change()



data["Strategy_Return"] = (
    data["Position"].shift(1) #Shift position by one day so signal today affects tomorrow
    * data["Stock_Return"] #Multiply by stock return to 'realize' the benefit based on if the stock is held
)




initial_capital = 10_000

#Strategy Return Calculations
data["Equity"] = (
    initial_capital
    * (1 + data["Strategy_Return"].fillna(0)).cumprod()
)


#Buy and Hold Return Calculations
data["Buy_Hold"] = (
    initial_capital
    * (1 + data["Stock_Return"].fillna(0)).cumprod()
)


#Calculate return numbers to print
final_strategy_value = data["Equity"].iloc[-1]
final_buy_hold_value = data["Buy_Hold"].iloc[-1]

strategy_return = (final_strategy_value / initial_capital - 1)
buy_hold_return = (final_buy_hold_value / initial_capital - 1)

print(f"Initial capital: ${initial_capital:,.2f}")
print(f"Strategy value:  ${final_strategy_value:,.2f}")
print(f"Buy & hold:      ${final_buy_hold_value:,.2f}")

print(f"Strategy return:  {strategy_return:.2%}")
print(f"Buy & hold:       {buy_hold_return:.2%}")


#Plotting the Results
plt.figure(figsize=(12, 6))

plt.plot(
    data.index,
    data["Equity"],
    label="Moving Average Strategy"
)

plt.plot(
    data.index,
    data["Buy_Hold"],
    label="Buy & Hold"
)

plt.title(f"{ticker} Backtest")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")

plt.legend()
plt.grid()

plt.show()