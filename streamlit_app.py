import streamlit as st
import pandas as pd
import plotly.express as px

# Load Excel file
file_path = r"D:\packing + palletizer area/palletizer downtime.xlsx"
df = pd.read_excel(file_path, sheet_name="Cleaned Downtime")

# Clean text columns
df = df.applymap(lambda x: ' '.join(x.strip().split()) if isinstance(x, str) else x)
df = df[~((df["reason"] == "no slings") | (df["reason"] == "reason"))]

# Date processing
df["Date"] = pd.to_datetime(df["Date"])
df["year"] = df["Date"].dt.year.astype("object")
df["month"] = df["Date"].dt.month_name()
df["day"] = df['Date'].dt.day_name()
df['week_number'] = df['Date'].dt.isocalendar().week
df['day_number'] = df['Date'].dt.dayofyear.astype("category")
df = df.dropna()

# Sidebar slicer
st.sidebar.header("Filter")
selected_categories = st.sidebar.multiselect(
    "Select Reason Categories",
    options=df["reason category"].unique(),
    default=df["reason category"].unique()
)

# Filter DataFrame
filtered_df = df[df["reason category"].isin(selected_categories)]

# Chart 1: Reason Category Frequency
counts = filtered_df["reason category"].value_counts(normalize=True).sort_values()
data = counts.reset_index()
data.columns = ['reason category', 'percentage']
fig1 = px.pie(
    data,
    names='reason category',
    values='percentage',
    title='Reason Category Frequency Distribution',
)
fig1.update_traces(textinfo='percent+label')
st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Reason Category by Hours
data2 = filtered_df.groupby('reason category')['Duration in Hrs'].sum().sort_values().reset_index()
fig2 = px.pie(
    data2,
    names='reason category',
    values='Duration in Hrs',
    title='Reason Category Hours Distribution',
)
fig2.update_traces(textinfo='percent+label')
st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Top Reasons by Total Duration
data3 = filtered_df.groupby('reason')['Duration in Hrs'].sum().sort_values().tail(15).reset_index()
fig3 = px.bar(
    data3,
    x='Duration in Hrs',
    y='reason',
    orientation='h',
    title='Top 15 Reasons by Total Duration (Hrs)',
    text='Duration in Hrs'
)
fig3.update_traces(texttemplate='%{text:.1f}', textposition='inside')
fig3.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Blockages per Day for Palletizer belt blockage
reason = "Palletizer belt blockage"
df_filtered = filtered_df[filtered_df["reason"] == reason]
daily_counts = df_filtered.groupby('Date').size().reset_index(name='blockages_per_day')
fig4 = px.line(
    daily_counts,
    x='Date',
    y='blockages_per_day',
    title='Palletizer Belt Blockage - Daily Count'
)
st.plotly_chart(fig4, use_container_width=True)

# Chart 5: Blockages per Week
weekly_counts = df_filtered.groupby(['year', 'week_number']).size().reset_index(name='blockages_per_week')
weekly_counts['year_week'] = weekly_counts['year'].astype(str) + '-W' + weekly_counts['week_number'].astype(str)
fig5 = px.line(
    weekly_counts,
    x='year_week',
    y='blockages_per_week',
    title='Palletizer Belt Blockage - Weekly Count'
)
st.plotly_chart(fig5, use_container_width=True)
