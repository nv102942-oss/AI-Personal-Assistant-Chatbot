
import streamlit as st
import requests

st.set_page_config(
    page_title="AI Personal Assistant",
    page_icon="🤖",
    layout="centered"
)

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """
You are a helpful AI Personal Assistant.
Answer questions in Hindi, English and Hinglish.
Help with programming, education, science,
technology, general knowledge and career guidance.
Give clear explanations and examples.
"""

st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
}
.title {
    text-align: center;
    color: #2563eb;
    font-size: 34px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="title">🤖 AI Personal Assistant</div>',
    unsafe_allow_html=True
)

st.caption("Your Smart AI Chatbot")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚙️ Settings")
    st.success("Groq AI Assistant")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.write("Supports Hindi and English.")
    st.write("Powered by Groq AI")

def get_ai_response(messages):
    try:
        api_key = st.secrets["GROQ_API_KEY"]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        api_messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        api_messages.extend(messages[-12:])

        payload = {
            "model": MODEL,
            "messages": api_messages,
            "temperature": 0.7,
            "max_tokens": 1200
        }

        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=90
        )

        if response.status_code == 401:
            return "Invalid API key. Check Streamlit Secrets."

        if response.status_code == 429:
            return "Free usage limit reached. Please try later."

        if response.status_code != 200:
            return (
                f"Groq API Error ({response.status_code}): "
                f"{response.text[:500]}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except KeyError:
        return "GROQ_API_KEY missing in Streamlit Secrets."

    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."

    except requests.exceptions.ConnectionError:
        return "Internet connection failed."

    except Exception as e:
        return f"Error: {str(e)}"

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask me anything...")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("🤖 AI is thinking..."):
            answer = get_ai_response(
                st.session_state.messages
            )

        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()

st.divider()
st.caption("AI Personal Assistant | Python + Streamlit")
