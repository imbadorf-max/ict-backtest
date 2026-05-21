import yfinance as yf
import pandas as pd
import numpy as np
from smartmoneyconcepts import smc
from backtesting import Backtest, Strategy
import mplfinance as mpf
import warnings
warnings.filterwarnings("ignore")

ticker = "EURUSD=X"
period = "5d"

df_ltf = yf.download(ticker, period=period, interval="5m")
df_ltf.columns = ["Open", "High", "Low", "Close", "Volume"]
df_ltf.dropna(inplace=True)

df_htf = yf.download(ticker, period=period, interval="1h")
df_htf.columns = ["Open", "High", "Low", "Close", "Volume"]
df_htf.dropna(inplace=True)

def get_htf_shadows(df_htf):
    shadows = pd.DataFrame(index=df_htf.index)
    shadows["Upper_Shadow_Top"] = df_htf["High"]
    shadows["Upper_Shadow_Bottom"] = np.maximum(df_htf["Open"], df_htf["Close"])
    shadows["Lower_Shadow_Top"] = np.minimum(df_htf["Open"], df_htf["Close"])
    shadows["Lower_Shadow_Bottom"] = df_htf["Low"]
    return shadows

def map_ltf_to_htf(df_ltf, df_htf):
    ltf_hour = df_ltf.index.floor("h")
    htf_shadows = get_htf_shadows(df_htf)
    mapped = htf_shadows.reindex(ltf_hour, method="ffill")
    mapped.index = df_ltf.index
    return mapped

class FractalICTStrategy(Strategy):
    atr_mult = 1.5

    def init(self):
        self.htf_mapped = map_ltf_to_htf(df_ltf, df_htf)

    def next(self):
        i = len(self.data) - 1
        if i < 10:
            return

        high, low, close = self.data.High[-1], self.data.Low[-1], self.data.Close[-1]
        htf_row = self.htf_mapped.iloc[i]
        upper_top, upper_bot = htf_row["Upper_Shadow_Top"], htf_row["Upper_Shadow_Bottom"]
        lower_top, lower_bot = htf_row["Lower_Shadow_Top"], htf_row["Lower_Shadow_Bottom"]

        if not self.position:
            # Медвежий вход
            if low <= upper_top and high >= upper_bot:
                print(f"[{self.data.index[-1]}] ВЕРХНЯЯ ТЕНЬ. Low={low:.5f} High={high:.5f}")
                sl = close + 0.0010
                tp = close - 0.0020
                self.sell(size=0.1, sl=sl, tp=tp)

            # Бычий вход
            if low <= lower_top and high >= lower_bot:
                print(f"[{self.data.index[-1]}] НИЖНЯЯ ТЕНЬ. Low={low:.5f} High={high:.5f}")
                sl = close - 0.0010
                tp = close + 0.0020
                self.buy(size=0.1, sl=sl, tp=tp)

bt = Backtest(df_ltf, FractalICTStrategy, cash=10000, commission=0.0)
stats = bt.run()
print(stats)
bt.plot()
