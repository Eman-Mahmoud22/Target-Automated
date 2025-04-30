#!/usr/bin/env python
# coding: utf-8

# In[4]:


import streamlit as st
import pandas as pd

# App config with wide layout (dark theme handled via config.toml or browser settings)
st.set_page_config(page_title="Target Comparison Tool", layout="wide")

# Custom CSS for centering and dark theme tweaks
st.markdown("""
    <style>
        .main {
            background-color: #1e1e1e;
            color: white;
        }
        h1, h2, h3, h4 {
            text-align: center;
            color: white;
        }
        .block-container {
            margin: auto;
            max-width: 1000px;
        }
        .stDataFrame {
            background-color: #262730;
        }
        .css-1v0mbdj {
            background-color: #1e1e1e;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 Historical Data vs Test New Target Tool")

# Step 1: Upload historical data
st.header("📁 Step 1: Upload Historical Data")
historical_file = st.file_uploader("Upload 'digitallll_datatttta.xlsx'", type=["xlsx"])

if historical_file:
    data = pd.read_excel(historical_file)
    data.fillna(0, inplace=True)
    data.columns = data.columns.str.strip()

    numeric_cols = data.select_dtypes(include=['number']).columns
    monthly_avg = data.groupby(['MonthFullName', 'Lead_source', 'Spec_Name'])[numeric_cols].mean().reset_index()

    grouped = data.groupby(['Lead_source', 'Spec_Name'])
    agg_data = grouped[numeric_cols].agg(['mean', 'max'])

    for col in numeric_cols:
        agg_data[(col, 'lower_bound')] = grouped[col].quantile(0.10)
        agg_data[(col, 'upper_bound')] = grouped[col].quantile(0.90)

    new_columns = []
    for col in numeric_cols:
        new_columns.extend([(col, 'mean'), (col, 'max'), (col, 'lower_bound'), (col, 'upper_bound')])

    agg_data = agg_data[new_columns]
    agg_data.columns = ['_'.join(col).strip() for col in agg_data.columns]
    agg_data.reset_index(inplace=True)
    agg_data.columns = agg_data.columns.str.strip()

    # Show processed tables
    st.subheader("📊 Monthly Averages")
    st.dataframe(monthly_avg)

    st.subheader("📈 Aggregated Data (Historical Bounds)")
    st.dataframe(agg_data)

    # Step 2: Upload new test data
    st.header("📁 Step 2: Upload New Target Data for Comparison")
    test_file = st.file_uploader("Upload 'newTarget.xlsx'", type=["xlsx"])

    if test_file:
        df = pd.read_excel(test_file)
        df.fillna(0, inplace=True)

        comparison_results = []

        for index, new_row in df.iterrows():
            lead_source = new_row['Lead_source']
            spec_name = new_row['Spec_Name']
            
            old_row = agg_data[
                (agg_data['Lead_source'] == lead_source) &
                (agg_data['Spec_Name'] == spec_name)
            ]
            if old_row.empty:
                continue

            result = {
                'Lead_source': lead_source,
                'Spec_Name': spec_name
            }

            for col in df.columns:
                if col not in ['Lead_source', 'Spec_Name']:
                    try:
                        lower_bound = old_row[f"{col}_lower_bound"].values[0]
                        upper_bound = old_row[f"{col}_upper_bound"].values[0]
                        new_value = new_row[col]

                        if new_value < lower_bound:
                            status = "Below Range"
                        elif new_value > upper_bound:
                            status = "Above Range"
                        else:
                            status = "Within Range"

                        result[col] = new_value
                        result[f"{col}_status"] = status
                    except KeyError:
                        result[col] = new_row[col]
                        result[f"{col}_status"] = "No Historical Data"
            
            comparison_results.append(result)

        final_df = pd.DataFrame(comparison_results)

        st.subheader("✅ Final Comparison Results")
        st.dataframe(final_df)


# In[ ]:




