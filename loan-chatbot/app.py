import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="LoanGPT",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/style.css")

# Initialize Gemini
genai.configure(api_key=st.secrets["AIzaSyCooDxXGRdFMuTYdomwUTvI-7aUd0FBfFw"])
model = genai.GenerativeModel('gemini-2.5-flash')  # Changed to supported model

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("loan_data.csv")

df = load_data()

# UI Components
st.sidebar.image("assets/logo.png", width=200)
st.sidebar.markdown("""
<div class="sidebar-header">
    <h2>Loan Approval Assistant</h2>
    <p>Developed by Jeki Panchal</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="sidebar-section">
    <h3>📊 Dataset Overview</h3>
    <p>Total Applications: {}</p>
    <p>Approval Rate: {:.1f}%</p>
</div>
""".format(
    len(df),
    (df['Loan_Status'].value_counts()['Y']/len(df))*100
), unsafe_allow_html=True)

# Chat container
st.title("💬 LoanGPT Assistant")
st.caption("Ask me anything about loan applications in our database")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about loan approvals..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Find relevant data - FIXED THIS SECTION
    relevant_data = df[
        df.apply(lambda row: any(word.lower() in str(row).lower() 
                for word in prompt.lower().split()), :
    ].head(3)
    
    # Generate response
    if not relevant_data.empty:
        context = relevant_data.to_string()
        full_prompt = f"""
        You're a loan officer assistant. Answer the user's question professionally using ONLY this data:
        
        {context}
        
        Question: {prompt}
        
        Rules:
        1. Be specific with numbers when available
        2. If loan status isn't mentioned, say you don't know
        3. Format numbers with commas (₹1,00,000)
        4. Keep answers concise (2-3 sentences max)
        """
        
        with st.spinner("Analyzing loan data..."):
            try:
                response = model.generate_content(full_prompt)
                answer = response.text
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                answer = "I'm having trouble processing that request. Please try again."
    else:
        answer = "I couldn't find relevant loan records. Try asking differently."
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(answer)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": answer})
