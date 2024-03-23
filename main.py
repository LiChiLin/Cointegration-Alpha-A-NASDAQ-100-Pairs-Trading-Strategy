# region imports
from AlgorithmImports import *
from QQQ_universe import QQQConstituentsUniverseSelectionModel
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from collections import deque
from datetime import timedelta
# endregion

class Pairs_Trading_Cointegration_Approach(QCAlgorithm):

    undesired_symbols_from_previous_deployment = []
    checked_symbols_from_previous_deployment = False

    def Initialize(self):
        self.SetStartDate(2022, 1, 1)
        self.SetEndDate(2023, 12, 31)
        self.SetCash(1_000_000)
        
        self.spread_mean = 0
        self.spread_std = 0
        
        # Then you can pass these settings when creating your universe
        self.UniverseSettings.DataNormalizationMode = DataNormalizationMode.Raw
        self.AddUniverseSelection(QQQConstituentsUniverseSelectionModel(self, self.UniverseSettings))
        self.symbols = []
        self.spread_window = deque(maxlen=30)  # Rolling window for spread calculation
        self.current_pair = None  # Current pair being traded
        self.last_update_date = None 
        self.last_trade_date = None

    def IsCointegrated(self, series_x, series_y):
        # Drop NaN or infinite values from both series to ensure clean data for OLS regression
        combined = pd.concat([series_x, series_y], axis=1).dropna().replace([np.inf, -np.inf], np.nan).dropna()
        if len(combined) < 20:  # Arbitrary number, ensure enough data points remain for meaningful analysis
            return False  # Not enough data to perform a cointegration test
        
        # Extract series again after cleaning
        clean_series_x = combined.iloc[:, 0]
        clean_series_y = combined.iloc[:, 1]
        
        model = sm.OLS(clean_series_x, clean_series_y).fit()
        residuals = model.resid
        adf_result = adfuller(residuals)
        p_value = adf_result[1]
        # model.param[0] is the beta
        return p_value, model.params[0] if p_value < 0.05 else (1, 0)

    def SelectPairs(self):
        # Request historical data for the symbols
        history = self.History(self.symbols, 30, Resolution.Daily)  # Changed from 60, Resolution.Hour

        # Check if the history request was successful and contains data
        if history.empty:
            self.Debug("No historical data returned.")
            return

        try:
            # Attempt to access the 'close' prices
            prices = history['close'].unstack(level=0)
        except KeyError:
            # Handle cases where 'close' prices are not available
            self.Debug("Unable to access 'close' prices in the historical data.")
            return
        
        lowest_p_value = 1  # Initialize with a value higher than any p-value
        most_cointegrated_pair = None
        strongest_strength = float('-inf')  # Initialize with negative infinity for maximization
        
        # Your existing loop with a slight modification
        for i in range(len(self.symbols)):
            for j in range(i + 1, len(self.symbols)):
                symbol_i = self.symbols[i]
                symbol_j = self.symbols[j]
                p_value, strength = self.IsCointegrated(prices[symbol_i], prices[symbol_j])
                if p_value < 0.05 and p_value < lowest_p_value:
                    if strength > strongest_strength:
                        lowest_p_value = p_value
                        strongest_strength = strength
                        most_cointegrated_pair = (symbol_i, symbol_j)

        if most_cointegrated_pair:
            self.current_pair = most_cointegrated_pair
            self.last_update_date = self.Time  # Record the day of the trade
            self.Debug(f"Most Cointegrated Pair: {self.current_pair}")

    def UpdatePairSelection(self):
        # Ensure there is a pair currently selected
        if self.current_pair is None:
            return
        
        # Fetch historical data for the current pair
        # history = self.History([self.current_pair[0], self.current_pair[1]], 30 * 24, Resolution.Hour)
        history = self.History([self.current_pair[0], self.current_pair[1]], 30, Resolution.Daily)  # Changed from 30 * 24, Resolution.Hour

        # Ensure the history request was successful and contains data
        if history.empty:
            self.Debug("No historical data returned for current pair.")
            return
        
        # Process historical data to get prices
        # Assuming 'close' prices are of interest
        try:
            prices = history['close'].unstack(level=0)
        except KeyError:
            self.Debug("Unable to access 'close' prices in the historical data.")
            return

        # Your existing logic that uses `prices`, for example:
        p_value, _ = self.IsCointegrated(prices[self.current_pair[0]], prices[self.current_pair[1]])
        if p_value >= 0.05:  # If the pair is not cointegrated anymore
            self.Liquidate(self.current_pair[0])
            self.Liquidate(self.current_pair[1])
            self.current_pair = None  # Consider selecting a new pair or handling this scenario appropriately

    def OnSecuritiesChanged(self, changes):
        # Update your symbols list based on the changes
        self.symbols = [security.Symbol for security in changes.AddedSecurities]
        if self.current_pair is None:
            self.Liquidate()
            self.SelectPairs()

    def HistoricalVolatility(self, symbol, days=30, resolution=Resolution.Daily):
        # Request 30 days plus a buffer for rolling calculation
        history = self.History(symbol, days + 1, resolution).close.unstack(level=0)
        
        # Calculate daily returns
        daily_returns = np.log(history / history.shift(1)).dropna()
        
        # Calculate the standard deviation of daily returns
        volatility = daily_returns.std() * np.sqrt(252)  # Annualize the volatility
        
        return volatility[symbol]
    # Trading Bot
    def SetDynamicHoldings(self, asset1, asset2, z_score):
        """Dynamically adjusts positions based on the z-score of the spread."""
        volatility1 = self.HistoricalVolatility(asset1, 30, Resolution.Daily)
        volatility2 = self.HistoricalVolatility(asset2, 30, Resolution.Daily)

        # Calculate the inverse volatilities
        inverse_volatility1 = 1 / volatility1
        inverse_volatility2 = 1 / volatility2

        # Calculate the weights
        weight1 = inverse_volatility1 / (inverse_volatility1 + inverse_volatility2)
        weight2 = inverse_volatility2 / (inverse_volatility1 + inverse_volatility2)

        # Normalize the weights so that their sum of absolute values is 1
        sum_of_weights = abs(weight1) + abs(weight2)
        normalized_weight1 = weight1 / sum_of_weights
        normalized_weight2 = weight2 / sum_of_weights

        # Determine direction based on z-score
        if z_score > 2.0:
            targetholding1 = -abs(normalized_weight1)
            targetholding2 = abs(normalized_weight2)
            self.SetHoldings(asset1, targetholding1)
            self.SetHoldings(asset2, targetholding2)
        elif z_score < -2.0:
            targetholding1 = abs(normalized_weight1)
            targetholding2 = -abs(normalized_weight2)
            self.SetHoldings(asset1, targetholding1)
            self.SetHoldings(asset2, targetholding2)
       
        currentWeight1 = self.Portfolio[asset1].Quantity * self.Securities[asset1].Price / self.Portfolio.TotalPortfolioValue
        currentWeight2 = self.Portfolio[asset2].Quantity * self.Securities[asset2].Price / self.Portfolio.TotalPortfolioValue
        self.Debug(f"Current Time {self.Time}")
        self.Debug(f"Current Holding {asset1}: {currentWeight1}, {asset2}: {currentWeight2}")
        self.Debug(f"Current Std {self.spread_std}")

    def OnData(self, data: Slice):
        if not self.current_pair:
            return  # No pair selected

        asset1, asset2 = self.current_pair
        if not (data.ContainsKey(asset1) and data.ContainsKey(asset2)):
            return  # Ensure we have data for both assets

        # Check if 30 days have passed since the last update or if it's the first time updating
        if self.last_update_date is None or (self.Time - self.last_update_date).days >= 90:
            self.UpdatePairSelection()
            self.last_update_date = self.Time  # Update the last update date to the current date
            if self.current_pair is None:
                self.SelectPairs()
                return

        asset1_price = data[self.current_pair[0]].Price
        asset2_price = data[self.current_pair[1]].Price

        # Ensure prices are valid
        if asset1_price <= 0 or asset2_price <= 0:
            self.Debug(f"Invalid price for assets in the pair {self.current_pair}.")
            return

        # Check for prices greater than 0 to avoid math errors with logarithms
        if self.last_trade_date is None or self.Time.date() > self.last_trade_date.date():
            # Calculate the logarithmic spread
            current_log_spread = np.log(asset1_price) - np.log(asset2_price)
            self.spread_window.append(current_log_spread)

            # Calculate the mean and standard deviation of the logarithmic spread
            self.spread_mean = np.mean(self.spread_window)
            self.spread_std = np.std(self.spread_window)

            # Calculate the z-score of the current logarithmic spread, if std is not zero
            # Trade Once a day
            if self.spread_std > 0:
                z_score = (current_log_spread - self.spread_mean) / self.spread_std
                # Adjust the holdings based on the z-score
                self.SetDynamicHoldings(self.current_pair[0], self.current_pair[1], z_score)
                self.last_trade_date = self.Time
    