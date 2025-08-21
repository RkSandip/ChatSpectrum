import streamlit as st

st.set_page_config(page_title="ChatSpectrum", page_icon="💬")
st.title("Whatsapp Chat Analyzer")
st.write("App is loading successfully! ✅")

# Test basic imports
try:
    import pandas as pd
    st.write("Pandas imported successfully!")
except ImportError as e:
    st.error(f"Pandas import failed: {e}")
