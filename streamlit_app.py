import streamlit as st
import pandas as pd
import plotly.express as px

# Load Excel file
file_path = "palletizer downtime.xlsx"
df = pd.read_excel(file_path, sheet_name="Cleaned Downtime")

# Clean text columns
df = df.applymap(lambda x: ' '.join(x.strip().split()) if isinstance(x, str) else x)
df = df[~((df["reason"] == "reason") | (df["reason"] == "Palletizer adjust Palletizer"))]
df['reason'] = df['reason'].str.replace('iftar', 'break', case=False, regex=True)

# Date processing
df["Date"] = pd.to_datetime(df["Date"])
df["year"] = df["Date"].dt.year.astype("object")
df["month"] = df["Date"].dt.month_name()
df["day"] = df["Date"].dt.day_name()
df["week_number"] = df["Date"].dt.isocalendar().week
df["day_number"] = df["Date"].dt.dayofyear.astype("category")
df = df.dropna()

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("Filters")

# Date range slicer (timeline filter)
min_date = df["Date"].min()
max_date = df["Date"].max()
selected_date_range = st.sidebar.date_input(
    "Select Date Range:",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply date filter
if len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

# Multiselect for reason categories
selected_categories = st.sidebar.multiselect(
    "Select Reason Categories:",
    options=df["reason category"].unique(),
    default=df["reason category"].unique()
)

# Filter by selected reason categories
filtered_df = df[df["reason category"].isin(selected_categories)]

# Dropdown for specific reason
unique_reasons = filtered_df["reason"].unique()
selected_reason = st.sidebar.selectbox("Select Specific Reason:", unique_reasons)

# -------------------- CHART 1 --------------------
counts = filtered_df["reason category"].value_counts(normalize=True).sort_values()
data1 = counts.reset_index()
data1.columns = ['reason category', 'percentage']
fig1 = px.pie(
    data1,
    names='reason category',
    values='percentage',
    title='Reason Category Frequency Distribution'
)
fig1.update_traces(textinfo='percent+label')
st.plotly_chart(fig1, use_container_width=True)

# -------------------- CHART 2 --------------------
data2 = filtered_df.groupby('reason category')['Duration in Hrs'].sum().sort_values().reset_index()
fig2 = px.pie(
    data2,
    names='reason category',
    values='Duration in Hrs',
    title='Reason Category Hours Distribution'
)
fig2.update_traces(textinfo='percent+label')
st.plotly_chart(fig2, use_container_width=True)

# -------------------- CHART 3 --------------------
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
fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig3, use_container_width=True)

# -------------------- CHART 4: Daily Count with 0s --------------------
df_reason_filtered = filtered_df[filtered_df["reason"] == selected_reason]

# Create a complete daily date range from filtered data
date_range = pd.date_range(start=filtered_df['Date'].min(), end=filtered_df['Date'].max())
daily_counts = df_reason_filtered.groupby('Date').size().reindex(date_range, fill_value=0).reset_index()
daily_counts.columns = ['Date', 'blockages_per_day']

fig4 = px.line(
    daily_counts,
    x='Date',
    y='blockages_per_day',
    title=f'{selected_reason} - Daily Count'
)
st.plotly_chart(fig4, use_container_width=True)
# -------------------- CHART 5: Weekly Count with 0s --------------------
# Create a DataFrame with full weekly periods in the selected range
filtered_df['week_start'] = filtered_df['Date'] - pd.to_timedelta(filtered_df['Date'].dt.dayofweek, unit='d')
all_weeks = pd.date_range(start=filtered_df['week_start'].min(), end=filtered_df['week_start'].max(), freq='W-MON')

# Group and reindex weekly counts
df_reason_filtered['week_start'] = df_reason_filtered['Date'] - pd.to_timedelta(df_reason_filtered['Date'].dt.dayofweek, unit='d')
weekly_counts = df_reason_filtered.groupby('week_start').size().reindex(all_weeks, fill_value=0).reset_index()
weekly_counts.columns = ['week_start', 'blockages_per_week']
weekly_counts['year_week'] = weekly_counts['week_start'].dt.strftime('%Y-W%U')

fig5 = px.line(
    weekly_counts,
    x='year_week',
    y='blockages_per_week',
    title=f'{selected_reason} - Weekly Count'
)
st.plotly_chart(fig5, use_container_width=True)


# -------------------- CHART 6: TIMELINE (All Events) --------------------
timeline_df = filtered_df.copy()
timeline_df["Start"] = timeline_df["Date"]
timeline_df["End"] = timeline_df["Date"] + pd.to_timedelta(timeline_df["Duration in Hrs"], unit="h")

# Plot all events without limiting
fig6 = px.timeline(
    timeline_df,
    x_start="Start",
    x_end="End",
    y="reason",
    color="reason category",
    title="Timeline of All Blockage Events",
    hover_data=["Duration in Hrs", "reason category"]
)
fig6.update_yaxes(autorange="reversed")
st.plotly_chart(fig6, use_container_width=True)



