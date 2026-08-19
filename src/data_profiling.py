import pandas as pd
import os

def profile_data():
    raw_dir = os.path.join('data', 'raw')
    report_path = 'data_profiling_report.txt'
    
    # The exact 9 expected Olist files
    files = [
        'olist_orders_dataset.csv',
        'olist_order_items_dataset.csv',
        'olist_products_dataset.csv',
        'olist_customers_dataset.csv',
        'olist_sellers_dataset.csv',
        'olist_order_payments_dataset.csv',
        'olist_order_reviews_dataset.csv',
        'olist_geolocation_dataset.csv',
        'product_category_name_translation.csv'
    ]

    print("Starting Data Profiling. Please wait...")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=== OLIST DATA PROFILING REPORT ===\n")
        f.write("Generated to understand data structure, missing values, and data types.\n\n")

        for file in files:
            file_path = os.path.join(raw_dir, file)
            
            if not os.path.exists(file_path):
                f.write(f"❌ MISSING FILE: {file}\n")
                f.write("-" * 50 + "\n\n")
                continue
                
            try:
                df = pd.read_csv(file_path)
                
                # Basic Stats
                f.write(f"📊 Dataset: {file}\n")
                f.write(f"Rows: {df.shape[0]:,}\n")
                f.write(f"Columns: {df.shape[1]}\n")
                
                # Check for Duplicates
                dupes = df.duplicated().sum()
                f.write(f"Duplicate Rows: {dupes}\n")
                
                missing = df.isnull().sum()
                missing = missing[missing > 0]
                if not missing.empty:
                    f.write("Missing Values:\n")
                    for col, val in missing.items():
                        percentage = (val / df.shape[0]) * 100
                        f.write(f"  - {col}: {val:,} missing ({percentage:.2f}%)\n")
                else:
                    f.write("Missing Values: None\n")
                    
                f.write("Data Types:\n")
                for col, dtype in df.dtypes.items():
                    f.write(f"  - {col}: {dtype}\n")
                    
                f.write("-" * 50 + "\n\n")
                print(f"Successfully profiled: {file}")
                
            except Exception as e:
                f.write(f"❌ ERROR reading {file}: {e}\n")
                f.write("-" * 50 + "\n\n")
                print(f"Error profiling: {file}")

    print(f"\n✅ Profiling complete! Please open '{report_path}' in your VS Code Explorer to see the results.")

if __name__ == "__main__":
    profile_data()
