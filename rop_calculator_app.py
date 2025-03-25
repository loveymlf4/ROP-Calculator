import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import datetime

# Title
st.title("📦 Reorder Point (ROP) Calculator")

# Session state to control run
if "run_triggered" not in st.session_state:
    st.session_state.run_triggered = False

# Upload Excel File
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# Sidebar config (always visible)
st.sidebar.header("🔧 Configuration")
lead_time_days = st.sidebar.number_input("Lead Time (Days)", min_value=1, value=5)
working_days = st.sidebar.number_input("Working Days per Week", min_value=1, max_value=7, value=5)
bootstrap_samples = st.sidebar.number_input("Bootstrap Samples", min_value=1000, max_value=10000, step=1000, value=2000)

st.sidebar.subheader("📊 Service Levels by ABC")
service_levels = {
    'A': st.sidebar.slider("A Items", 0.70, 0.99, 0.95),
    'B': st.sidebar.slider("B Items", 0.70, 0.99, 0.85),
    'C': st.sidebar.slider("C Items", 0.70, 0.99, 0.75)
}

# Run button (only shows if file is uploaded)
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ File loaded successfully!")

    required_cols = ['calendar_date', 'item_number', 'quantity']
    if not all(col in df.columns for col in required_cols):
        st.error(f"File must contain columns: {required_cols}")
    else:
        df['calendar_date'] = pd.to_datetime(df['calendar_date'])
        if 'branch_number' not in df.columns:
            df['branch_number'] = 'BRANCH'

        # Show Run button
        if st.button("▶️ Run ROP Calculation"):
            st.session_state.run_triggered = True

# Only run calculation after button is pressed
if st.session_state.run_triggered:

    lead_time_weeks = lead_time_days / working_days
    total_months = df['calendar_date'].dt.to_period('M').nunique()

    transaction_counts = df.groupby('item_number')['calendar_date'].count().reset_index(name='transaction_count')
    item_metrics = df.groupby('item_number').agg(
        total_qty=('quantity', 'sum'),
        avg_monthly_qty=('quantity', lambda x: x.sum() / total_months)
    ).reset_index()

    item_metrics = item_metrics.merge(transaction_counts, on='item_number')

    weekly_demand_item = df.set_index('calendar_date').groupby('item_number').resample('W-MON')['quantity'].sum().reset_index()
    weeks_no_demand = weekly_demand_item.groupby('item_number').agg(
        weeks_without_demand=('quantity', lambda x: (x == 0).sum())
    ).reset_index()

    item_metrics = item_metrics.merge(weeks_no_demand, on='item_number')

    meets_criteria = (
        (item_metrics['avg_monthly_qty'] >= 0.5) &
        (item_metrics['transaction_count'] >= 10)
    )
    item_metrics['Demand_Group'] = np.where(meets_criteria, 'Qualified', 'Human check needed')

    criteria_df = item_metrics[meets_criteria].nlargest(500, 'total_qty')

    criteria_df = criteria_df.sort_values(by='total_qty', ascending=False)
    criteria_df['cum_qty'] = criteria_df['total_qty'].cumsum()
    total_qty_sum = criteria_df['total_qty'].sum()

    conditions = [
        criteria_df['cum_qty'] <= 0.80 * total_qty_sum,
        criteria_df['cum_qty'] <= 0.95 * total_qty_sum
    ]
    choices = ['A', 'B']
    criteria_df['ABC_class'] = np.select(conditions, choices, default='C')

    def calculate_rop(demand_data, lead_time_weeks, service_level, bootstrap_samples):
        lead_time_demands = []
        for _ in range(bootstrap_samples):
            sampled = np.random.choice(demand_data)
            lead_time_demands.append(sampled * lead_time_weeks)
        rop = np.percentile(lead_time_demands, service_level * 100)
        nonzero = [x for x in demand_data if x > 0]
        if nonzero:
            mode = pd.Series(nonzero).mode().iloc[0]
            if rop < 0.5 * mode:
                return np.ceil(mode * service_level)
        return np.ceil(rop)

    results = []

    for _, row in item_metrics.iterrows():
        item = row['item_number']
        demand_group = row['Demand_Group']
        total_qty = row['total_qty']
        transaction_count = row['transaction_count']

        if demand_group == 'Qualified':
            item_demand = df[df['item_number'] == item].set_index('calendar_date')\
                .resample('W-MON')['quantity'].sum().fillna(0).tolist()

            if item in criteria_df['item_number'].values:
                abc_class = criteria_df.loc[criteria_df['item_number'] == item, 'ABC_class'].values[0]
            else:
                abc_class = 'C'

            service_level = service_levels[abc_class]
            rop = int(calculate_rop(item_demand, lead_time_weeks, service_level, bootstrap_samples))
        else:
            abc_class = 'N/A'
            rop = None

        results.append({
            'item_number': item,
            'ABC_class': abc_class,
            'ROP': rop,
            'Demand_Group': demand_group,
            'Total_Qty': total_qty,
            'Transaction_Count': transaction_count
        })

    results_df = pd.DataFrame(results)

    st.subheader("📋 ROP Results")
    st.dataframe(results_df)

    # Export to Excel
    output = BytesIO()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"rop_results_{timestamp}.xlsx"

    qualified_df = results_df[results_df['Demand_Group'] == 'Qualified']
    human_check_df = results_df[results_df['Demand_Group'] == 'Human check needed']

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        qualified_df.to_excel(writer, index=False, sheet_name='ROP Results')
        human_check_df.to_excel(writer, index=False, sheet_name='Needs Review')
    output.seek(0)

    st.download_button(
        label="📥 Download Results (2 Sheets)",
        data=output,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
