# SQL-Driven E-Commerce Database Optimization
This project demonstrates an end-to-end SQL query optimization system with ML-based prediction, dynamic indexing, real-time monitoring via InfluxDB + Grafana, and benchmarking using JMeter. The backend is powered by a Flask API that applies query rewrites, logs performance metrics, and adapts based on historical patterns.

## How to Compile and Run
1. Clone the repository

2. Install Python dependencies
<br/>Ensure you are using Python 3.8+. Install requirements: pip install mysql-connector-python flask scikit-learn pandas

3. Start MySQL and InfluxDB
<br/>Make sure the following services are running locally:
<br/>MySQL (with user: your_username & password, database: ecommerce_db)
<br/>InfluxDB (port 8086, database: jmeter)

4. Set up MySQL schema and data
<br/>Run the provided SQL setup file or manually execute sql_setup.sql to populate tables like products, reviews, orders.

5. Start the Flask API
<br/>python ml_optimization_script.py
<br/>The API will start at: http://localhost:5000/query/

6. Run JMeter Benchmark
<br/>Open comparison.jmx in Apache JMeter
<br/>Add Backend Listener for InfluxDB
<br/>Ensure JSON Extractors and JSR223 Listeners are properly placed
<br/>Start test

7. View in Grafana
<br/>Access Grafana at http://localhost:3000
<br/>--> Data Source Configuration
<br/>     - Go to: Gear Icon → Data Sources
<br/>     - Click: Add data source
<br/>     - Select: InfluxDB
<br/>     - Set:
<br/>     - URL: http://localhost:8086
<br/>     - Database: jmeter
<br/>     - Version: InfluxQL
<br/>     - Click Save & Test
<br/>Import the dashboard JSON provided or manually configure panels to visualize metrics from:
<br/>  jmeter_metrics (JDBC requests)
<br/>  optimized_query_exec (Flask-optimized responses)

## Requirements & Installation
Python 3.8+
<br/>Flask
<br/>pandas, numpy, scikit-learn
<br/>MySQL Server
<br/>InfluxDB (v1.x)
<br/>Grafana
<br/>Apache JMeter
<br/>MySQL Connector for Python

## Team Contributions
--> Ananya Penuballi
<br/>Designed and created the MySQL schema and dataset for products, reviews, and orders.
<br/>Implemented core SQL optimization logic, including:
<br/>  - Index suggestion and creation logic
<br/>  - Query rewriting strategies (e.g., USE INDEX, SQL_NO_CACHE)
<br/>  - Handling of subqueries, JOINs, and aggregations
  
<br/>--> Sai Sanjay Yerunkar
<br/>Led the Flask API development, responsible for:
<br/>Predictive optimization using a trained ML model (RandomForestRegressor)
<br/>  - Executing optimized queries and logging performance
<br/>  - Returning clean JSON responses with applied optimizations
<br/>Built the JMeter setup for benchmarking each query endpoint
<br/>Integrated InfluxDB and Grafana for real-time visualization
<br/>Ensured correct query execution time logging via JSR223 scripting and JSON extractors

### Notes
The optimized_query_exec InfluxDB measurement logs only query execution time, not API overhead.
<br/>Indexes are created dynamically if missing, with error-handling for duplicate index cases.
<br/>All dashboards are parameterized to allow per-query comparison over time.
