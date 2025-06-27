# Document Q&A Chatbot

A web-based chatbot that lets you upload TXT, PDF, DOCX, and Excel files, then ask questions and get answers based on your documents using OpenAI's GPT.

## Features
- Upload multiple TXT, PDF, DOCX, or Excel files
- Extracts and indexes content from your files
- Ask questions in a chat interface
- Answers are generated using OpenAI GPT and your document content

## Setup

1. **Clone this repo and navigate to the `agent/` directory**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```bash
   streamlit run app.py
   ```
4. **Open the web interface:**
   - Go to the local URL shown in your terminal (usually http://localhost:8501)

## Usage
- Upload your TXT, PDF, DOCX, or Excel files in the sidebar
- Enter your OpenAI API key in the sidebar
- Ask questions about your documents in the main chat area
- The bot will answer using the content of your uploaded files

---

*This project is for local/private use. Your files are not uploaded anywhere except your own machine.* 