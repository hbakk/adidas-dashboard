import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# Streamlit Page Configuration
st.set_page_config(page_title="Adidas Interactive Sales Dashboard", page_icon="👟", layout="wide")

st.title("👟 Adidas Interactive Sales Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# File uploader
fl = st.file_uploader(":file_folder: Upload Adidas Sales File", type=["csv", "xlsx"])

if fl is not None:
    filename = fl.name
    st.write(f"**Uploaded File:** {filename}")

    try:
        if filename.endswith(('csv', 'txt')):
            df = pd.read_csv(fl, encoding='ISO-8859-1', delimiter=';')
        else:
            df = pd.read_excel(fl)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # Convert InvoiceDate column
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors='coerce')

    # Clean numeric columns
    for col in ['TotalSales', 'OperatingProfit', 'PriceperUnit']:
        df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Sidebar Filters
    st.sidebar.header("Filter Data: ")
    region = st.sidebar.multiselect("Pick Region", df["Region"].unique())
    state = st.sidebar.multiselect("Pick State", df["State"].unique())
    city = st.sidebar.multiselect("Pick City", df["City"].unique())

    filtered_df = df.copy()

    if region:
        filtered_df = filtered_df[filtered_df["Region"].isin(region)]
    if state:
        filtered_df = filtered_df[filtered_df["State"].isin(state)]
    if city:
        filtered_df = filtered_df[filtered_df["City"].isin(city)]

    # Date Filter
    col1, col2 = st.columns((2))
    startDate = filtered_df["InvoiceDate"].min()
    endDate = filtered_df["InvoiceDate"].max()

    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))

    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate))

    filtered_df = filtered_df[(filtered_df["InvoiceDate"] >= date1) & (filtered_df["InvoiceDate"] <= date2)].copy()

    # KPIs
    total_sales = filtered_df["TotalSales"].sum()
    total_profit = filtered_df["OperatingProfit"].sum()
    total_units = filtered_df["UnitsSold"].sum()
    total_orders = filtered_df.shape[0]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(label="Total Sales", value=f"${total_sales:,.0f}")
    kpi2.metric(label="Total Profit", value=f"${total_profit:,.0f}")
    kpi3.metric(label="Units Sold", value=f"{total_units:,}")
    kpi4.metric(label="Total Orders", value=f"{total_orders}")

    # Total Sales by Retailer
    st.subheader("Total Sales by Retailer")
    retailer_df = filtered_df.groupby("Retailer", as_index=False)["TotalSales"].sum()
    fig1 = px.bar(retailer_df, x="Retailer", y="TotalSales", text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)

    # Total Sales Over Time
    st.subheader("Total Sales Over Time")
    filtered_df["Month_Year"] = filtered_df["InvoiceDate"].dt.to_period("M").astype(str)
    time_df = filtered_df.groupby("Month_Year", as_index=False)["TotalSales"].sum()
    fig2 = px.line(time_df, x="Month_Year", y="TotalSales")
    st.plotly_chart(fig2, use_container_width=True)

    # Treemap Sales by Region & City
    st.subheader("Total Sales by Region and City in Treemap")
    fig3 = px.treemap(filtered_df, path=["Region", "City"], values="TotalSales")
    st.plotly_chart(fig3, use_container_width=True)

    # Sales & Units Sold by State
    st.subheader("Total Sales and Units Sold by State")
    state_df = filtered_df.groupby("State", as_index=False).agg({"TotalSales": "sum", "UnitsSold": "sum"})
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=state_df['State'], y=state_df['TotalSales'], name='Total Sales'))
    fig4.add_trace(go.Scatter(x=state_df['State'], y=state_df['UnitsSold'], name='Units Sold', yaxis="y2"))
    fig4.update_layout(yaxis2=dict(overlaying='y', side='right', title='Units Sold'))
    st.plotly_chart(fig4, use_container_width=True)

    # Pie Chart: Retailer Wise
    chart1, chart2 = st.columns((2))
    with chart1:
        st.subheader("Retailer wise Sales")
        fig5 = px.pie(filtered_df, values="TotalSales", names="Retailer", hole=0.4)
        st.plotly_chart(fig5, use_container_width=True)

    # Pie Chart: Product Wise
    with chart2:
        st.subheader("Product wise Sales")
        fig6 = px.pie(filtered_df, values="TotalSales", names="Product", hole=0.4)
        st.plotly_chart(fig6, use_container_width=True)

    # Download Filtered Data
    with st.expander("Download Filtered Data"):
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Filtered Data", data=csv, file_name="Filtered_Adidas_Data.csv", mime="text/csv")

    # View Filtered Data
    with st.expander("View Filtered Data"):
        st.dataframe(filtered_df)

else:
    st.warning("Please upload a valid Adidas Sales file to proceed.")