"""
Voter Duplicate Detection System - Streamlit Web Application
Upload voter database and detect duplicates using AI/ML techniques
"""

import streamlit as st
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict

# Page configuration
st.set_page_config(
    page_title="Voter Duplicate Detection System",
    page_icon="🗳️",
    layout="wide"
)

# Title and description
st.title("🗳️ Voter Duplicate Detection System")
st.markdown("**AI-Powered Electoral Integrity Tool** - Identify potential duplicate voter registrations")

# Sidebar for configuration
st.sidebar.header("⚙️ Detection Settings")

similarity_threshold = st.sidebar.slider(
    "Name Similarity Threshold (%)",
    min_value=50,
    max_value=100,
    value=85,
    help="Higher values = stricter matching"
)

dob_tolerance = st.sidebar.slider(
    "Date of Birth Tolerance (days)",
    min_value=0,
    max_value=365,
    value=30,
    help="Allow DOB differences within this range"
)

check_address = st.sidebar.checkbox("Include Address Matching", value=True)
address_threshold = st.sidebar.slider(
    "Address Similarity Threshold (%)",
    min_value=50,
    max_value=100,
    value=70,
    disabled=not check_address
)


def calculate_name_similarity(name1, name2):
    """Calculate similarity between two names using multiple methods"""
    if pd.isna(name1) or pd.isna(name2):
        return 0

    name1 = str(name1).strip().upper()
    name2 = str(name2).strip().upper()

    # Multiple similarity metrics
    ratio = fuzz.ratio(name1, name2)
    partial_ratio = fuzz.partial_ratio(name1, name2)
    token_sort = fuzz.token_sort_ratio(name1, name2)
    token_set = fuzz.token_set_ratio(name1, name2)

    # Weighted average
    similarity = (ratio * 0.3 + partial_ratio * 0.2 + token_sort * 0.25 + token_set * 0.25)
    return similarity


def calculate_address_similarity(addr1, addr2):
    """Calculate address similarity"""
    if pd.isna(addr1) or pd.isna(addr2):
        return 0

    addr1 = str(addr1).strip().upper()
    addr2 = str(addr2).strip().upper()

    return fuzz.token_set_ratio(addr1, addr2)


def calculate_dob_difference(dob1, dob2):
    """Calculate difference between two dates in days"""
    try:
        if pd.isna(dob1) or pd.isna(dob2):
            return 999999

        date1 = pd.to_datetime(dob1)
        date2 = pd.to_datetime(dob2)

        return abs((date1 - date2).days)
    except:
        return 999999


def detect_duplicates(df, name_threshold, dob_tolerance_days, check_addr, addr_threshold):
    """Main duplicate detection algorithm"""

    duplicates = []
    n = len(df)

    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Compare each record with every other record (brute force for small datasets)
    # For large datasets, you'd use blocking strategies

    compared = set()

    for i in range(n):
        status_text.text(f"Processing record {i + 1}/{n}...")
        progress_bar.progress((i + 1) / n)

        for j in range(i + 1, n):
            # Skip if already compared
            pair = tuple(sorted([i, j]))
            if pair in compared:
                continue
            compared.add(pair)

            record1 = df.iloc[i]
            record2 = df.iloc[j]

            # Calculate name similarity
            name_sim = calculate_name_similarity(record1['Full_Name'], record2['Full_Name'])

            # Check if names are similar enough
            if name_sim < name_threshold:
                continue

            # Calculate DOB difference
            dob_diff = calculate_dob_difference(record1['Date_of_Birth'], record2['Date_of_Birth'])

            # Calculate address similarity if enabled
            addr_sim = 0
            if check_addr:
                addr_sim = calculate_address_similarity(record1['Address'], record2['Address'])

            # Determine if it's a duplicate based on criteria
            is_duplicate = False
            confidence = 0
            reasons = []

            # Exact or very high name match
            if name_sim >= 95:
                is_duplicate = True
                confidence = name_sim
                reasons.append(f"High name similarity ({name_sim:.1f}%)")

            # High name similarity + same/similar DOB
            elif name_sim >= name_threshold and dob_diff <= dob_tolerance_days:
                is_duplicate = True
                confidence = (name_sim + (100 - dob_diff / 365 * 100)) / 2
                reasons.append(f"Name similarity ({name_sim:.1f}%)")
                reasons.append(f"DOB difference ({dob_diff} days)")

            # High name similarity + same address
            elif name_sim >= name_threshold and check_addr and addr_sim >= addr_threshold:
                is_duplicate = True
                confidence = (name_sim + addr_sim) / 2
                reasons.append(f"Name similarity ({name_sim:.1f}%)")
                reasons.append(f"Address similarity ({addr_sim:.1f}%)")

            if is_duplicate:
                duplicates.append({
                    'Record_1_Index': i,
                    'Record_2_Index': j,
                    'Voter_ID_1': record1['Voter_ID'],
                    'Voter_ID_2': record2['Voter_ID'],
                    'Name_1': record1['Full_Name'],
                    'Name_2': record2['Full_Name'],
                    'DOB_1': record1['Date_of_Birth'],
                    'DOB_2': record2['Date_of_Birth'],
                    'Address_1': record1['Address'],
                    'Address_2': record2['Address'],
                    'Name_Similarity': name_sim,
                    'DOB_Difference_Days': dob_diff,
                    'Address_Similarity': addr_sim,
                    'Confidence_Score': confidence,
                    'Detection_Reasons': ' | '.join(reasons)
                })

    progress_bar.empty()
    status_text.empty()

    return pd.DataFrame(duplicates)


# File upload section
st.header("📤 Upload Voter Database")

