import pandas as pd
import psycopg2

conn = psycopg2.connect(host='localhost', port=5433, dbname='jeans_source_db', user='user', password='password')

print("--- SCHEMA INFO ---")
df_schemas = pd.read_sql("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE 'fct_%' OR table_name LIKE 'stg_%'", conn)
print(df_schemas)

if not df_schemas.empty:
    schema_name = df_schemas['table_schema'].iloc[0]
    
    print("\n--- FCT ORDER FULFILLMENT ---")
    query1 = f"SELECT current_stage, is_shipped, COUNT(distinct order_form_no) as num_orders FROM {schema_name}.fct_order_fulfillment GROUP BY current_stage, is_shipped"
    df_fct = pd.read_sql(query1, conn)
    print(df_fct)

    print("\n--- STUCK IN PRODUCTION ---")
    query2 = f"SELECT current_stage, AVG(EXTRACT(DAY FROM (CURRENT_TIMESTAMP - last_stage_updated_at))) as avg_days_stuck FROM {schema_name}.fct_order_fulfillment WHERE not is_shipped GROUP BY current_stage"
    df_stuck = pd.read_sql(query2, conn)
    print(df_stuck)
