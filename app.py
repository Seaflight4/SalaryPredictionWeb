import streamlit as st
from predict_page import show_predict_page
from explore_page import show_explore_page
from explore_page import shorten_categories
from explore_page import clean_experience
from explore_page import clean_education
import os
import requests
import zipfile
from pathlib import Path
import pandas as pd

ZIP_URL = "https://survey.stackoverflow.co/datasets/stack-overflow-developer-survey-2024.zip"
EXTRACT_DIR = "data"
CSV_FILENAME = "survey_results_public.csv"
CSV_PATH = os.path.join(EXTRACT_DIR, CSV_FILENAME)

@st.cache_data  # Cache the downloaded data to avoid re-downloading on every rerun
def download_and_extract_zip():
    """Download the ZIP file and extract its contents."""
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    
    # Download the ZIP
    zip_path = os.path.join(EXTRACT_DIR, "survey.zip")
    if not os.path.exists(zip_path):
        with st.spinner("Downloading Stack Overflow survey data (this may take a minute)..."):
            response = requests.get(ZIP_URL, stream=True)
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
    
    # Extract the CSV
    if not os.path.exists(CSV_PATH):
        with st.spinner("Extracting CSV file..."):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(EXTRACT_DIR)
    
    return CSV_PATH

@st.cache_data
def load_data():
    csv_path = download_and_extract_zip()
    df = pd.read_csv(csv_path)
    df = df[["Country", "EdLevel", "YearsCodePro", "Employment", "ConvertedCompYearly"]]
    df = df.rename({"ConvertedCompYearly": "Salary"}, axis = 1)
    df = df[df["Salary"].notnull()]
    df = df.dropna()
    df = df[df["Employment"] == "Employed, full-time"]
    df = df.drop("Employment", axis=1)

    country_map = shorten_categories(df.Country.value_counts(), 400)
    df['Country'] = df['Country'].map(country_map)
    df = df[df["Salary"] <= 250000]
    df = df[df["Salary"] >= 10000]
    df = df[df["Country"] != 'Other']

    df['YearsCodePro'] = df['YearsCodePro'].apply(clean_experience)
    df['EdLevel'] = df['EdLevel'].apply(clean_education)
    return df

df = load_data()

page = st.sidebar.selectbox("Explore Or Predict", ("Predict", "Explore"))
if page == "Predict":
    show_predict_page()
else:
    show_explore_page(df)

