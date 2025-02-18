import streamlit as st
import requests
import pandas as pd
import io

# API Details
API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
# Custom CSS
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
        resize: vertical;
        min-height: 150px;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        padding: 15px 25px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 18px;
        display: block;
        margin: 0 auto;
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
        white-space: pre-wrap;
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

# API Key Input and Validation

api_key = st.sidebar.text_input("Enter your Hugging Face API Key:", type="password") # Use sidebar for cleaner UI
headers = {} # Initialize headers
api_key_valid = False

if api_key:
    headers = {"Authorization": f"Bearer {api_key}"}
    # Validate the API key (basic check - a more robust check would query the API)
    try:
        # Attempt a simple API call to check the key
        response = requests.post(API_URL, headers=headers, json={"inputs": "test", "parameters": {"max_new_tokens": 1}})
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        if response.status_code == 200:
            st.sidebar.success("API Key is valid!")
            api_key_valid = True
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"API Key validation failed: {e}")
        api_key_valid = False
    except Exception as e:
        st.sidebar.error(f"An unexpected error occurred during API key validation: {e}")
        api_key_valid = False

# Streamlit UI (Conditional Rendering based on API Key Validation)
if api_key_valid:
    st.title("AI Text Generator with CSV Input & Price Extraction")
    st.write("Enter a prompt, optionally upload a CSV, and the AI will generate a response. Also extracts prices from the CSV.")

    # File upload
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("CSV file uploaded successfully!")
            st.write("Preview of the data:")
            st.dataframe(df.head())

            # Price Extraction and Display
            if 'price' in df.columns:
                price_values = df['price'].tolist()
                st.subheader("Extracted Prices:")
                for price in price_values:
                    st.write(price)
            else:
                st.warning("The 'price' column was not found in the CSV file.")


        except pd.errors.EmptyDataError:
            st.error("The CSV file is empty.")
        except pd.errors.ParserError:
            st.error("Error parsing CSV file.  Check the file format.")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            df = None
    else:
        df = None

    with st.container():
        text_input = st.text_area("Enter your prompt:", "")  # The text input

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
                        # Make the API call
                        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

                        # Raise HTTP errors
                        response.raise_for_status()

                        # If successful, parse the JSON response
                        json_response = response.json()
                        generated_text = json_response[0]["generated_text"]
                        st.markdown(f'<div class="stText">{generated_text}</div>', unsafe_allow_html=True)

                    except requests.exceptions.HTTPError as http_err:
                        st.error(f"HTTP error occurred: {http_err}")
                        st.error(f"Response status code: {response.status_code}")
                        try:
                            st.error(f"Response content: {response.json()}")
                        except:
                            st.error("Could not decode response content as JSON.")

                    except requests.exceptions.RequestException as req_err:
                        st.error(f"Request failed: {req_err}")

                    except (KeyError, IndexError, TypeError) as json_err:
                        st.error(f"Error processing the response (JSON format issue): {json_err}")
                        st.error(f"Raw response content: {response.text}")

            else:
                st.warning("Please enter a prompt.")
else:
    st.warning("Please enter a valid Hugging Face API Key to continue.")







# import streamlit as st
# import requests
# import pandas as pd
# import os  # Import os module for environment variables

# # Fetch Hugging Face API key from environment variables
# HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
# if not HF_TOKEN:
#     st.error("Hugging Face API key not found. Please set it in the terminal.")
#     st.stop()

# # Hugging Face API URL
# API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
# headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# # Streamlit UI
# st.title("AI Text Generator with CSV Input")
# st.write("Enter a prompt, optionally upload a CSV, and the AI will generate a response.")

# # File upload
# uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
# if uploaded_file is not None:
#     try:
#         df = pd.read_csv(uploaded_file)
#         st.success("CSV file uploaded successfully!")
#         st.write("Preview of the data:")
#         st.dataframe(df.head())  # Display a preview of the data
#     except Exception as e:
#         st.error(f"Error reading CSV: {e}")
#         df = None  # Reset df if there's an error
# else:
#     df = None

# # Text input
# text_input = st.text_area("Enter your prompt:", "")

# # Generate button
# if st.button("Generate"):
#     if text_input:
#         with st.spinner("Generating..."):
#             # Incorporate CSV data if available
#             if uploaded_file is not None and df is not None:
#                 csv_context = "Here's the relevant data from the CSV file:\n" + df.to_string() + "\n\n"
#                 prompt_with_csv = csv_context + "Based on the CSV data, answer this question or fulfill this request: " + text_input
#                 payload = {"inputs": prompt_with_csv, "parameters": {"max_new_tokens": 1000}}
#             else:
#                 payload = {"inputs": text_input, "parameters": {"max_new_tokens": 1000}}

#             try:
#                 response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
#                 response.raise_for_status()
#                 json_response = response.json()
#                 generated_text = json_response[0]["generated_text"]
#                 st.write("### Generated Response:")
#                 st.markdown(f'<div id="response-container" style="border: 1px solid #ddd; padding: 10px; background: #f9f9f9; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{generated_text}</div>', unsafe_allow_html=True) # Apply styles
#             except requests.exceptions.RequestException as e:
#                 st.error(f"Request failed: {e}")
#             except (KeyError, IndexError, TypeError) as e:
#                 st.error(f"Error processing the response: {e}. Check the API response format.")
#     else:
#         st.warning("Please enter a prompt.")



# # Custom CSS to improve the UI
# st.markdown(
#     """
#     <style>
#     /* General styles */
#     body {
#         font-family: 'Arial', sans-serif;
#         background-color: #f8f9fa;
#         color: #343a40;
#     }

#     .stApp {
#         max-width: 900px; /* Increase max width for better readability */
#         margin: 0 auto; /* Center the app */
#         padding: 20px;
#     }

#     /* Title */
#     .st-emotion-cache-10tr9gx { /* Adjust the title style class */
#         color: #007bff;
#         text-align: center;
#         margin-bottom: 20px;
#     }

#     /* Section headers */
#     h3 {
#         color: #28a745;
#         margin-top: 20px;
#         margin-bottom: 10px;
#     }

#     /* Text area and file uploader styles */
#     .st-emotion-cache-16ids5y { /* text area */
#       border-radius: 5px;
#       border: 1px solid #ced4da;
#       padding: 10px;
#       margin-bottom: 15px;
#       background-color: #fff;
#     }

#     .st-emotion-cache-1w7h7m { /* file uploader */
#         border-radius: 5px;
#         border: 1px solid #ced4da;
#         padding: 10px;
#         margin-bottom: 15px;
#         background-color: #fff;
#     }


#     /* Button styles */
#     .stButton>button {
#         background-color: #007bff;
#         color: white;
#         border: none;
#         border-radius: 5px;
#         padding: 10px 20px;
#         cursor: pointer;
#         transition: background-color 0.2s ease;
#     }

#     .stButton>button:hover {
#         background-color: #0056b3;
#     }

#     /* DataFrame Styles */
#     .stDataFrame {
#         margin-bottom: 20px;
#         border-radius: 5px;
#         overflow: auto; /* Add scroll if table is too wide */
#     }

#     /* Response Container Styles (already present, but improving it) */
#     #response-container { /* Defined above in st.markdown */
#         border-radius: 5px;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#         overflow-wrap: break-word;  /* Prevent overflow of long words */
#     }

#     /* Spinner Styles (minor adjustments) */
#     .st-emotion-cache-162po9a { /* Spinner */
#         color: #007bff;
#     }

#     </style>
#     """,
#     unsafe_allow_html=True,
# )





