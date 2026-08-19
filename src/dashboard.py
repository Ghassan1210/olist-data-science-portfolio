import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set up the visual layout of the web page
st.set_page_config(page_title="Olist Analytics Dashboard", page_icon="🛒", layout="wide")

# @st.cache_data tells the app to remember the data so it doesn't reload on every click!
@st.cache_data
def load_data():
    processed_dir = os.path.join('data', 'processed')
    
    # Load only the data we need for the dashboard to keep it fast
    orders = pd.read_csv(os.path.join(processed_dir, 'cleaned_orders.csv'), 
                         parse_dates=['order_purchase_timestamp'])
    items = pd.read_csv(os.path.join(processed_dir, 'cleaned_order_items.csv'))
    products = pd.read_csv(os.path.join(processed_dir, 'cleaned_products.csv'))
    
    # Merge data (Orders + Items + Products)
    delivered = orders[orders['order_status'] == 'delivered'].copy()
    df = delivered.merge(items, on='order_id').merge(
        products[['product_id', 'product_category_name']], 
        on='product_id', 
        how='left'
    )
    return df


@st.cache_data
def load_rfm_data():
    processed_dir = os.path.join('data', 'processed')
    rfm_path = os.path.join(processed_dir, 'rfm_segments.csv')
    if os.path.exists(rfm_path):
        return pd.read_csv(rfm_path)
    return None

def main():
    # Dashboard Header
    st.title("🛒 Olist E-Commerce Business Dashboard")
    st.markdown("Welcome to the interactive analytics dashboard for the Brazilian E-Commerce dataset. **Data processed perfectly!**")
    
    # Load the data
    with st.spinner('Loading millions of data points...'):
        df = load_data()
        rfm = load_rfm_data()
    
    st.divider()

    st.subheader("📊 Key Performance Indicators")
    
    # Create 3 columns for our top metrics
    col1, col2, col3 = st.columns(3)
    
    total_revenue = df['price'].sum()
    total_orders = df['order_id'].nunique()
    total_items = len(df)
    
    col1.metric("Total Revenue", f"R$ {total_revenue:,.2f}")
    col2.metric("Total Orders Delivered", f"{total_orders:,}")
    col3.metric("Total Items Sold", f"{total_items:,}")
    
    st.divider()

    st.subheader("📈 Revenue Over Time")
    
    # We must reset the index to plot correctly in Streamlit
    df_time = df.copy()
    df_time.set_index('order_purchase_timestamp', inplace=True)
    monthly_rev = df_time['price'].resample('ME').sum()
    
    # Create the Revenue Chart
    fig_rev, ax_rev = plt.subplots(figsize=(12, 4))
    sns.lineplot(x=monthly_rev.index, y=monthly_rev.values, ax=ax_rev, color='#2e86c1', linewidth=2.5)
    ax_rev.set_ylabel("Revenue (BRL)", fontweight='bold')
    ax_rev.set_xlabel("Date", fontweight='bold')
    ax_rev.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig_rev)
    
    st.divider()

    st.subheader("🏆 Top 10 Product Categories")
    
    # Calculate top categories
    top_cats = df['product_category_name'].value_counts().head(10)
    
    # Create the Bar Chart
    fig_cat, ax_cat = plt.subplots(figsize=(12, 5))
    sns.barplot(x=top_cats.values, y=top_cats.index, palette='magma', ax=ax_cat, hue=top_cats.index, legend=False)
    ax_cat.set_xlabel("Total Items Sold", fontweight='bold')
    ax_cat.set_ylabel("Category", fontweight='bold')
    st.pyplot(fig_cat)

    if rfm is not None:
        st.divider()
        st.subheader("🎯 Customer Segmentation (Machine Learning)")
        st.markdown("Using an **RFM Model** (Recency, Frequency, Monetary) to group customers by purchasing behavior.")

        col_rfm1, col_rfm2 = st.columns([1, 2])
        segment_counts = rfm['Segment'].value_counts()

        with col_rfm1:
            st.dataframe(
                segment_counts.reset_index().rename(columns={'count': 'Customers', 'Segment': 'Segment'})
            )

        with col_rfm2:
            fig_rfm, ax_rfm = plt.subplots(figsize=(10, 5))
            sns.barplot(
                x=segment_counts.values,
                y=segment_counts.index,
                palette='Set2',
                ax=ax_rfm,
                hue=segment_counts.index,
                legend=False,
            )
            ax_rfm.set_xlabel("Number of Customers", fontweight='bold')
            ax_rfm.set_ylabel("")
            st.pyplot(fig_rfm)
    
    st.markdown("---")
    st.caption("Dashboard built with ❤️ using Python and Streamlit.")

if __name__ == "__main__":
    main()
