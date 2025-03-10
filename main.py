import streamlit as st 
import pandas as pd 
import os
from io import BytesIO
import openpyxl 

#setting up the app
st.set_page_config(page_title="📊 Data Sweeper", layout="wide")
st.title("📊 Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel)", type=["csv","xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)

        elif file_ext == ".xlsx":
            df = pd.read_excel(file)

        else:
            st.error(f"Unsupported file type:{file_ext}")
            continue

        #info of file
        st.write(f"**File Name:** {file.name}")
        st.write(f"** File Size:** {file.size/1024}")

        #display 5 rows of the selected file
        st.write("Preview the Head of the Dataframe")
        st.dataframe(df.head())

        #Data cleaning options
        st.subheader("🧹 Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"🗑️ Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")

            with col2:
                if st.button(f"🔢 Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values have been Filled!")

        
        #Choose specific columns to keep or convert
        st.subheader("📋 Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        #Creating Visualizations
        st.subheader("📈 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            # Get numeric columns
            numeric_cols = df.select_dtypes(include=["number"]).columns
            
            if len(numeric_cols) > 0:
                # Create a selectbox for choosing visualization type
                viz_type = st.selectbox(
                    "Choose visualization type",
                    ["Bar Chart", "Line Chart", "Scatter Plot"],
                    key=f"viz_type_{file.name}"
                )
                
                # Create a selectbox for choosing columns to visualize
                selected_cols = st.multiselect(
                    "Select columns to visualize",
                    numeric_cols,
                    default=numeric_cols[:2] if len(numeric_cols) >= 2 else numeric_cols,
                    key=f"cols_{file.name}"
                )
                
                if selected_cols:
                    if viz_type == "Bar Chart":
                        st.bar_chart(df[selected_cols])
                    elif viz_type == "Line Chart":
                        st.line_chart(df[selected_cols])
                    elif viz_type == "Scatter Plot":
                        if len(selected_cols) >= 2:
                            st.scatter_chart(df[selected_cols[:2]])
                        else:
                            st.warning("Please select at least 2 columns for scatter plot")
            else:
                st.warning("No numeric columns found in the dataset for visualization")
                
            # Show basic statistics
            st.subheader("📊 Basic Statistics")
            st.write(df.describe())

        #Convert the file -> CSV to Excel
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:",["CSV","Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type =="CSV":
                df.to_csv(buffer,index=False)
                file_name = file.name.replace(file_ext,".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext,".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            #Download Button
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("✨ All Files Processed!")

            
