import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Bookstore Analytics",
    page_icon="📚",
    layout="wide"
)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

Driver = 'ODBC Driver 18 for SQL Server'
Server = r'sai\SQLEXPRESS'
Database = 'project'

connection_string = (
    f'DRIVER={{{Driver}}};'
    f'SERVER={Server};'
    f'DATABASE={Database};'
    f'Trusted_Connection=yes;'
    f'TrustServerCertificate=yes;'
)

conn = pyodbc.connect(connection_string)


# --------------------------------------------------
# SQL QUERY
# --------------------------------------------------

query = """
SELECT 
    o.Order_ID,
    o.Book_ID,
    o.Customer_ID,
    o.Order_Date,
    o.Quantity,
    o.Total_Amount,

    b.Title,
    b.Author,
    b.Genre,
    b.Published_Year,
    b.Stock,
    b.Price,

    c.Name AS Customer_Name,
    c.Email,
    c.Phone,
    c.City,
    c.Country

FROM Orders AS o

JOIN Books AS b
    ON o.Book_ID = b.Book_ID

JOIN Customers AS c
    ON o.Customer_ID = c.Customer_ID
"""

df = pd.read_sql(query, conn)

conn.close()


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📚 Bookstore Analytics Dashboard")

st.write(
    "Analyze bookstore sales, customers, books and orders."
)


# --------------------------------------------------
# DATE CONVERSION
# --------------------------------------------------

df["Order_Date"] = pd.to_datetime(df["Order_Date"])


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("🔎 Filters")

selected_genre = st.sidebar.selectbox(
    "Select Genre",
    ["All"] + sorted(df["Genre"].unique().tolist())
)

selected_city = st.sidebar.selectbox(
    "Select City",
    ["All"] + sorted(df["City"].unique().tolist())
)


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()

if selected_genre != "All":
    filtered_df = filtered_df[
        filtered_df["Genre"] == selected_genre
    ]

if selected_city != "All":
    filtered_df = filtered_df[
        filtered_df["City"] == selected_city
    ]


# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_revenue = filtered_df["Total_Amount"].sum()

total_orders = filtered_df["Order_ID"].nunique()

total_books_sold = filtered_df["Quantity"].sum()

total_customers = filtered_df["Customer_ID"].nunique()


# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Revenue",
    f"₹{total_revenue:,.2f}"
)

col2.metric(
    "📦 Total Orders",
    total_orders
)

col3.metric(
    "📚 Books Sold",
    total_books_sold
)

col4.metric(
    "👥 Customers",
    total_customers
)


# --------------------------------------------------
# TOP BOOKS + GENRE REVENUE
# --------------------------------------------------

col1, col2 = st.columns(2)


# ---------------- TOP BOOKS ----------------

with col1:

    st.subheader("📚 Top 10 Best-Selling Books")

    best_books = (
        filtered_df
        .groupby("Title")["Quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        best_books,
        x="Title",
        y="Quantity",
        title="Top 10 Best-Selling Books",
        labels={
            "Title": "Book",
            "Quantity": "Quantity Sold"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ---------------- GENRE REVENUE ----------------

with col2:

    st.subheader("💰 Revenue by Genre")

    genre_revenue = (
        filtered_df
        .groupby("Genre")["Total_Amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig = px.bar(
        genre_revenue,
        x="Genre",
        y="Total_Amount",
        title="Revenue by Genre",
        labels={
            "Genre": "Genre",
            "Total_Amount": "Revenue"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# --------------------------------------------------
# TOP CUSTOMERS
# --------------------------------------------------

st.subheader("👥 Top 10 Customers")

top_customers = (
    filtered_df
    .groupby("Customer_Name")["Total_Amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig = px.bar(
    top_customers,
    x="Customer_Name",
    y="Total_Amount",
    title="Top Customers by Spending",
    labels={
        "Customer_Name": "Customer",
        "Total_Amount": "Total Spending"
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# SALES OVER TIME
# --------------------------------------------------

st.subheader("📈 Sales Over Time")

sales_over_time = (
    filtered_df
    .groupby("Order_Date")["Total_Amount"]
    .sum()
    .reset_index()
)

fig = px.line(
    sales_over_time,
    x="Order_Date",
    y="Total_Amount",
    markers=True,
    title="Sales Over Time",
    labels={
        "Order_Date": "Date",
        "Total_Amount": "Revenue"
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# REVENUE BY CITY
# --------------------------------------------------

st.subheader("🌍 Revenue by City")

city_revenue = (
    filtered_df
    .groupby("City")["Total_Amount"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig = px.bar(
    city_revenue,
    x="City",
    y="Total_Amount",
    title="Revenue by City",
    labels={
        "City": "City",
        "Total_Amount": "Revenue"
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)