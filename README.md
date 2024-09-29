# Pairs Trading Strategy Using Cointegration

**Author**: Chi-Lin Li

## Project Overview

This project develops a pairs trading strategy using cointegration among NASDAQ-100 equities, specifically within the **QQQ ETF universe**. By identifying securities with mean-reverting price relationships using statistical tests like the Johansen cointegration test and the Augmented Dickey-Fuller test, the strategy dynamically adjusts positions based on asset volatility and the z-score of price spreads. Empirical results demonstrate the effectiveness of the strategy in generating consistent alpha with controlled market exposure.

### Key Features:
- **Cointegration-Based Pairs Trading**: Focus on securities with statistically significant long-term equilibrium relationships.
- **Statistical Tests**: Employs the Engle-Granger two-step method, Johansen cointegration test, and Augmented Dickey-Fuller test to confirm mean reversion.
- **Dynamic Risk Management**: Implements inverse volatility allocation and sliding window techniques for real-time position adjustments.
- **Empirical Validation**: Tested on NASDAQ-100 equities, showing promising results in terms of risk-adjusted returns and scalability.

## Methodologies

### 1. Cointegration Testing
- **Engle-Granger Two-Step Method**: This method is used to identify pairs with a stable long-term relationship.
  - **Step 1**: Regression between two asset price series is conducted to derive a cointegrating equation.
  - **Step 2**: The residuals are tested for stationarity using the Augmented Dickey-Fuller (ADF) test, confirming the presence of cointegration.

### 2. Trading Strategy
- **Trading Signal**: A trade is triggered when the z-score of the spread between the two assets exceeds a specified threshold, indicating a divergence from equilibrium.
  - **Entry**: Go long on the underperforming asset and short on the overperforming asset.
  - **Exit**: Close positions when the spread reverts to its mean.
- **Sliding Window Approach**: Continuously recalculates cointegration and spread metrics over a moving window of historical data.
- **Inverse Volatility Allocation**: Allocates capital inversely proportional to asset volatility, reducing risk exposure and optimizing risk-adjusted returns.

## Empirical Studies

The strategy was tested on daily closing prices from January 2022 to December 2023, focusing on pairs within the NASDAQ-100. Key parameters include:
- **Sliding Window Size**: 30 trading days.
- **Volatility Calculation Period**: 30 trading days.
- **Deviation Threshold**: 2 standard deviations for trade entry; 0.5 standard deviations for exit.

### Performance Summary:
- **Net Profit**: 1.565%
- **Average Loss**: -1.21%
- **Probability of Success Rate (PSR)**: 6.948%
- **Maximum Drawdown**: 14.70%
- **Sharpe Ratio**: -0.08
- **Win Rate**: 34% (Profit-Loss Ratio of 2.15)
- **Annual Volatility**: 17.5%
- **Strategy Capacity**: 1.4M

### Portfolio Insights:
- The strategy demonstrated resilience during volatile periods with a cumulative upward trend in returns, particularly in 2022. However, 2023 showed moderate underperformance.
- **Key Holdings**: SPXL (largest allocation).
- **Drawdown Period**: Most significant around May 2023, aligned with adverse market movements.

## Conclusion

The pairs trading strategy, anchored on cointegration within NASDAQ-100 equities, has proven robust and profitable. It successfully generated consistent alpha while maintaining controlled market exposure. The use of dynamic position adjustments through inverse volatility allocation has shown to be an effective tool in managing risk across various market conditions. The strategy also exhibits scalability, making it adaptable to varying investment volumes.

## Installation

To replicate or modify this project, install the following dependencies:

```bash
pip install numpy pandas statsmodels matplotlib
```

## Usage

1. **Preprocess Data**: Import NASDAQ-100 price data and preprocess it using the Engle-Granger two-step method for cointegration testing.
2. **Trading Signal Generation**: Monitor spreads for deviations from the mean and trigger trades based on z-scores.
3. **Position Adjustment**: Adjust trading positions dynamically using the sliding window and inverse volatility techniques.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contribution

Chi-Lin Li contributed 100% to this project.
