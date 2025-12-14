import streamlit as st
from langgraph_backend_db import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ****************************************
# Utility Functions
# ****************************************

def generate_thread_id():
    return str(uuid.uuid4())

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

def get_last_user_question(thread_id):
    messages = load_conversation(thread_id)
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content[:40]
    return "New Chat"

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []
    st.session_state['chat_threads'].append(thread_id)
    st.session_state['thread_titles'][thread_id] = "New Chat"


# ****************************************
# Session Setup
# ****************************************

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {
        tid: get_last_user_question(tid)
        for tid in st.session_state['chat_threads']
    }

# Select existing thread on refresh (NO new thread creation)
if 'thread_id' not in st.session_state:
    if st.session_state['chat_threads']:
        st.session_state['thread_id'] = st.session_state['chat_threads'][-1]
    else:
        st.session_state['thread_id'] = None

if 'message_history' not in st.session_state:
    if st.session_state['thread_id']:
        messages = load_conversation(st.session_state['thread_id'])
        st.session_state['message_history'] = [
            {
                "role": "user" if isinstance(m, HumanMessage) else "assistant",
                "content": m.content
            }
            for m in messages
        ]
    else:
        st.session_state['message_history'] = []


# ****************************************
# Sidebar UI
# ****************************************

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("➕ New Chat"):
    reset_chat()

st.sidebar.divider()
st.sidebar.subheader("My Conversations")

if st.session_state['chat_threads']:

    thread_labels = [
        st.session_state['thread_titles'][tid]
        for tid in st.session_state['chat_threads']
    ]

    label_to_thread = dict(zip(thread_labels, st.session_state['chat_threads']))

    current_index = (
        st.session_state['chat_threads'].index(st.session_state['thread_id'])
        if st.session_state['thread_id'] in st.session_state['chat_threads']
        else 0
    )

    selected_label = st.sidebar.radio(
        label="",
        options=thread_labels,
        index=current_index
    )

    selected_thread_id = label_to_thread[selected_label]

    if selected_thread_id != st.session_state['thread_id']:
        st.session_state['thread_id'] = selected_thread_id
        messages = load_conversation(selected_thread_id)
        st.session_state['message_history'] = [
            {
                "role": "user" if isinstance(m, HumanMessage) else "assistant",
                "content": m.content
            }
            for m in messages
        ]


# ****************************************
# Main Chat UI
# ****************************************

for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type here")

if user_input:

    # Create thread lazily if none exists
    if st.session_state['thread_id'] is None:
        reset_chat()

    st.session_state['message_history'].append(
        {"role": "user", "content": user_input}
    )

    # Update sidebar title
    st.session_state['thread_titles'][st.session_state['thread_id']] = user_input[:40]

    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }

    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            chunk.content
            for chunk, _ in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            )
            if isinstance(chunk, AIMessage)
        )

    st.session_state['message_history'].append(
        {"role": "assistant", "content": ai_message}
    )


# import streamlit as st
# from langgraph_backend_db import chatbot, retrieve_all_threads
# from langchain_core.messages import HumanMessage
# import uuid

# # **************************************** utility functions *************************

# def generate_thread_id():
#     thread_id = uuid.uuid4()
#     return thread_id

# def reset_chat():
#     thread_id = generate_thread_id()
#     st.session_state['thread_id'] = thread_id
#     add_thread(st.session_state['thread_id'])
#     st.session_state['message_history'] = []

# def add_thread(thread_id):
#     if thread_id not in st.session_state['chat_threads']:
#         st.session_state['chat_threads'].append(thread_id)

# def load_conversation(thread_id):
#     state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
#     # Check if messages key exists in state values, return empty list if not
#     return state.values.get('messages', [])


# # **************************************** Session Setup ******************************
# if 'message_history' not in st.session_state:
#     st.session_state['message_history'] = []

# if 'thread_id' not in st.session_state:
#     st.session_state['thread_id'] = generate_thread_id()

# if 'chat_threads' not in st.session_state:
#     st.session_state['chat_threads'] = retrieve_all_threads()

# add_thread(st.session_state['thread_id'])


# # **************************************** Sidebar UI *********************************

# st.sidebar.title('LangGraph Chatbot')

# if st.sidebar.button('New Chat'):
#     reset_chat()

# st.sidebar.header('My Conversations')

# for thread_id in st.session_state['chat_threads'][::-1]:
#     if st.sidebar.button(str(thread_id)):
#         st.session_state['thread_id'] = thread_id
#         messages = load_conversation(thread_id)

#         temp_messages = []

#         for msg in messages:
#             if isinstance(msg, HumanMessage):
#                 role='user'
#             else:
#                 role='assistant'
#             temp_messages.append({'role': role, 'content': msg.content})

#         st.session_state['message_history'] = temp_messages


# # **************************************** Main UI ************************************

# # loading the conversation history
# for message in st.session_state['message_history']:
#     with st.chat_message(message['role']):
#         st.text(message['content'])

# user_input = st.chat_input('Type here')

# if user_input:

#     # first add the message to message_history
#     st.session_state['message_history'].append({'role': 'user', 'content': user_input})
#     with st.chat_message('user'):
#         st.text(user_input)

#     #CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

#     CONFIG = {
#         "configurable": {"thread_id": st.session_state["thread_id"]},
#         "metadata": {
#             "thread_id": st.session_state["thread_id"]
#         },
#         "run_name": "chat_turn",
#     }

#     # first add the message to message_history
#     with st.chat_message('assistant'):

#         ai_message = st.write_stream(
#             message_chunk.content for message_chunk, metadata in chatbot.stream(
#                 {'messages': [HumanMessage(content=user_input)]},
#                 config= CONFIG,
#                 stream_mode= 'messages'
#             )
#         )

#     st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})