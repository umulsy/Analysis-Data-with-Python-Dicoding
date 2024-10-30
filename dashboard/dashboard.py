import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from func import DataAnalyzer, BrazilMapPlotter
from babel.numbers import format_currency

# set 
sns.set(style='dark')
st.set_option('deprecation.showPyplotGlobalUse', False)

#dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv('geolocation_dataset.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')


for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    # Title
    st.title("Olist E-Commerce by Umul")

    # Logo Image
    st.image("Olist.png")

    # Date Range
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    # Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Title
st.header("E-Commerce Dashboard :convenience_store:")

# Daily Orders
st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#074B83"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Customer Spend Money
st.subheader("Customer Spend Money")
col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(sum_spend_df["total_spend"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Spend: **{total_spend}**")

with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "IDR", locale="id_ID")
    st.markdown(f"Average Spend: **{avg_spend}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    sum_spend_df["order_approved_at"],
    sum_spend_df["total_spend"],
    marker="o",
    linewidth=2,
    color="#074B83"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Order Items
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

colors = ["#0E8CF2", "#58AFF6", "#58AFF6", "#58AFF6", "#58AFF6"]

sns.barplot(x="product_count", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0], hue="product_category_name", legend=False)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=50)
ax[0].tick_params(axis ='y', labelsize=35)
ax[0].tick_params(axis ='x', labelsize=30)

sns.barplot(x="product_count", y="product_category_name", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1], hue="product_category_name", legend=False)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# RFM Analysis Section
st.subheader("RFM Analysis")

# Calculate Recency, Frequency, and Monetary values
import datetime as dt

# Reference date for recency calculation
snapshot_date = max(all_df["order_purchase_timestamp"]) + dt.timedelta(days=1)

# Aggregate data to calculate RFM metrics
rfm_df = all_df.groupby("customer_unique_id").agg({
    "order_purchase_timestamp": lambda x: (snapshot_date - x.max()).days,  # Recency
    "order_id": "count",  # Frequency
    "payment_value": "sum"  # Monetary
}).rename(columns={
    "order_purchase_timestamp": "Recency",
    "order_id": "Frequency",
    "payment_value": "Monetary"
})

# Display summary metrics
avg_recency = rfm_df["Recency"].mean()
avg_frequency = rfm_df["Frequency"].mean()
avg_monetary = rfm_df["Monetary"].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**Average Recency:** {avg_recency:.2f} days")
with col2:
    st.markdown(f"**Average Frequency:** {avg_frequency:.2f} orders")
with col3:
    st.markdown(f"**Average Monetary Value:** {format_currency(avg_monetary, 'IDR', locale='id_ID')}")

# RFM Segmentation with Quantiles
rfm_df["R_Score"] = pd.qcut(rfm_df["Recency"], q=4, labels=[4, 3, 2, 1])
rfm_df["F_Score"] = pd.qcut(rfm_df["Frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4])
rfm_df["M_Score"] = pd.qcut(rfm_df["Monetary"], q=4, labels=[1, 2, 3, 4])

# Combine RFM Scores
rfm_df["RFM_Segment"] = rfm_df["R_Score"].astype(str) + rfm_df["F_Score"].astype(str) + rfm_df["M_Score"].astype(str)
rfm_df["RFM_Score"] = rfm_df[["R_Score", "F_Score", "M_Score"]].sum(axis=1)

# Plot RFM Distributions
fig, ax = plt.subplots(1, 3, figsize=(18, 6))
sns.histplot(rfm_df["Recency"], bins=20, kde=True, color="#074B83", ax=ax[0])
ax[0].set_title("Recency Distribution")
ax[0].set_xlabel("Days since last order")

sns.histplot(rfm_df["Frequency"], bins=20, kde=True, color="#58AFF6", ax=ax[1])
ax[1].set_title("Frequency Distribution")
ax[1].set_xlabel("Number of Orders")

sns.histplot(rfm_df["Monetary"], bins=20, kde=True, color="#0E8CF2", ax=ax[2])
ax[2].set_title("Monetary Distribution")
ax[2].set_xlabel("Total Spend (IDR)")

st.pyplot(fig)

# Segment Summary
rfm_segments_summary = rfm_df["RFM_Segment"].value_counts().reset_index()
rfm_segments_summary.columns = ["RFM Segment", "Count"]
st.write(rfm_segments_summary)


# Customer Demographic
st.subheader("Customer Demographic")
tab1, tab2, tab3 = st.tabs(["State", "Order Status", "Geolocation"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
            y=state.customer_count.values, 
            data=state,
            palette=["#0E8CF2" if score == most_common_state else "#58AFF6" for score in state.customer_state.value_counts().index],
            hue=state.customer_state, legend=False)

    plt.title("Number customers from State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab2:
    common_status_ = order_status.value_counts().index[0]
    st.markdown(f"Most Common Order Status: **{common_status_}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=order_status.index,
            y=order_status.values,
            order=order_status.index,
            palette=["#0E8CF2" if score == common_status else "#58AFF6" for score in order_status.index],
            hue=order_status.index, legend=False)
    
    plt.title("Order Status", fontsize=15)
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab3:
    map_plot.plot()

    with st.expander("See Explanation"):
        st.write('Terdapat lebih banyak pelanggan di bagian tenggara dan selatan. Informasi lainnya, ada lebih banyak pelanggan di kota-kota yang merupakan ibu kota (São Paulo, Rio de Janeiro, Porto Alegre, dan lainnya).')

    st.caption('Copyright (C) Umul Syarifah. 2024')