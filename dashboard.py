import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    #File data
    df = pd.read_csv('Financials Sample Data.csv')
    
    df_long = pd.melt(df,
                      id_vars=['Account', 'Businees Unit', 'Currency', 'Year', 'Scenario'],
                      var_name='Month',
                      value_vars=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                      value_name='Amount')
    
    df_long['Amount'] = df_long['Amount'].astype(str)
    df_long['Amount'] = df_long['Amount'].str.replace('$', '')
    df_long['Amount'] = df_long['Amount'].str.replace(',', '')
    df_long['Amount'] = df_long['Amount'].str.replace('(', '-')
    df_long['Amount'] = df_long['Amount'].str.replace(')', '')
    df_long['Amount'] = pd.to_numeric(df_long['Amount'], errors='coerce')
    
    month_to_num = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    df_long['Month_Num'] = df_long['Month'].map(month_to_num)
    df_long['Date'] = pd.to_datetime(df_long['Year'].astype(str) + '-' + 
                                      df_long['Month_Num'].astype(str) + '-01')
    
    return df, df_long

df, df_long = load_data()

#CSS
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0a0a0a;
    }
    
    /* Cards */
    .css-1r6slb0, .css-1v3fvcr {
        background-color: #1a1a2e;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #00ffcc20;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #0d0d0d;
        border-right: 1px solid #00ffcc30;
    }
    
    /* Heading colors */
    h1, h2, h3, .stMarkdown {
        color: #00ffcc !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: #ffd700 !important;
        font-size: 32px !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #cccccc !important;
    }
    
    /* Selectbox dan filter */
    .stSelectbox label, .stMultiSelect label {
        color: #00ffcc !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a2e;
        border-radius: 8px;
        padding: 8px 20px;
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00ffcc;
        color: #0a0a0a;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/null/financial-growth.png", width=60)
    st.markdown("## 📊 **Filter Data**")
    st.markdown("---")
    
    years = sorted(df_long['Year'].unique())
    selected_years = st.multiselect("📅 Pilih Tahun", years, default=[2020, 2021, 2022])
    
    units = df_long['Businees Unit'].unique().tolist()
    selected_units = st.multiselect("🏢 Pilih Business Unit", units, default=units)
    
    scenarios = df_long['Scenario'].unique().tolist()
    selected_scenarios = st.multiselect("📈 Pilih Scenario", scenarios, default=['Actuals'])
    
    accounts = df_long['Account'].unique().tolist()
    selected_accounts = st.multiselect("💰 Pilih Account (Opsional)", accounts, default=accounts[:5])
    
    st.markdown("---")
    st.markdown("### 📌 **Informasi**")
    st.info(f"📊 Data dari {min(years)} - {max(years)}")
    st.caption("Second Dashboard")
    st.caption("Dataset: Financials Sample Data")

filtered_df = df_long[
    (df_long['Year'].isin(selected_years)) &
    (df_long['Businees Unit'].isin(selected_units)) &
    (df_long['Scenario'].isin(selected_scenarios))
]

if selected_accounts:
    filtered_df = filtered_df[filtered_df['Account'].isin(selected_accounts)]

st.markdown("# 📊 **Analisis Biaya Perusahaan**")
st.markdown(f"### Data {min(selected_years)} - {max(selected_years)} | Sumber: Financials Sample Data")
st.markdown("---")

col1, col2, col3 = st.columns(3)

sales_data = filtered_df[filtered_df['Account'] == 'Sales']['Amount'].sum()
expense_data = filtered_df[~filtered_df['Account'].isin(['Sales'])]['Amount'].sum()
profit = sales_data + expense_data  

if sales_data != 0:
    profit_margin = (profit / sales_data) * 100
else:
    profit_margin = 0

with col1:
    st.metric(
        label="💰 **TOTAL PENDAPATAN**",
        value=f"${sales_data/1e6:,.1f} M",
        delta=f"+{profit_margin:.1f}% Margin"
    )

with col2:
    st.metric(
        label="📉 **TOTAL BIAYA**",
        value=f"${abs(expense_data)/1e6:,.1f} M",
        delta=f"{(abs(expense_data)/sales_data)*100:.1f}% dari Revenue"
    )

with col3:
    st.metric(
        label="📈 **LABA BERSIH**",
        value=f"${profit/1e6:,.1f} M",
        delta=f"Profit {profit_margin:.1f}%"
    )

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📋 **Ringkasan Account**")
    account_totals = filtered_df.groupby('Account')['Amount'].sum().sort_values(ascending=False).head(8)
    for acc, val in account_totals.items():
        sign = "💰" if val > 0 else "📉"
        st.markdown(f"{sign} **{acc}**  →  `${abs(val)/1e6:,.1f}M`")

with col2:
    st.markdown("### 📅 **Detail Tahun**")
    year_totals = filtered_df.groupby('Year')['Amount'].sum()
    for year, val in year_totals.items():
        color = "🟢" if val > 0 else "🔴"
        st.markdown(f"{color} **{year}**  →  `Profit ${val/1e6:,.1f}M`")
    
    st.markdown("---")
    st.markdown("### 🏢 **Business Unit**")
    unit_totals = filtered_df.groupby('Businees Unit')['Amount'].sum()
    for unit, val in unit_totals.items():
        st.markdown(f"🏭 **{unit}**  →  `${abs(val)/1e6:,.1f}M`")

with col3:
    st.markdown("### 💵 **NOMINAL**")
    total_sales = filtered_df[filtered_df['Account'] == 'Sales']['Amount'].sum()
    total_exp = filtered_df[~filtered_df['Account'].isin(['Sales'])]['Amount'].sum()
    
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #00ffcc20, #ffd70010); padding:15px; border-radius:15px; border-left:4px solid #00ffcc;">
        <h4 style="margin:0 0 10px 0; color:#00ffcc;">💰 Summary</h4>
        <p style="margin:5px 0;">📈 Revenue: <b style="color:#00ffcc;">${total_sales/1e6:,.1f}M</b></p>
        <p style="margin:5px 0;">📉 Expenses: <b style="color:#ff6b6b;">${abs(total_exp)/1e6:,.1f}M</b></p>
        <p style="margin:5px 0;">📊 Profit: <b style="color:#ffd700;">${(total_sales+total_exp)/1e6:,.1f}M</b></p>
        <hr style="margin:10px 0; border-color:#00ffcc30;">
        <p style="margin:5px 0; font-size:12px;">Profit Margin: <b>{profit_margin:.2f}%</b></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("## 📊 **Visualisasi Data**")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 **Revenue vs Expense per Tahun**")
    
    yearly_sales = filtered_df[filtered_df['Account'] == 'Sales'].groupby('Year')['Amount'].sum().reset_index()
    yearly_sales['Type'] = 'Revenue'
    
    yearly_expense = filtered_df[~filtered_df['Account'].isin(['Sales'])].groupby('Year')['Amount'].sum().reset_index()
    yearly_expense['Amount'] = yearly_expense['Amount'].abs()
    yearly_expense['Type'] = 'Expenses'
    
    bar_data = pd.concat([yearly_sales, yearly_expense])
    
    fig_bar = px.bar(bar_data, x='Year', y='Amount', color='Type',
                     color_discrete_map={'Revenue': '#00ffcc', 'Expenses': '#ff6b6b'},
                     title='Pendapatan vs Biaya per Tahun',
                     text_auto='.1s')
    fig_bar.update_layout(
        plot_bgcolor='#1a1a2e',
        paper_bgcolor='#1a1a2e',
        font_color='white',
        title_font_color='#00ffcc'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.markdown("### 📈 **Tren Profit per Tahun**")
    
    profit_by_year = filtered_df.groupby('Year')['Amount'].sum().reset_index()
    
    fig_line = px.line(profit_by_year, x='Year', y='Amount',
                       title='Trend Profit (Revenue - Expenses)',
                       markers=True, line_shape='spline')
    fig_line.update_traces(line_color='#ffd700', marker_color='#00ffcc', marker_size=10)
    fig_line.add_hline(y=0, line_dash="dash", line_color="red", 
                       annotation_text="Break Even Point")
    fig_line.update_layout(
        plot_bgcolor='#1a1a2e',
        paper_bgcolor='#1a1a2e',
        font_color='white',
        title_font_color='#00ffcc'
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col3:
    st.markdown("### 🌡️ **Heatmap Bulanan**")
    
    monthly_sales = filtered_df[filtered_df['Account'] == 'Sales'].pivot_table(
        index='Year', columns='Month', values='Amount', aggfunc='sum'
    )
    months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_sales = monthly_sales[months_order]
    
    fig_heat = px.imshow(monthly_sales/1e6, 
                         text_auto='.0f',
                         color_continuous_scale='RdYlGn',
                         title='Heatmap Penjualan (juta USD)',
                         labels=dict(x="Bulan", y="Tahun", color="Juta USD"))
    fig_heat.update_layout(
        plot_bgcolor='#1a1a2e',
        paper_bgcolor='#1a1a2e',
        font_color='white',
        title_font_color='#00ffcc'
    )
    st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")
st.markdown("## 📋 **Lihat Data Lengkap**")

tab1, tab2, tab3 = st.tabs(["📊 Ringkasan per Account", "📅 Data per Bulan", "🔍 Raw Data"])

with tab1:
    account_summary = filtered_df.groupby('Account').agg({
        'Amount': 'sum',
        'Businees Unit': 'first',
        'Year': lambda x: f"{min(selected_years)}-{max(selected_years)}"
    }).reset_index()
    account_summary['Amount (M)'] = account_summary['Amount'] / 1e6
    account_summary = account_summary.sort_values('Amount', ascending=False)
    
    st.dataframe(
        account_summary[['Account', 'Businees Unit', 'Amount (M)']].style.format({'Amount (M)': '${:.2f}M'}),
        use_container_width=True,
        height=400
    )

with tab2:
    monthly_data = filtered_df.pivot_table(
        index=['Year', 'Month'], 
        values='Amount', 
        aggfunc='sum'
    ).reset_index()
    
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_data['Month'] = pd.Categorical(monthly_data['Month'], categories=month_order, ordered=True)
    monthly_data = monthly_data.sort_values(['Year', 'Month'])
    monthly_data['Amount (M)'] = monthly_data['Amount'] / 1e6
    
    st.dataframe(
        monthly_data[['Year', 'Month', 'Amount (M)']].style.format({'Amount (M)': '${:.2f}M'}),
        use_container_width=True,
        height=400
    )

with tab3:
    st.dataframe(filtered_df.head(100), use_container_width=True, height=400)

st.markdown("---")
st.markdown("## 💡 **Key Insights**")

insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    unit_profit = filtered_df.groupby('Businees Unit')['Amount'].sum().sort_values(ascending=False)
    top_unit = unit_profit.index[0]
    top_unit_val = unit_profit.values[0]/1e6
    st.info(f"🏆 **Best Performing Unit**\n\n{top_unit} dengan profit ${top_unit_val:.1f}M")

with insight_col2:
    monthly_agg = filtered_df[filtered_df['Account'] == 'Sales'].groupby('Month')['Amount'].sum()
    top_month = monthly_agg.idxmax()
    st.success(f"📅 **Best Sales Month**\n\nBulan {top_month} dengan total sales ${monthly_agg.max()/1e6:.1f}M")

with insight_col3:
    total_profit = filtered_df['Amount'].sum()/1e6
    st.warning(f"📊 **Total Profit periode {min(selected_years)}-{max(selected_years)}**\n\n${total_profit:.2f}M")

st.markdown("---")
st.caption("📊 Dashboard dibuat dengan Streamlit")