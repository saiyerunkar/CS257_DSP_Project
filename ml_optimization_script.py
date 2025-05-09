from flask import Flask, jsonify
import mysql.connector
import time
import re  # for regex handling
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)

# Load ML model on startup from query_logs
print("Training ML model on historical query logs...")
conn_ml = mysql.connector.connect(
    host='localhost',
    user='saiyeru',
    password='Admin@25',
    database='ecommerce_db'
)
cursor_ml = conn_ml.cursor()
cursor_ml.execute("SELECT query_text, execution_time FROM query_logs_optimized")
data = cursor_ml.fetchall()
df = pd.DataFrame(data, columns=['query_text', 'execution_time'])
df['query_length'] = df['query_text'].apply(len)
df['num_keywords'] = df['query_text'].apply(lambda x: x.lower().count("join") + x.lower().count("select"))
X_train = df[['query_length', 'num_keywords']]
y_train = df['execution_time']
ml_model = RandomForestRegressor()
ml_model.fit(X_train, y_train)
cursor_ml.close()
conn_ml.close()

candidate_queries = [
    "SELECT SQL_NO_CACHE p.name, r.rating, r.review_text FROM products p JOIN reviews AS r ON p.product_id = r.product_id WHERE r.rating >= 4",
    "SELECT SQL_NO_CACHE order_id, total_price FROM orders WHERE total_price > 1500",
    "SELECT SQL_NO_CACHE name, stock FROM products WHERE stock < 10",
    "SELECT SQL_NO_CACHE product_id, AVG(rating) AS avg_rating FROM reviews GROUP BY product_id HAVING avg_rating > 4.5",
    "SELECT SQL_NO_CACHE name FROM products WHERE product_id IN (SELECT product_id FROM reviews WHERE rating = 5)"
]

@app.route('/query/<int:qid>', methods=['GET'])
def run_query(qid):
    if qid >= len(candidate_queries) or qid < 0:
        return jsonify({"error": "Invalid query ID"})

    query = candidate_queries[qid]
    original_query = query
    applied_optimizations = []

    # ML Prediction Block
    features = pd.DataFrame([{ 
        'query_length': len(query),
        'num_keywords': query.lower().count("join") + query.lower().count("select")
    }])
    predicted_time = ml_model.predict(features)[0]

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='saiyeru',
            password='Admin@25',
            database='ecommerce_db'
        )
        cursor = conn.cursor()

        if re.search(r"SELECT\\s+\\*", query, re.IGNORECASE):
            query = re.sub(r"SELECT\\s+\\*", "SELECT SQL_NO_CACHE *", query, flags=re.IGNORECASE)
            applied_optimizations.append("Replaced SELECT * with SQL_NO_CACHE")

        if re.search(r"JOIN\\s+reviews(\\s+AS)?\\s+r", query, re.IGNORECASE) and "USE INDEX" not in query.upper():
            query = re.sub(r"JOIN\\s+reviews(\\s+AS)?\\s+r", "JOIN reviews AS r USE INDEX (idx_reviews_product)", query, flags=re.IGNORECASE)
            applied_optimizations.append("Added USE INDEX on reviews.product_id")

        if re.search(r"WHERE\\s+stock\\s*<", query, re.IGNORECASE):
            try:
                cursor.execute("CREATE INDEX idx_stock ON products(stock)")
                applied_optimizations.append("Created index on products.stock")
            except mysql.connector.Error as err:
                if err.errno != 1061:
                    raise

        if "orders" in query and "total_price" in query:
            try:
                cursor.execute("CREATE INDEX idx_orders_price ON orders(total_price)")
                applied_optimizations.append("Created index on orders.total_price")
            except mysql.connector.Error as err:
                if err.errno != 1061:
                    raise

        if "GROUP BY product_id" in query and "reviews" in query:
            try:
                cursor.execute("CREATE INDEX idx_reviews_rating ON reviews(rating)")
                cursor.execute("CREATE INDEX idx_reviews_product ON reviews(product_id)")
                applied_optimizations.append("Created index on reviews.rating and reviews.product_id")
            except mysql.connector.Error as err:
                if err.errno != 1061:
                    raise

        if "IN (SELECT" in query.upper():
            applied_optimizations.append("Detected subquery pattern – consider EXISTS or join rewrite")

        conn.commit()

        # Execute query
        start_time = time.time()
        cursor.execute(query)
        
        try:
            results = cursor.fetchall()
        except:
            results = []
        exec_time = time.time() - start_time

        cursor.execute(
            "INSERT INTO query_logs_optimized (query_text, execution_time) VALUES (%s, %s)",
            (query, exec_time)
        )
        conn.commit()
        cursor.close()
        conn.close()
        is_optimized = bool(applied_optimizations)

        return jsonify({
            "query_id": qid,
            "optimized_query": query,
            "predicted_execution_time": predicted_time,
            "actual_execution_time": exec_time,
            "optimized": is_optimized,
            "applied_optimizations": applied_optimizations,
            "rows_returned": len(results)
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
