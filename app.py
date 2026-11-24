import streamlit as st
from pypdf import PdfReader
from google import genai
from google.genai import types

st.set_page_config(page_title="Campus GenAI Assistant", page_icon="🎓")
st.title("🎓 Campus Policy & Syllabus Assistant")
st.write("Upload your university PDF documents and ask any question.")

with st.sidebar:
    st.header("Setup")
    api_key = st.text_input("Paste Gemini API Key", type="password")
    uploaded_files = st.file_uploader(
        "Upload PDFs (Syllabus, Circulars, Notes)",
        type=["pdf"],
        accept_multiple_files=True,
    )

def read_pdfs(files):
    text = ""
    for pdf in files:
        reader = PdfReader(pdf)
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text += f"\n[Source: {pdf.name}, Page {page_num + 1}]\n{page_text}"
    return text

if api_key and uploaded_files:
    document_text = read_pdfs(uploaded_files)
    st.success(f"Loaded {len(uploaded_files)} PDF file(s)!")

    question = st.text_input("Type your question here:")
    if st.button("Ask AI") and question:
        with st.spinner("Reading documents and generating answer..."):
            client = genai.Client(api_key=api_key)
            rules = (
                "You are a helpful university assistant. Answer ONLY using the "
                "uploaded documents below. Always mention the document name and page "
                "number. If the answer is not in the documents, say: 'This information "
                "is not mentioned in the uploaded documents.'"
            )
            prompt = f"DOCUMENTS:\n{document_text[:60000]}\n\nSTUDENT QUESTION: {question}"
            
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=rules,
                    temperature=0.2,
                ),
            )
            st.subheader("Answer:")
            st.write(response.text)
else:
    st.info("👈 Paste your API key and upload a PDF in the left sidebar to start.")
