import pandas as pd
import os

def clean_data():
    raw_dir = os.path.join('data', 'raw')
    processed_dir = os.path.join('data', 'processed')
    
    # Create the processed directory if it doesn't exist
    os.makedirs(processed_dir, exist_ok=True)

    print("🚀 Starting Data Cleaning Process...\n")

    print("1/5 Cleaning Orders Dataset...")
    orders_path = os.path.join(raw_dir, 'olist_orders_dataset.csv')
    orders = pd.read_csv(orders_path)
    
    # Convert all date columns from text (object) to actual Datetime objects
    date_cols = [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col])
    
    # Save to processed folder
    orders.to_csv(os.path.join(processed_dir, 'cleaned_orders.csv'), index=False)

    print("2/5 Cleaning Order Items Dataset...")
    items_path = os.path.join(raw_dir, 'olist_order_items_dataset.csv')
    items = pd.read_csv(items_path)
    
    items['shipping_limit_date'] = pd.to_datetime(items['shipping_limit_date'])
    items.to_csv(os.path.join(processed_dir, 'cleaned_order_items.csv'), index=False)

    print("3/5 Cleaning Order Reviews Dataset...")
    reviews_path = os.path.join(raw_dir, 'olist_order_reviews_dataset.csv')
    reviews = pd.read_csv(reviews_path)
    
    # Fix dates
    reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])
    reviews['review_answer_timestamp'] = pd.to_datetime(reviews['review_answer_timestamp'])
    
    # Fill missing text reviews with placeholders
    reviews['review_comment_title'] = reviews['review_comment_title'].fillna('No Title')
    reviews['review_comment_message'] = reviews['review_comment_message'].fillna('No Message')
    reviews.to_csv(os.path.join(processed_dir, 'cleaned_reviews.csv'), index=False)

    print("4/5 Cleaning Products Dataset...")
    products_path = os.path.join(raw_dir, 'olist_products_dataset.csv')
    products = pd.read_csv(products_path)
    
    # Fill missing categories with 'unknown'
    products['product_category_name'] = products['product_category_name'].fillna('unknown')
    
    # Fill missing physical dimensions with 0
    num_cols = [
        'product_name_lenght', 'product_description_lenght', 'product_photos_qty',
        'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'
    ]
    for col in num_cols:
        products[col] = products[col].fillna(0)
    
    products.to_csv(os.path.join(processed_dir, 'cleaned_products.csv'), index=False)

    print("5/5 Transferring remaining datasets without changes...")
    others = [
        ('olist_customers_dataset.csv', 'cleaned_customers.csv'),
        ('olist_sellers_dataset.csv', 'cleaned_sellers.csv'),
        ('olist_order_payments_dataset.csv', 'cleaned_payments.csv'),
        ('olist_geolocation_dataset.csv', 'cleaned_geolocation.csv'),
        ('product_category_name_translation.csv', 'cleaned_translation.csv')
    ]
    
    for raw_name, clean_name in others:
        df = pd.read_csv(os.path.join(raw_dir, raw_name))
        df.to_csv(os.path.join(processed_dir, clean_name), index=False)

    print("\n✅ DATA CLEANING COMPLETE!")
    print(f"All 9 cleaned and formatted files are ready for analysis in the '{processed_dir}' folder.")

if __name__ == "__main__":
    clean_data()
