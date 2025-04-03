import streamlit as st
import requests
from PyPDF2 import PdfReader
import io
import textwrap

# **Mistral 7B API Endpoint (Replace with your AWS URL)**
MISTRAL_API_URL = "https://arin.scimaxmi.com/api/input/evaluate"

# **Streamlit Page Configuration**
st.set_page_config(page_title="AI PDF Query", page_icon="📄", layout="wide")

# **Custom Styling**
st.markdown("""
    <style>
    body { font-family: 'Arial', sans-serif; }
    .stButton>button { width: 100%; background-color: #4CAF50; color: white; border-radius: 8px; }
    .big-title { font-size: 32px; font-weight: bold; text-align: center; color: #FFFFFF; margin-bottom: 30px; }
    .small-box { background-color: #000000; padding: 15px; border-radius: 10px; font-size: 12px; color: #FFFFFF; }
    </style>
""", unsafe_allow_html=True)

# **Title Section**
st.markdown("<h1 class='big-title'>📄 AI-Powered PDF Query</h1>", unsafe_allow_html=True)
st.write("### 🚀 Upload a PDF and enter a query to extract relevant information!")

# **Layout: Left (Main App) & Right (Info Box)**
col1, col2 = st.columns([3, 1], gap="large")

with col1:
    uploaded_file = st.file_uploader("📤 Upload your PDF", type="pdf")
    user_query = st.text_area("🔍 Enter Your Query (e.g., 'Extract details about XYZ topic'):", "")

with col2:
    st.markdown("<div class='small-box'>", unsafe_allow_html=True)
    st.markdown("### 🖼️ How It Works")
    st.write("💡 **Upload a PDF**: The AI scans the document.")
    st.write("🔎 **Enter a Query**: Instead of summarizing the whole file, AI will find the most relevant sections.")
    st.write("📋 **Get Focused Results**: Download a new PDF with only the extracted content!")
    st.markdown("</div>", unsafe_allow_html=True)

TOKEN_LIMIT = 1000  # Adjust for Mistral’s token limit

def extract_text_from_pdf(pdf_stream):
    """Extract text from a PDF and return as chunks."""
    reader = PdfReader(pdf_stream)
    chunks = []
    for page_number, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():  # Ignore empty pages
            for i in range(0, len(text), TOKEN_LIMIT):
                chunk_content = text[i:i + TOKEN_LIMIT].strip()
                if chunk_content:
                    chunks.append({"page_number": page_number + 1, "content": chunk_content})
    return chunks

def request_mistral(text, query):
    """Send text to AWS-hosted Mistral 7B for query-based extraction."""
    prompt = f"""
    <s>Text:{text}
    [INST] Extract information relevant to the following query: "{query}" [/INST]
    </s>
    """
    payload = {"prompt": prompt, "temperature": 0.5, "top_p": 0.7, "top_k": 50, "no_repeat_ngram_size": 2}
    try:
        response = requests.post(MISTRAL_API_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "No text generated")
        else:
            return f"Error: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

def extract_relevant_text(chunks, query):
    """Process text chunks through Mistral API based on the query."""
    extracted_chunks = []
    progress_bar = st.progress(0)
    for i, chunk in enumerate(chunks):
        extracted_content = request_mistral(chunk['content'], query)
        if extracted_content.strip():
            extracted_chunks.append({"page_number": chunk['page_number'], "content": extracted_content})
        progress = (i + 1) / len(chunks)
        progress_bar.progress(progress)
    return extracted_chunks

def generate_pdf(pages):
    """Generate a PDF with extracted text."""
    from fpdf import FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)
    for page in pages:
        pdf.add_page()
        pdf.multi_cell(0, 8, f"Page {page['page_number']}\n{page['content']}")
    output_buffer = io.BytesIO()
    pdf.output(output_buffer, "F")
    output_buffer.seek(0)
    return output_buffer

if uploaded_file is not None and user_query.strip():
    st.markdown("### ⏳ Processing your request... Please wait.")
    with st.spinner("Extracting text..."):
        text_chunks = extract_text_from_pdf(uploaded_file)
    with st.spinner("Finding relevant content using AI..."):
        relevant_text = extract_relevant_text(text_chunks, user_query)
    with st.spinner("Generating the final PDF..."):
        final_pdf = generate_pdf(relevant_text)
    st.success("✅ Extraction Complete! 🎉")
    st.download_button("📥 Download Extracted Content", final_pdf, "extracted_info.pdf", "application/pdf")
else:
    st.info("📂 Please upload a PDF and enter a query to begin.")
