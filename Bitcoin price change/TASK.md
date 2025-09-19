# Screening Task: Anomaly Detection in Time Series

## Steps

1. Load a CSV file containing hourly OHLC data.

2. Calculate the percentage change from `close[t-1]` to `close[t]`.

3. Flag all timestamps where the absolute change is greater than 3%.

4. Display the first 5 of these timestamps in a table, showing **Date** and **% Change**.
