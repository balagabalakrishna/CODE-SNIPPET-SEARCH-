import streamlit as st
import google.generativeai as genai

# Configure the Gemini API key securely
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Load a Gemini model
model = genai.GenerativeModel("models/gemini-1.5-flash")

def generate_code(prompt):
    response = model.generate_content(prompt)
    return response.text

