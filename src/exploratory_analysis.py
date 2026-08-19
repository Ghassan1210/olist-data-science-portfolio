import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda():
    processed_dir = os.path.join('data', 'processed')
    reports_dir = 'reports'
    figures_dir = os.path.join(reports_dir, 'figures')
    
    # Create folders for our reports and charts
    os.makedirs(figures_dir, exist_ok=True)
    
    print("🚀 Starting Exploratory Data Analysis (EDA)...\n")
    
    print("1/4 Loading cleaned datasets...")
    # We must tell pandas to parse the date columns again since CSVs store them as text
    orders = pd.read_csv(os.path.join(processed_dir, 'cleaned_orders.csv'), 
                         parse_dates=['order_purchase_timestamp'])
    items = pd.read_csv(os.path.join(processed_dir, 'cleaned_order_items.csv'))
    products = pd.read_csv(os.path.join(processed_dir, 'cleaned_products.csv'))
    
    print("2/4 Merging data to calculate business metrics...")
    # Filter only delivered orders for accurate revenue calculation
    delivered_orders = orders[orders['order_status'] == 'delivered'].copy()
    
    # Merge orders with items to get prices, then with products to get categories
    merged_data = delivered_orders.merge(items, on='order_id', how='inner')
    merged_data = merged_data.merge(products[['product_id', 'product_category_name']], 
                                    on='product_id', how='left')
    
    print("3/4 Generating Revenue Over Time Chart...")
    # Set the date as the index and group by month to get monthly revenue
    merged_data.set_index('order_purchase_timestamp', inplace=True)
    monthly_revenue = merged_data['price'].resample('ME').sum()
    
    # Plot Monthly Revenue
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=monthly_revenue.index, y=monthly_revenue.values, color='blue', linewidth=2)
    plt.title('Total Monthly Revenue (Delivered Orders)', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Revenue (BRL)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'monthly_revenue_trend.png'))
    plt.close()

    print("4/4 Generating Top Product Categories Chart...")
    # Count the number of items sold per category
    top_categories = merged_data['product_category_name'].value_counts().head(10)
    
    # Plot Top Categories
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_categories.values, y=top_categories.index, hue=top_categories.index, legend=False, palette='viridis')
    plt.title('Top 10 Product Categories by Items Sold', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Items Sold', fontsize=12)
    plt.ylabel('Category', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'top_10_categories.png'))
    plt.close()

    print("Writing text summary report...")
    summary_path = os.path.join(reports_dir, 'business_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=== OLIST BUSINESS INSIGHTS SUMMARY ===\n\n")
        f.write(f"Total Delivered Orders: {len(delivered_orders):,}\n")
        f.write(f"Total Revenue (BRL): R$ {merged_data['price'].sum():,.2f}\n")
        f.write(f"Total Items Sold: {len(merged_data):,}\n\n")
        f.write("Top 5 Selling Categories:\n")
        for cat, count in top_categories.head(5).items():
            f.write(f" - {cat}: {count:,} items\n")
            
    print("\n✅ EDA COMPLETE!")
    print(f"Check the '{reports_dir}' folder for the text summary and '{figures_dir}' for your charts!")

if __name__ == "__main__":
    run_eda()
