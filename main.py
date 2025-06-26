# main.py

import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
# This is crucial for securely loading your API key.
load_dotenv()

# --- Configuration ---
# Get your Google API Key from environment variables.
# It's recommended to set GOOGLE_API_KEY in your system's environment
# or in a .env file in the root of your project.

API_KEY = os.getenv("GOOGLE_API_KEY")
#API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not API_KEY:
    st.error("Lỗi: Không tìm thấy GOOGLE_API_KEY. Vui lòng đặt nó làm biến môi trường hoặc trong tệp .env.")
    st.info("Bạn có thể lấy API Key từ Google AI Studio (aistudio.google.com).")
    st.stop() # Stop the Streamlit app if API key is missing

# Configure the generative AI model
genai.configure(api_key=API_KEY)

# Initialize the Gemini model (cached for performance)
# We use 'gemini-pro' for text generation.
# Adjust generation configuration for desired output.
@st.cache_resource
def get_gemini_model():
    """Caches the Gemini GenerativeModel instance."""
    return genai.GenerativeModel(
        'gemini-2.0-flash',
        generation_config={
            "temperature": 0.7,  # Controls randomness. Lower for more deterministic output.
            "max_output_tokens": 1024, # Maximum number of tokens in the response.
        }
    )

model = get_gemini_model()

# --- Helper Functions ---

def read_file_content(uploaded_file):
    """
    Reads the content of an uploaded text file from Streamlit.
    Args:
        uploaded_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The file uploaded via Streamlit.
    Returns:
        str: The content of the file, or None if an error occurs.
    """
    try:
        # Decode the bytes content of the uploaded file to a string
        content = uploaded_file.read().decode('utf-8')
        return content
    except Exception as e:
        st.error(f"Lỗi khi đọc tệp: {e}. Vui lòng đảm bảo đây là tệp văn bản hợp lệ.")
        return None

def get_chat_response(file_content, user_query):
    """
    Interacts with the Gemini model using file content as context.
    Args:
        file_content (str): The content of the file to use as context.
        user_query (str): The user's question.
    Returns:
        str: The model's response.
    """
    if not file_content:
        return "Tôi không có nội dung tệp để trả lời câu hỏi của bạn."

    # Construct the prompt by combining file content and user's query.
    # It's important to clearly delineate the context and the question.
    prompt = f"""
    Bạn là một trợ lý chatbot thông minh. Bạn sẽ trả lời các câu hỏi của người dùng dựa trên NỘI DUNG TỆP sau đây.
    Nếu câu hỏi không liên quan đến nội dung tệp, hãy nói rằng bạn chỉ có thể trả lời các câu hỏi liên quan đến tệp đã cung cấp.

    NỘI DUNG TỆP:
    ---
    {file_content}
    ---

    CÂU HỎI CỦA NGƯỜI DÙNG: {user_query}

    TRẢ LỜI CỦA BẠN:
    """
    try:
        with st.spinner("Đang suy nghĩ..."): # Show a loading spinner while waiting for the API response
            response = model.generate_content(prompt)
            return response.text
    except Exception as e:
        st.error(f"Lỗi khi gọi API Gemini: {e}")
        return "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu của bạn. Vui lòng thử lại."

# --- Streamlit UI ---

def main():
    """
    Main function to run the Streamlit chatbot application.
    """
    st.set_page_config(page_title="Chatbot đọc tệp (Gemini AI)", page_icon="📄", layout="centered")
    st.title("📄 Chatbot")
    st.markdown("""
        Chào mừng bạn đến với Chatbot đọc tệp!
        Tải lên một tệp văn bản và hỏi tôi bất cứ điều gì liên quan đến nội dung của nó.
    """)

    # File uploader widget
    uploaded_file = st.file_uploader("Chọn một tệp văn bản (.txt) để tải lên", type=["txt"])

    file_content = None
    if uploaded_file is not None:
        file_content = read_file_content(uploaded_file)
        if file_content:
            st.success("Đã tải tệp thành công! Bây giờ bạn có thể hỏi các câu hỏi.")
            # Display a snippet of the file content for confirmation
            with st.expander("Xem nội dung tệp đã tải (100 ký tự đầu)"):
                st.code(file_content[:500] + "..." if len(file_content) > 500 else file_content)
        else:
            uploaded_file = None # Reset if file reading failed

    # Chat input and history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Bạn hỏi gì về nội dung tệp?"):
        # Display user message in chat message container
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from chatbot
        if uploaded_file is None:
            response_text = "Vui lòng tải lên một tệp trước khi đặt câu hỏi."
        else:
            response_text = get_chat_response(file_content, prompt)
        
        # Display assistant response in chat message container
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)

if __name__ == "__main__":
    main()
