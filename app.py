
import streamlit as st
import requests
import pandas as pd

# Choose an LLM for text generation
API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"  # Or your chosen model
headers = {"Authorization": "Bearer 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"}  # Replace with your Hugging Face API token

# Custom CSS for styling
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f4f4f4;
        margin: 0;
        padding: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }
    .container {
        background-color: #fff;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 30px;
        width: 80%;
        max-width: 800px;
    }
    h1 {
        color: #333;
        text-align: center;
        margin-bottom: 20px;
    }
    p {
        color: #666;
        text-align: center;
        margin-bottom: 20px;
    }
    .stTextInput textarea {
        width: 100%;
        padding: 15px;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 16px;
        margin-bottom: 15px;
        resize: vertical; /* Allow vertical resizing */
        min-height: 150px; /* Initial height of the text area */
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        padding: 15px 25px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 18px;
        display: block; /* Make it a block element */
        margin: 0 auto; /* Center the button */
    }
    .stButton button:hover {
        background-color: #3e8e41;
    }
    .stText {
        margin-top: 20px;
        padding: 15px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: #f9f9f9;
        color: #333;
        font-size: 16px;
        white-space: pre-wrap; /* Preserve line breaks and spaces */
    }
    .stAlert {
        margin-top: 20px;
        padding: 15px;
        border-radius: 4px;
        font-size: 16px;
    }
    .stAlert.st-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .stAlert.st-warning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit UI
st.title("AI Text Generator with CSV Input")
st.write("Enter a prompt, optionally upload a CSV, and the AI will generate a response.")

# File upload
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully!")
        st.write("Preview of the data:")
        st.dataframe(df.head())  # Display a preview of the data
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        df = None  # Reset df if there's an error
else:
    df = None

with st.container():
    text_input = st.text_area("Enter your prompt:", "")

    if st.button("Generate"):
        if text_input:
            with st.spinner("Generating..."):
                # Incorporate CSV data if available
                if uploaded_file is not None and df is not None:
                    csv_context = "Here's the relevant data from the CSV file:\n" + df.to_string() + "\n\n"
                    prompt_with_csv = csv_context + "Based on the CSV data, answer this question or fulfill this request: " + text_input
                    payload = {"inputs": prompt_with_csv, "parameters": {"max_new_tokens": 1000}}
                else:
                    # No CSV - use the basic prompt
                    payload = {"inputs": text_input, "parameters": {"max_new_tokens": 1000}}

                try:
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
                    response.raise_for_status()
                    json_response = response.json()
                    generated_text = json_response[0]["generated_text"]
                    st.markdown(f'<div class="stText">{generated_text}</div>', unsafe_allow_html=True)
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")
                except (KeyError, IndexError, TypeError) as e:
                    st.error(f"Error processing the response: {e}. Check the API response format.")
        else:
            st.warning("Please enter a prompt.")