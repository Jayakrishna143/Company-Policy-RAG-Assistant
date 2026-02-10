import streamlit as st
import requests
import os

API_URL ="http://localhost:8000"

st.set_page_config(page_title="Policy Assistant")
st.title("Policy Assistant")
try:
    response = requests.get(f"{API_URL}/check-database")
    db_status = response.json()
except:
    st.error("cannot connect to database")
    st.stop()
if not db_status["exists"]:
    st.warning("database does not exist")

    uploaded_file = st.file_uploader(
        "Upload a file",
        accept_multiple_files=True,
    )
    if st.button("Upload"):
        if not uploaded_file:
            st.warning("no file uploaded")
        else:
            with st.spinner("Uploading..."):
                files = [("files",(f.name,f,"application/pdf")) for f in uploaded_file]
                response = requests.post(f"{API_URL}/ingest", files=files)

                if response.status_code == 200:
                    st.success("file uploaded")
                    st.rerun()
                else:
                    st.error("unable to upload")
else:
    st.sidebar.success("database ready")
    question = st.text_input("Ask a question about compony policies")

    if question:
       with st.spinner("Thinking..."):
           response = requests.post(f"{API_URL}/ask", json={"question":question})
           if response.status_code == 200:
               data = response.json()
               st.subheader("Answer")
               st.write(data["answer"])

               with st.expander("view sources"):
                   for i ,source in enumerate(data["sources"]):
                       st.markdown(f"**Source #{i+1}:**")
                       st.info(source)
           else:
               st.error("unable to answer")