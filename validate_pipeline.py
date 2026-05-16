# C:\Data Engineering\jeans_mfg_data_pipeline\validate_pipeline.py

import os
import psycopg2
import pandas as pd
from pathlib import Path

def check_csv_files():
    print("--- 1. Checking Raw Data CSVs ---")
    data_dir = Path("raw_data_landing_zone")
    files_to_check = ["orders_sample.csv", "bom_sample.csv"]
    
    all_good = True
    for file in files_to_check:
        path = data_dir / file
        if not path.exists():
            print(f"[FAIL] Missing {file}")
            all_good = False
        else:
            df = pd.read_csv(path)
            print(f"[PASS] {file} exists with {len(df)} rows.")
            
    return all_good

def check_postgres_connection(name, host, port, dbname, user, password):
    print(f"--- 2. Checking {name} Connection ({host}:{port}) ---")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=3
        )
        conn.close()
        print(f"[PASS] Successfully connected to {name}.")
        return True
    except Exception as e:
        print(f"[FAIL] Could not connect to {name}: {e}")
        return False

def check_dbt_config():
    print("--- 3. Checking dbt Configuration ---")
    dbt_proj = Path("dbt_project.yml")
    profiles = Path("profiles.yml")
    
    if dbt_proj.exists() and profiles.exists():
        print("[PASS] dbt configuration files found.")
        return True
    else:
        print("[FAIL] Missing dbt_project.yml or profiles.yml.")
        return False

if __name__ == "__main__":
    print("======================================")
    print("Pipeline Readiness Validation Script")
    print("======================================\n")
    
    csv_ok = check_csv_files()
    print("")
    dbt_ok = check_dbt_config()
    print("")
    
    # We test the exposed ports from docker-compose.yml 
    # source: 5433, dwh: 5434
    src_ok = check_postgres_connection("Source DB", "localhost", "5433", "jeans_source_db", "user", "password")
    dwh_ok = check_postgres_connection("DWH DB", "localhost", "5434", "jeans_dwh_db", "user", "password")
    
    print("\n======================================")
    if all([csv_ok, dbt_ok, src_ok, dwh_ok]):
        print("✅ SUCCESS: All pre-flight checks passed! Pipeline is ready.")
    else:
        print("❌ WARNING: Some checks failed. Please review the output above.")
