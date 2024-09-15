from diff_pipeline import chat
from funcs_file import get_tools
import streamlit as st
import re


def get_avatar_url(role):
    if role == "assistant":
        return "https://shorturl.at/LqdTy"
    else:
        return "https://shorturl.at/uFX1t"


def get_code(text):
    reg = r"<CODE>(.*?)</CODE>"
    matches = re.findall(reg, text, re.DOTALL)
    if matches:
        return matches[0]
    return None


st.set_page_config(page_title="")
with st.sidebar:
    st.title("CWYD")


@st.cache_resource
def load_model():
    return chat(tools=get_tools())


bot = load_model()


def generate_response(input):
    result, code = bot.run_n_branch(input)
    return result, code


if "session_messages" not in st.session_state:
    st.session_state.session_messages = [{"role": "system", "content": bot.DEF_PRMPT}]
    st.session_state.session_messages.append(
        {"role": "assistant", "content": "Welcome! How can I help you?"}
    )

for message in st.session_state.session_messages:
    role = message["role"]
    exclude_system = role != "system"
    no_tool_call_id = "tool_call_id" not in message
    no_tool_calls = "tool_calls" not in message

    if exclude_system and no_tool_call_id and no_tool_calls:
        avatar_url = get_avatar_url(role)
        with st.chat_message(role, avatar=avatar_url):
            code = get_code(message["content"])
            if code:
                query = message["content"].split("<SPLIT>")
                st.write(query[0])
                st.code(code)
            else:
                st.write(message["content"])

if input := st.chat_input():
    st.session_state.session_messages.append({"role": "user", "content": input})
    with st.chat_message("user", avatar="https://shorturl.at/uFX1t"):
        st.write(input)

if (
    st.session_state.session_messages[-1]["role"] != "assistant"
    and st.session_state.session_messages[-1]["role"] != "system"
    and st.session_state.session_messages[-1]["role"] != "tool"
):
    with st.chat_message("assistant", avatar="https://shorturl.at/LqdTy"):
        # with st.spinner("Fetching your data"):
        response, code = generate_response(st.session_state.session_messages)
        st.write(response)
        if code:
            st.code(code)
            code = "<SPLIT> <CODE>" + code + "</CODE>"

        response = response + code

    message = {"role": "assistant", "content": response}
    st.session_state.session_messages.append(message)