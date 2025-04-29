#!/usr/bin/env python
# coding: utf-8

# In[4]:


import streamlit as st
import pandas as pd

# Title
st.title("📊 Historical Summary & Test Data Comparison")

# Upload Historical Data
uploaded_file = st.file_uploader("Upload Historical Data (Excel)", type=["xlsx"])

# Upload Test Data
uploaded_test_file = st.file_uploader("Upload Test Data (Excel)", type=["xlsx"])

if uploaded_file and uploaded_test_file:
    # Load and clean historical data
    data = pd.read_excel(uploaded_file)
    data.columns = data.columns.str.strip()
    data.fillna(0, inplace=True)

    # Show descriptive statistics for historical data
    st.subheader("📌 Descriptive Statistics for Historical Data")
    st.dataframe(data.describe())

    # Preprocess historical data for comparison
    data['MonthFullName'] = pd.to_datetime(data['MonthFullName'])
    numeric_cols = data.select_dtypes(include=['number']).columns
    monthly_avg = data.groupby(['MonthFullName', 'Lead_source', 'Spec_Name'])[numeric_cols].mean().reset_index()
    agg_data = monthly_avg.groupby(['Lead_source', 'Spec_Name'])[numeric_cols].agg(['mean'])

    # Add ±10% bounds
    for col in numeric_cols:
        agg_data[(col, 'lower_bound')] = agg_data[(col, 'mean')] * 0.9
        agg_data[(col, 'upper_bound')] = agg_data[(col, 'mean')] * 1.1

    # Flatten columns
    bounds_cols = []
    for col in numeric_cols:
        bounds_cols.extend([(col, 'lower_bound'), (col, 'upper_bound')])
    agg_data = agg_data[bounds_cols]
    agg_data.columns = ['_'.join(col).strip() for col in agg_data.columns]
    agg_data.reset_index(inplace=True)

    # Load and clean test data
    test_data = pd.read_excel(uploaded_test_file)
    test_data.columns = test_data.columns.str.strip()

    # Compare test data against bounds
    comparison_results = []
    for _, test_row in test_data.iterrows():
        lead_source = test_row['Lead_source']
        spec_name = test_row['Spec_Name']
        historical_row = agg_data[(agg_data['Lead_source'] == lead_source) & (agg_data['Spec_Name'] == spec_name)]

        if historical_row.empty:
            continue

        result = {'Lead_source': lead_source, 'Spec_Name': spec_name}
        for col in test_data.columns:
            if col not in ['Lead_source', 'Spec_Name']:
                lb_col = f"{col}_lower_bound"
                ub_col = f"{col}_upper_bound"
                if lb_col in historical_row and ub_col in historical_row:
                    lb = historical_row[lb_col].values[0]
                    ub = historical_row[ub_col].values[0]
                    value = test_row[col]

                    if value < lb:
                        status = "Below Range"
                    elif value > ub:
                        status = "Above Range"
                    else:
                        status = "Within Range"

                    result[col] = value
                    result[f"{col}_status"] = status
        comparison_results.append(result)

    # Show final comparison results
    st.subheader("📉 Comparison Results (Test Data vs Historical Bounds)")
    final_df = pd.DataFrame(comparison_results)
    st.dataframe(final_df)


# In[ ]:




