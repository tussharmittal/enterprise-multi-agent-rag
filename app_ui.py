import streamlit as st
import requests
import time

# Point this to your FastAPI server
API_URL = "http://127.0.0.1:8000"

# Configure the page aesthetics
st.set_page_config(page_title="Enterprise AI Agent", page_icon="🤖", layout="centered")
st.title("Enterprise Multi-Agent Search 🌐")
st.caption("Powered by FastAPI, Upstash Redis, arq, and Groq (Llama 3.1)")

# Initialize the chat history in the browser's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Redraw the chat history every time the page updates
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# The Chat Input Box
if prompt := st.chat_input("Ask a quick question or request a deep web-research report..."):
    # 1. Display the user's prompt in the UI
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Send the request to your FastAPI Backend
    try:
        with st.spinner("Routing your request..."):
            response = requests.post(f"{API_URL}/ask", json={"query": prompt, "limit": 2})
            response.raise_for_status()
            data = response.json()

        # Branch A: The Fast Route (Cache or Vector DB)
        if data["status"] == "success":
            source = data.get("source", "database")
            process_time = data.get("process_time_ms", 0)
            
            # Format the answer (simplifying the list of results for the UI)
            answer_text = f"*(Served instantly from {source} in {process_time}ms)*\n\n"
            answer_text += str(data["data"]) 

            with st.chat_message("assistant"):
                st.markdown(answer_text)
            st.session_state.messages.append({"role": "assistant", "content": answer_text})

        # Branch B: The Heavy Research Route (Async Worker)
        elif data["status"] == "accepted":
            job_id = data["job_id"]
            
            # Create an empty box in the UI to show live status updates
            status_box = st.empty()
            
            # Start the Polling Loop
            while True:
                status_res = requests.get(f"{API_URL}/status/{job_id}")
                status_data = status_res.json()
                current_status = status_data["status"]
                
                if current_status == "queued":
                    status_box.info("⏳ Task queued in Redis. Waiting for worker...")
                
                elif current_status == "processing":
                    status_box.warning("🧠 Llama 3.1 is scraping the web and writing the report...")
                
                elif current_status == "complete":
                    status_box.empty() # Clear the loading message
                    final_report = status_data["data"]
                    
                    # Print the beautiful Markdown report!
                    with st.chat_message("assistant"):
                        st.markdown(final_report)
                    st.session_state.messages.append({"role": "assistant", "content": final_report})
                    break # Exit the loop
                    
                elif current_status == "failed":
                    status_box.error("❌ Task failed in the background.")
                    break
                    
                # Wait 2 seconds before asking the server again
                time.sleep(2)

    except requests.exceptions.ConnectionError:
        st.error("🚨 Could not connect to the API. Is your FastAPI server running on port 8000?")
    except Exception as e:
        st.error(f"An error occurred: {e}")