uploaded_file = st.file_uploader(
    "Choose a CSV file containing voter data",
    type=['csv'],
    help="CSV should contain: Voter_ID, Full_Name, Date_of_Birth, Address, etc."
)

if uploaded_file is not None:
    # Load the data
    df = pd.read_csv(uploaded_file)

    st.success(f"✅ Loaded {len(df)} voter records")

    # Show sample data
    with st.expander("📋 View Sample Data"):
        st.dataframe(df.head(10))

    # Detect duplicates button
    if st.button("🔍 Detect Duplicates", type="primary"):
        st.header("🔎 Duplicate Detection Results")

        with st.spinner("Analyzing voter records for duplicates..."):
            duplicates_df = detect_duplicates(
                df,
                similarity_threshold,
                dob_tolerance,
                check_address,
                address_threshold
            )

        if len(duplicates_df) > 0:
            # Statistics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Records", len(df))
            with col2:
                # Count unique voters involved in duplicates
                unique_duplicates = len(
                    set(duplicates_df['Voter_ID_1'].tolist() + duplicates_df['Voter_ID_2'].tolist()))
                st.metric("Potential Duplicates", unique_duplicates)
            with col3:
                duplicate_percentage = (unique_duplicates / len(df)) * 100
                st.metric("Duplicate %", f"{duplicate_percentage:.2f}%")
            with col4:
                avg_confidence = duplicates_df['Confidence_Score'].mean()
                st.metric("Avg Confidence", f"{avg_confidence:.1f}%")

            # Confidence distribution chart
            st.subheader("📊 Confidence Score Distribution")
            fig = px.histogram(
                duplicates_df,
                x='Confidence_Score',
                nbins=20,
                title="Distribution of Duplicate Detection Confidence Scores",
                labels={'Confidence_Score': 'Confidence Score (%)', 'count': 'Number of Duplicate Pairs'}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Detailed results
            st.subheader("📝 Detailed Duplicate Pairs")

            # Add filters
            col1, col2 = st.columns(2)
            with col1:
                min_confidence = st.slider("Minimum Confidence Score", 0, 100, 70)
            with col2:
                sort_by = st.selectbox("Sort by", ["Confidence_Score", "Name_Similarity", "DOB_Difference_Days"])

            # Filter and sort
            filtered_df = duplicates_df[duplicates_df['Confidence_Score'] >= min_confidence].sort_values(
                by=sort_by,
                ascending=False if sort_by != "DOB_Difference_Days" else True
            )

            st.info(f"Showing {len(filtered_df)} duplicate pairs with confidence ≥ {min_confidence}%")

            # Display results in expandable cards
            for idx, row in filtered_df.iterrows():
                with st.expander(
                        f"🔴 Duplicate Pair #{idx + 1} - Confidence: {row['Confidence_Score']:.1f}%"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**👤 Record 1**")
                        st.write(f"**Voter ID:** {row['Voter_ID_1']}")
                        st.write(f"**Name:** {row['Name_1']}")
                        st.write(f"**DOB:** {row['DOB_1']}")
                        st.write(f"**Address:** {row['Address_1']}")

                    with col2:
                        st.markdown("**👤 Record 2**")
                        st.write(f"**Voter ID:** {row['Voter_ID_2']}")
                        st.write(f"**Name:** {row['Name_2']}")
                        st.write(f"**DOB:** {row['DOB_2']}")
                        st.write(f"**Address:** {row['Address_2']}")

                    st.markdown("---")
                    st.markdown("**📊 Similarity Metrics:**")

                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    with metric_col1:
                        st.metric("Name Similarity", f"{row['Name_Similarity']:.1f}%")
                    with metric_col2:
                        st.metric("DOB Difference", f"{row['DOB_Difference_Days']} days")
                    with metric_col3:
                        st.metric("Address Similarity", f"{row['Address_Similarity']:.1f}%")

                    st.info(f"**Detection Reasons:** {row['Detection_Reasons']}")

            # Download results
            st.subheader("💾 Export Results")
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Duplicate Report (CSV)",
                data=csv,
                file_name=f"duplicate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        else:
            st.success("🎉 No duplicates detected with the current settings!")
            st.info("Try adjusting the similarity thresholds in the sidebar to find more potential matches.")

else:
    # Instructions when no file is uploaded
    st.info("👆 Please upload a voter database CSV file to begin duplicate detection.")

    st.markdown("### 📋 Expected CSV Format:")
    st.markdown("""
    Your CSV file should contain the following columns:
    - `Voter_ID` - Unique voter identification number
    - `Full_Name` - Complete name of the voter
    - `Date_of_Birth` - Date of birth (YYYY-MM-DD format)
    - `Address` - Residential address
    - `Father_Mother_Name` (optional)
    - `Gender` (optional)
    - `City`, `State`, `PIN_Code` (optional)
    """)

    st.markdown("### 🎯 How It Works:")
    st.markdown("""
    1. **Upload** your voter database CSV file
    2. **Configure** detection settings in the sidebar
    3. **Click** 'Detect Duplicates' button
    4. **Review** the results with confidence scores
    5. **Download** the detailed report

    The system uses advanced fuzzy matching algorithms to detect:
    - Exact duplicates
    - Names with typos
    - Phonetically similar names
    - Records with missing/extra characters
    - Case variations and spacing issues
    """)

    # Sample data download
    st.markdown("### 📥 Don't have test data?")
    if st.button("Generate Sample Dataset"):
        st.info("Run the data generator script first to create 'voter_database.csv'")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🗳️ Voter Duplicate Detection System | Built for Electoral Integrity</p>
        <p style='font-size: 12px; color: #666;'>Capstone Project 2024</p>
    </div>
    """,
    unsafe_allow_html=True
)