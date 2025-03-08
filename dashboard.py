import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from babel.numbers import format_currency

def create_purchase_month(all_df):
    all_df["order_purchase_month"] = all_df["order_purchase_month"]
    order_trend = all_df.groupby("order_purchase_month")["order_id"].count()
    return order_trend

# untuk menyiapkan top_categories (top kategori yang paling laris)
def create_top_categories(all_df):
    top_categories = all_df.groupby("product_category_name")["order_id"].count().sort_values(ascending=False).head(10)
    return top_categories

# untuk menyiapkan top_states (states dengan customer terbanyak)
def create_top_states(all_df):
    top_states = all_df.groupby("customer_state")["customer_id"].nunique().sort_values(ascending=False).head(10)
    return top_states

# untuk menyiapkan rfm_df (rfm analysis)
def create_rfm_df(all_df):
    rfm_df = all_df.groupby("customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "count",
        "payment_value_x": "sum"
    })

    rfm_df.columns = ["customer_id", "order_purchase_timestamp", "frequency", "monetary"]

    latest_date = all_df["order_purchase_timestamp"].max()
    rfm_df["recency"] = (latest_date - rfm_df["order_purchase_timestamp"]).dt.days

    rfm_df.drop("order_purchase_timestamp", axis=1, inplace=True)
    return rfm_df

# Memanggil dataset
all_df = pd.read_csv("main_data.csv")

# Mengurutkan dataframe berdasarkan order_purchase_timestamp
datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Membuat Komponen Filter
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo
    st.image("https://dicoding-web-img.sgp1.cdn.digitaloceanspaces.com/original/commons/dbs/cc-dbsf-no-tagline.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Penjelasan dari dashboard
    st.subheader("Tren pesanan dari waktu kewaktu")
    st.text("Berisikan total pembelian pada waktu yang telah ditentukan")
    st.subheader("10 Kategori produk terlaris")
    st.text("Berisikan kategori produk dengan pembelian terbanyak")
    st.subheader("10 Negara bagian customer terbanyak")
    st.text("Berisikan daftar negara bagian dengan customer/pelanggan terbanyak")
    st.subheader("Pelanggan terbaik based on RFM Parameters")
    st.text("Berisikan data customer terbaik yang diperoleh dari RFM analysis")

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]


# memanggil helper function
purchase_month = create_purchase_month(main_df)
top_categories = create_top_categories(main_df)
top_states = create_top_states(main_df)
rfm_df = create_rfm_df(main_df)

# Judul
st.title('Proyek Analisis Data: E-Commerce Public Dataset')
st.markdown(
    """
    - **Nama:** Bayu Pratama Putra 
    - **Email:** mc476d5y0372@student.devacademy.id
    - **Cohord ID:** MC476D5Y0372
    """
)

# Visualisasi Data
# Tren Pesanan dari waktu ke waktu
st.subheader("Tren Pesanan dari waktu ke waktu")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    purchase_month.index, 
    purchase_month.values, 
    marker="o", 
    linestyle="-", 
    color="b"
)
ax.set_xlabel("Bulan dan Tahun")
ax.set_ylabel("Jumlah Pesanan")
ax.set_title("Tren Jumlah Pesanan dari Waktu ke Waktu")
ax.tick_params(axis='x', rotation=45)
ax.grid()

st.pyplot(fig)

# Kategori Produk Terlaris
st.subheader("10 Kategori Produk Terlaris")

fig, ax = plt.subplots(figsize=(12, 6))
top_categories.plot(kind="bar", color="c", ax=ax)
ax.set_xlabel("Kategori Produk")
ax.set_ylabel("Jumlah Penjualan")
ax.set_title("10 Kategori Produk Paling Banyak Terjual")
ax.tick_params(axis='x', rotation=45)
ax.grid(axis="y")

st.pyplot(fig)

# Negara Bagian dengan Pelanggan Terbanyak
st.subheader("10 Negara Bagian Customer Terbanyak")
fig, ax = plt.subplots(figsize=(12, 6))
top_states.plot(kind="barh", color="m", ax=ax)

plt.figure(figsize=(12, 6))
top_states.plot(kind="barh", color="m")
ax.set_ylabel("Negara Bagian")
ax.set_xlabel("Jumlah Pelanggan")
ax.set_title("10 Negara Bagian dengan Pelanggan Terbanyak")
ax.invert_yaxis()
ax.grid(axis="x") 

st.pyplot(fig)

# Pelanggan Terbaik Based on RFM
st.subheader("Pelanggan Terbaik Based on RFM Parameters")

col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "$", locale='en_US') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#72BCD4"] * 5

# Recency
top_recency = rfm_df.sort_values(by="recency", ascending=True).head(5).reset_index()
sns.barplot(y="recency", x=top_recency.index, hue=top_recency.index, data=top_recency, palette=colors, ax=ax[0], legend=False)
ax[0].set_xticks(top_recency.index)
ax[0].set_xticklabels(top_recency["customer_id"].str[:5] + "...", rotation=45)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)

# Frequency
top_frequency = rfm_df.sort_values(by="frequency", ascending=False).head(5).reset_index()
sns.barplot(y="frequency", x=top_frequency.index, hue=top_frequency.index, data=top_frequency, palette=colors, ax=ax[1], legend=False)
ax[1].set_xticks(top_frequency.index)
ax[1].set_xticklabels(top_frequency["customer_id"].str[:5] + "...", rotation=45)
ax[1].set_title("By Frequency", loc="center", fontsize=18)

# Monetary
top_monetary = rfm_df.sort_values(by="monetary", ascending=False).head(5).reset_index()
sns.barplot(y="monetary", x=top_monetary.index, hue=top_monetary.index, data=top_monetary, palette=colors, ax=ax[2], legend=False)
ax[2].set_xticks(top_monetary.index)
ax[2].set_xticklabels(top_monetary["customer_id"].str[:5] + "...", rotation=45)
ax[2].set_title("By Monetary", loc="center", fontsize=18)

plt.suptitle("Best Customer Based on RFM Parameters", fontsize=20)

st.pyplot(fig)