import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ****************************************
# Utility Functions
# ****************************************

def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []
    st.session_state['thread_summaries'][thread_id] = "New Chat"

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])


# ****************************************
# Session Setup
# ****************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

if 'thread_summaries' not in st.session_state:
    st.session_state['thread_summaries'] = {}

add_thread(st.session_state['thread_id'])

if st.session_state['thread_id'] not in st.session_state['thread_summaries']:
    st.session_state['thread_summaries'][st.session_state['thread_id']] = "New Chat"


# ****************************************
# Sidebar UI
# ****************************************

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("➕ New Chat"):
    reset_chat()

st.sidebar.divider()
st.sidebar.subheader("My Conversations")

# Create labels for radio buttons
thread_labels = [
    st.session_state['thread_summaries'].get(tid, "New Chat")
    for tid in st.session_state['chat_threads']
]

# Map label -> thread_id
label_to_thread = dict(zip(thread_labels, st.session_state['chat_threads']))

# Currently selected index
current_index = st.session_state['chat_threads'].index(
    st.session_state['thread_id']
)

# Radio button (auto-highlighted by Streamlit)
selected_label = st.sidebar.radio(
    label="",
    options=thread_labels,
    index=current_index
)

selected_thread_id = label_to_thread[selected_label]

# Load selected conversation
if selected_thread_id != st.session_state['thread_id']:
    st.session_state['thread_id'] = selected_thread_id
    messages = load_conversation(selected_thread_id)

    temp_messages = []
    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        temp_messages.append({"role": role, "content": msg.content})

    st.session_state['message_history'] = temp_messages


# ****************************************
# Main Chat UI
# ****************************************

for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    # Store user message
    st.session_state['message_history'].append(
        {"role": "user", "content": user_input}
    )

    # Update thread title (last question)
    st.session_state['thread_summaries'][st.session_state['thread_id']] = user_input[:40]

    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {"configurable": {"thread_id": st.session_state['thread_id']}}

    with st.chat_message("assistant"):

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append(
        {"role": "assistant", "content": ai_message}
    )




# import streamlit as st
# from langgraph_backend import chatbot
# from langchain_core.messages import HumanMessage, AIMessage
# import uuid

# # ****************************************
# # Utility Functions
# # ****************************************

# def generate_thread_id():
#     return uuid.uuid4()

# def add_thread(thread_id):
#     if thread_id not in st.session_state['chat_threads']:
#         st.session_state['chat_threads'].append(thread_id)

# def reset_chat():
#     thread_id = generate_thread_id()
#     st.session_state['thread_id'] = thread_id
#     add_thread(thread_id)
#     st.session_state['message_history'] = []
#     st.session_state['thread_summaries'][thread_id] = "New Chat"

# def load_conversation(thread_id):
#     state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
#     return state.values.get('messages', [])


# # ****************************************
# # Session Setup
# # ****************************************

# if 'message_history' not in st.session_state:
#     st.session_state['message_history'] = []

# if 'thread_id' not in st.session_state:
#     st.session_state['thread_id'] = generate_thread_id()

# if 'chat_threads' not in st.session_state:
#     st.session_state['chat_threads'] = []

# if 'thread_summaries' not in st.session_state:
#     st.session_state['thread_summaries'] = {}

# add_thread(st.session_state['thread_id'])

# if st.session_state['thread_id'] not in st.session_state['thread_summaries']:
#     st.session_state['thread_summaries'][st.session_state['thread_id']] = "New Chat"


# # ****************************************
# # Sidebar UI
# # ****************************************

# st.sidebar.title("LangGraph Chatbot")

# if st.sidebar.button("➕ New Chat"):
#     reset_chat()

# st.sidebar.divider()
# st.sidebar.subheader("My Conversations")

# for thread_id in reversed(st.session_state['chat_threads']):
#     label = st.session_state['thread_summaries'].get(thread_id, "New Chat")

#     is_active = thread_id == st.session_state['thread_id']
#     icon = "🟢" if is_active else "⚪"

#     if st.sidebar.button(f"{icon} {label}", key=str(thread_id)):
#         st.session_state['thread_id'] = thread_id
#         messages = load_conversation(thread_id)

#         temp_messages = []
#         for msg in messages:
#             role = "user" if isinstance(msg, HumanMessage) else "assistant"
#             temp_messages.append({"role": role, "content": msg.content})

#         st.session_state['message_history'] = temp_messages


# # ****************************************
# # Main Chat UI
# # ****************************************

# for message in st.session_state['message_history']:
#     with st.chat_message(message["role"]):
#         st.text(message["content"])

# user_input = st.chat_input("Type your message...")

# if user_input:
#     # Store user message
#     st.session_state['message_history'].append(
#         {"role": "user", "content": user_input}
#     )

#     # Update sidebar thread label (last user question)
#     st.session_state['thread_summaries'][st.session_state['thread_id']] = user_input[:40]

#     with st.chat_message("user"):
#         st.text(user_input)

#     CONFIG = {"configurable": {"thread_id": st.session_state['thread_id']}}

#     with st.chat_message("assistant"):

#         def ai_only_stream():
#             for message_chunk, metadata in chatbot.stream(
#                 {"messages": [HumanMessage(content=user_input)]},
#                 config=CONFIG,
#                 stream_mode="messages",
#             ):
#                 if isinstance(message_chunk, AIMessage):
#                     yield message_chunk.content

#         ai_message = st.write_stream(ai_only_stream())

#     # Store assistant response
#     st.session_state['message_history'].append(
#         {"role": "assistant", "content": ai_message}
#     )


# import streamlit as st
# from langgraph_backend import chatbot
# from langchain_core.messages import HumanMessage, AIMessage
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
#     st.session_state['chat_threads'] = []

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

#     CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

#      # first add the message to message_history
#     with st.chat_message("assistant"):
#         def ai_only_stream():
#             for message_chunk, metadata in chatbot.stream(
#                 {"messages": [HumanMessage(content=user_input)]},
#                 config=CONFIG,
#                 stream_mode="messages"
#             ):
#                 if isinstance(message_chunk, AIMessage):
#                     # yield only assistant tokens
#                     yield message_chunk.content

#         ai_message = st.write_stream(ai_only_stream())

#     st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})