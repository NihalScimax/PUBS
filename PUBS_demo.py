import streamlit as st
import requests
from PyPDF2 import PdfReader
from fpdf import FPDF
import io
import textwrap

# **Mistral 7B API Endpoint (Replace with your AWS URL)**
MISTRAL_API_URL = "https://arin.scimaxmi.com/api/input/predict"

# **Streamlit Page Configuration**
st.set_page_config(page_title="AI PDF Simplifier", page_icon="📄", layout="wide")

# **Custom Styling for Font and Layout**
st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: #FFFFFF;
        font-size: 16px;  /* Reduced font size */
        border-radius: 8px;
    }
    .stFileUploader label {
        font-size: 16px;  /* Reduced font size */
        font-weight: bold;
        color: #FFFFFF;
    }
    .stProgress {
        height: 12px !important;  /* Reduced progress bar height */
    }
    .big-title {
        font-size: 32px;  /* Reduced title size */
        font-weight: bold;
        text-align: center;
        color: #FFFFFF;
        margin-bottom: 30px;
    }
    .small-box {
        background-color: #000000; /* Black background */
        padding: 15px;
        border-radius: 10px;
        font-size: 12px;  /* Smaller font */
        text-align: left;
        color: #FFFFFF; /* White text for contrast */
    }
    </style>
""", unsafe_allow_html=True)

# **Title Section with More Space**
st.markdown("<h1 class='big-title'>📄 AI-Powered PDF Simplifier</h1>", unsafe_allow_html=True)
st.write("### 🚀 Upload a PDF file, and our **Mistral 7B model** will simplify its content for easy understanding.")

# **Layout: Left (Main App) & Right (Info Box)**
col1, col2 = st.columns([3, 1], gap="large")  # Pushes box to the right

with col1:
    uploaded_file = st.file_uploader("📤 Upload your PDF", type="pdf")

with col2:
    st.markdown("<div class='small-box'>", unsafe_allow_html=True)
    st.markdown("### 🖼️ How We Simplify Images")
    st.write("📊 **Visual graphs become clear**: AI scans charts, extracts key points, and presents them in simple terms.")
    st.write("🖼️ **Complicated diagrams? No problem!** Our AI redraws them into easier-to-read formats.")
    st.write("🤖 **Smart Processing**: We don’t just read images. We understand them!")
    st.markdown("</div>", unsafe_allow_html=True)

TOKEN_LIMIT = 1000  # Adjust based on Mistral’s max token limit


def extract_text_from_pdf(pdf_stream):
    """Extract text from a PDF file and return as chunks."""
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


def request_mistral(text):
    """Send text to AWS-hosted Mistral 7B for simplification."""
    prompt = f"<s>Text:{text} [INST]Generate plain language summary for the given text[/INST]</s>"
    payload = {
        "prompt": prompt,
        "temperature": 0.5,
        "top_p": 0.7,
        "top_k": 50,
        "no_repeat_ngram_size": 2
    }

    try:
        response = requests.post(MISTRAL_API_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "No text generated")
        else:
            return f"Error: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"


def simplify_text(chunks):
    """Process text chunks through Mistral API."""
    simplified_chunks = []
    progress_bar = st.progress(0)

    for i, chunk in enumerate(chunks):
        simplified_content = request_mistral(chunk['content'])
        simplified_chunks.append({"page_number": chunk['page_number'], "content": simplified_content})

        # Update progress bar
        progress = (i + 1) / len(chunks)
        progress_bar.progress(progress)

    return simplified_chunks


def generate_pdf(pages):
    """Generate a PDF with simplified text."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)  # Reduced font size for better readability

    for page in pages:
        pdf.add_page()
        pdf.multi_cell(0, 8, page['content'])  # Adjusted spacing

    output_buffer = io.BytesIO()
    pdf.output(output_buffer, "F")
    output_buffer.seek(0)
    return output_buffer


# **Streamlit Workflow**
if uploaded_file is not None:
    st.markdown("### ⏳ Processing your PDF... Please wait.")

    with st.spinner("Extracting text..."):
        text_chunks = extract_text_from_pdf(uploaded_file)

    with st.spinner("Simplifying content using AI..."):
        simplified_text = simplify_text(text_chunks)

    with st.spinner("Generating the final PDF..."):
        final_pdf = generate_pdf(simplified_text)

    # **Provide Download Link**
    st.success("✅ PDF Simplification Complete! 🎉")
    st.download_button("📥 Download Your Simplified PDF", final_pdf, "simplified.pdf", "application/pdf")

else:
    st.info("📂 Please upload a PDF file to begin.")
