# USA Airline Delay Causes Dashboard

Interactive Streamlit dashboard exploring US flight delays and cancellations by year, month, state, and airport.


## Questions explored
- What causes most delays, and how does it vary by month?
- How do delays/cancellations compare with the previous year?
- Which states and airports are most affected relative to flight volume?


## Data
- Taken from Kaggle

## Approach
- Merged datasets on IATA code; removed airports without valid codes
- Used rates (delayed + cancelled ÷ total flights) instead of raw counts so busy airports don't dominate
- Grouped delay causes under 5% out of the pie for readability

## Features
- Year/month filters, YoY change metrics, cause breakdown, gauges, monthly trends, state choropleth, top-10 airports

## Tech
Python, Streamlit, pandas, Plotly, Matplotlib

## Run locally
pip install -r requirements.txt
streamlit run app.py

## Limitations / next steps
- (e.g. add carrier filter, cache data loading, add delay duration analysis)
