
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
You are an intelligent AI Personal Assistant.
Answer in Hindi, English and Hinglish.
Help with programming, education, science,
technology, general knowledge and career guidance.
Give clear and detailed answers with examples.
Never return an empty answer.
"""

# CSS DESIGN
st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
    color: #172033;
}
.title {
    text-align: center;
    color: #2563eb;
    font-size: 34px;
    font-weight: bold;
}
[data-testid="stChatMessage"] {
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}
[data-testid="stChatInput"] {
    background-color: white;
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown(
    '<div class="title">🤖 AI Personal Assistant</div>',
    unsafe_allow_html=True
)
st.caption("Your Smart AI Chatbot")
st.divider()

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR
with st.sidebar:
    st.title("⚙️ Settings")
    st.success("Groq AI Assistant")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.write("🌐 Hindi & English Support")
    st.write("💻 Programming Help")
    st.write("📚 Education Support")
    st.write("⚡ Powered by Groq AI")

# AI RESPONSE FUNCTION
def get_ai_response(messages):

    try:
        api_key = st.secrets["GROQ_API_KEY"]

        if not api_key:
            return "Error: API key is empty."

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
            "max_tokens": 1500
        }

        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            try:
                error = response.json()
                message = error.get(
                    "error", {}
                ).get("message", response.text)
            except Exception:
                message = response.text

            return (
                f"Groq API Error {response.status_code}: "
                f"{message}"
            )

        data = response.json()

        answer = data["choices"][0]["message"]["content"]

        if not answer or not answer.strip():
            return "AI returned an empty answer. Try again."

        return answer.strip()

    except KeyError:
        return "GROQ_API_KEY missing in Streamlit Secrets."

    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."

    except requests.exceptions.ConnectionError:
        return "Internet connection failed."

    except Exception as e:
        return f"Error: {str(e)}"


# DISPLAY CHAT HISTORY
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# CHAT INPUT
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

# FOOTER
st.divider()
st.caption("AI Personal Assistant | Python + Streamlit + Groq")
