
import streamlit as st
import requests

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Personal Assistant",
    page_icon="🤖",
    layout="centered"
)

# ---------------- AI CONFIG ----------------
API_URL = "https://vireonix.ai/v1/chat/completions"
MODEL = "auto"

SYSTEM_PROMPT = """
You are a helpful AI Personal Assistant.
Answer clearly, accurately and politely.
You can answer questions about:
- Education and programming
- Computer science
- Science and technology
- General knowledge
- Writing and translation
- Career guidance
- Everyday questions

Understand Hindi, English and Hinglish.
Reply in the language used by the user.
If you do not know an answer, say so honestly.
Use examples when helpful.
"""

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    max-width: 900px;
    margin: auto;
}
.stChatMessage {
    border-radius: 12px;
}
.title {
    text-align: center;
    font-size: 34px;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(
    '<div class="title">🤖 AI Personal Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your smart AI assistant</div>',
    unsafe_allow_html=True
)

st.divider()

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Settings")

    st.success("AI Service: Online AI")

    st.caption("No Gemini API key required.")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.markdown("### About")
    st.write(
        "This AI assistant can answer questions "
        "in Hindi, English and Hinglish."
    )

    st.caption("Powered by Vireonix AI")

# ---------------- DISPLAY CHAT ----------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- AI FUNCTION ----------------
def get_ai_response(messages):

    api_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # Send recent conversation context
    api_messages.extend(messages[-12:])

    payload = {
        "model": MODEL,
        "messages": api_messages,
        "temperature": 0.7,
        "max_tokens": 1500
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=90
        )

        if response.status_code != 200:
            return (
                f"AI service error ({response.status_code}): "
                f"{response.text[:1000]}"
            )

        data = response.json()

        answer = data["choices"][0]["message"]["content"]

        if isinstance(answer, list):
            answer = "\n".join(
                item.get("text", "")
                for item in answer
                if isinstance(item, dict)
            )

        if not answer:
            return "AI returned an empty response. Please try again."

        return str(answer)

    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."

    except requests.exceptions.ConnectionError:
        return "Internet connection or AI service connection failed."

    except requests.exceptions.RequestException as e:
        return f"Network error: {str(e)}"

    except (KeyError, IndexError, TypeError, ValueError) as e:
        return f"Invalid AI response: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"


# ---------------- CHAT INPUT ----------------
user_input = st.chat_input(
    "Ask me anything..."
)

if user_input:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("🤖 AI is thinking..."):

            answer = get_ai_response(
                st.session_state.messages
            )

        st.markdown(answer)

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()

# ---------------- FOOTER ----------------
st.divider()

st.caption(
    "AI Personal Assistant | Built with Python and Streamlit"
)
