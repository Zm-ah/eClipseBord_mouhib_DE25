import streamlit as st 
import httpx 

BACKEND_URL = "http://127.0.0.1:8000"


st.title("eClipseBord") 
st.write("Solar & Lunar Eclipse Dashboard")
eclipse_type = st.selectbox("Choose eclipse type", ["lunar", "solar"]) 


response = httpx.get(f"{BACKEND_URL}/eclipses/{eclipse_type}")
data = response.json()
st.write(f"Antal rader: {len(data)}") 

response = httpx.get(f"{BACKEND_URL}/eclipses/{eclipse_type}")
data = response.json()