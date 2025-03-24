# 📄 AI-Powered PDF Simplifier & Visual Data Transformer

## 🚀 Overview
This Streamlit-based web application simplifies complex textual content from PDFs and transforms visual data representations into more understandable formats. It leverages **Mistral 7B** for advanced text simplification and an external API for image-based data summarization.

## 🎯 Features
- 📄 **Extracts text from PDFs** and processes large documents efficiently.
- 🧠 **Utilizes Mistral 7B** to generate plain-language summaries.
- 🖼️ **Converts complex images and visualizations** into simpler representations.
- 🎨 **Interactive and user-friendly UI** with professional aesthetics.
- ☁️ **Streamlit-based** for easy deployment and accessibility.

## 🏗️ Tech Stack
- **Python**
- **Streamlit**
- **PyPDF2** (PDF text extraction)
- **FPDF** (PDF generation)
- **Requests** (API calls)
- **Mistral 7B** (AI-powered text simplification)

## 📂 Project Structure
```
📁 project-root
│-- 📄 app.py          # Main Streamlit app
│-- 📄 requirements.txt # Dependencies
│-- 📄 README.md        # Project documentation
```

## 🔧 Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
   ```

2. **Create a virtual environment (Optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Running the App Locally
```bash
streamlit run app.py
```
After running, the app will be accessible at:
```
http://localhost:8501
```

## 🚀 Deploying on Streamlit Cloud
1. Upload all files to a **GitHub repository**.
2. Add a **requirements.txt** file with all dependencies.
3. Deploy via **Streamlit Cloud**.

## 🛠️ Troubleshooting
### **ModuleNotFoundError: No module named 'PyPDF2'**
- Ensure `requirements.txt` includes `PyPDF2` and is uploaded to Streamlit.
- Restart the Streamlit deployment after adding dependencies.

## 📜 License
This project is licensed under the **MIT License**.

---

💡 **Contributions are welcome!** Feel free to open issues or submit PRs. 😊

