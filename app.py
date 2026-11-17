
import streamlit as st
import time
from google import genai

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="AI Personal Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Personal Assistant Chatbot")
st.caption("Your personal AI assistant | Hindi + English")

# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.header("⚙️ Settings")

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Paste your NEW API key here"
    )

    st.caption("Keep your API key private.")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------- DISPLAY CHAT HISTORY ----------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- CHAT INPUT ----------------

user_prompt = st.chat_input("Ask anything...")

if user_prompt:

    if not api_key.strip():
        st.warning("Please enter your Gemini API key in Settings.")

    else:

        # Save user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_prompt
        })

        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Prepare conversation
        conversation = []

        for item in st.session_state.messages[-12:]:
            role = "User" if item["role"] == "user" else "Assistant"
            conversation.append(
                f"{role}: {item['content']}"
            )

        prompt = (
            "You are a helpful and friendly personal AI assistant. "
            "Reply in the same language as the user. "
            "Give clear, accurate and useful answers. "
            "If you do not know something, say so.\n\n"
            + "\n\n".join(conversation)
        )

        # ---------------- GEMINI BACKGROUND API ----------------

        with st.chat_message("assistant"):

            try:
                client = genai.Client(
                    api_key=api_key.strip(),
                    http_options={"timeout": 60000}
                )

                with st.spinner("Connecting to Gemini AI..."):

                    # Start background request
                    interaction = client.interactions.create(
                        model="gemini-3.8-flash",
                        input=prompt,
                        background=True
                    )

                # Check background task
                answer = None
                attempts = 0

                progress = st.progress(0)
                status_text = st.empty()

                while attempts < 120:

                    if interaction.status == "completed":
                        answer = interaction.output_text
                        break

                    if interaction.status == "failed":
                        raise RuntimeError(
                            "Gemini background task failed."
                        )

                    if interaction.status != "in_progress":
                        raise RuntimeError(
                            "Unexpected task status: "
                            + str(interaction.status)
                        )

                    time.sleep(5)

                    interaction = client.interactions.get(
                        interaction.id
                    )

                    attempts += 1
                    progress.progress(min(attempts / 120, 1.0))
                    status_text.write(
                        f"AI is working... {attempts * 5} seconds"
                    )

                if answer is None:
                    raise TimeoutError(
                        "AI took too long. Please try again."
                    )

                if not answer.strip():
                    answer = "Sorry, AI returned an empty response."

                progress.empty()
                status_text.empty()

                st.markdown(answer)

                # Save AI response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:

                st.error("Gemini AI request failed.")

                st.write("Technical error:")
                st.code(str(error))

                st.info(
                    "Check your internet, API key and Gemini API access."
                )

# ---------------- WELCOME MESSAGE ----------------

if not st.session_state.messages:
    st.info(
        "👋 Welcome! Try asking: "
        "Explain Artificial Intelligence in simple Hindi."
    )

    st.markdown("### Example questions")

    st.write("- What is Artificial Intelligence?")
    st.write("- Explain Python in Hindi.")
    st.write("- Write a C++ program.")
    st.write("- What is Machine Learning?")
