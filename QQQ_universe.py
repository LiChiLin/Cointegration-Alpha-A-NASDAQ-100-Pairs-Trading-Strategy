 #region imports
from AlgorithmImports import *
#endregion

class QQQConstituentsUniverseSelectionModel(ETFConstituentsUniverseSelectionModel):
    def __init__(self, algorithm, universe_settings: UniverseSettings = None) -> None:
        self.algorithm = algorithm
        symbol = Symbol.Create("QQQ", SecurityType.Equity, Market.USA)
        super().__init__(symbol, universe_settings, lambda constituents: [c.Symbol for c in constituents]) 
        self.algorithm.Debug(f"Initialized universe selection model for: {symbol.Value}")

