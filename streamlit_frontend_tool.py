import streamlit as st
from langgraph_tool_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid

# ======================================================
# Utilities
# ======================================================

def generate_thread_id():
    return str(uuid.uuid4())

def load_conversation(thread_id):
    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )
    return state.values.get("messages", [])

def get_last_user_question(thread_id):
    for msg in reversed(load_conversation(thread_id)):
        if isinstance(msg, HumanMessage):
            return msg.content[:40]
    return "New Chat"

def reset_chat():
    tid = generate_thread_id()
    st.session_state["thread_id"] = tid
    st.session_state["chat_threads"].insert(0, tid)
    st.session_state["message_history"] = []

# ======================================================
# Session Init
# ======================================================

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = list(
        reversed(retrieve_all_threads())
    )

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = (
        st.session_state["chat_threads"][0]
        if st.session_state["chat_threads"]
        else generate_thread_id()
    )

if "message_history" not in st.session_state:
    msgs = load_conversation(st.session_state["thread_id"])
    st.session_state["message_history"] = [
        {
            "role": "user" if isinstance(m, HumanMessage) else "assistant",
            "content": m.content,
        }
        for m in msgs
    ]

# ======================================================
# Sidebar
# ======================================================

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("➕ New Chat"):
    reset_chat()
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("My Conversations")

for tid in st.session_state["chat_threads"]:
    label = get_last_user_question(tid)
    is_active = tid == st.session_state["thread_id"]

    if st.sidebar.button(
        label,
        key=tid,
        type="primary" if is_active else "secondary",
    ):
        st.session_state["thread_id"] = tid
        msgs = load_conversation(tid)
        st.session_state["message_history"] = [
            {
                "role": "user" if isinstance(m, HumanMessage) else "assistant",
                "content": m.content,
            }
            for m in msgs
        ]
        st.rerun()

# ======================================================
# Main Chat UI
# ======================================================

for msg in st.session_state["message_history"]:
    with st.chat_message(msg["role"]):
        st.text(msg["content"])

user_input = st.chat_input("Type here...")

if user_input:

    tid = st.session_state["thread_id"]

    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {
        "configurable": {"thread_id": tid},
        "metadata": {"thread_id": tid},
    }

    # ==================================================
    # Run graph with Tool status (NO AI streaming)
    # ==================================================

    with st.chat_message("assistant"):

        status_holder = {"box": None}

        for message_chunk, _ in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages",
        ):

            # ✅ TOOL STATUS ONLY
            if isinstance(message_chunk, ToolMessage):
                tool_name = getattr(message_chunk, "name", "tool")
                if status_holder["box"] is None:
                    status_holder["box"] = st.status(
                        f"🔧 Using `{tool_name}` …",
                        expanded=True,
                    )
                else:
                    status_holder["box"].update(
                        label=f"🔧 Using `{tool_name}` …",
                        state="running",
                        expanded=True,
                    )

        if status_holder["box"]:
            status_holder["box"].update(
                label="✅ Tool finished",
                state="complete",
                expanded=False,
            )

    # ==================================================
    # SHOW ONLY FINAL AI MESSAGE
    # ==================================================

    messages = load_conversation(tid)

    final_answer = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            final_answer = msg.content
            break

    with st.chat_message("assistant"):
        st.text(final_answer or "No response generated.")

    # Refresh UI state (NO DUPLICATES)
    st.session_state["message_history"] = [
        {
            "role": "user" if isinstance(m, HumanMessage) else "assistant",
            "content": m.content,
        }
        for m in messages
    ]

    # Move thread to top
    if tid in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].remove(tid)
    st.session_state["chat_threads"].insert(0, tid)


# import streamlit as st
# from langgraph_tool_backend import chatbot, retrieve_all_threads
# from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
# import uuid

# # ======================================================
# # Utilities
# # ======================================================

# def generate_thread_id():
#     return str(uuid.uuid4())

# def load_conversation(thread_id):
#     state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
#     return state.values.get("messages", [])

# def get_last_user_question(thread_id):
#     for msg in reversed(load_conversation(thread_id)):
#         if isinstance(msg, HumanMessage):
#             return msg.content[:40]
#     return "New Chat"

# def reset_chat():
#     tid = generate_thread_id()
#     st.session_state["thread_id"] = tid
#     st.session_state["chat_threads"].insert(0, tid)
#     st.session_state["message_history"] = []

# # ======================================================
# # Session Init
# # ======================================================

# if "chat_threads" not in st.session_state:
#     st.session_state["chat_threads"] = list(
#         reversed(retrieve_all_threads())
#     )

# if "thread_id" not in st.session_state:
#     st.session_state["thread_id"] = (
#         st.session_state["chat_threads"][0]
#         if st.session_state["chat_threads"]
#         else generate_thread_id()
#     )

# if "message_history" not in st.session_state:
#     msgs = load_conversation(st.session_state["thread_id"])
#     st.session_state["message_history"] = [
#         {
#             "role": "user" if isinstance(m, HumanMessage) else "assistant",
#             "content": m.content,
#         }
#         for m in msgs
#     ]

# # ======================================================
# # Sidebar
# # ======================================================

# st.sidebar.title("LangGraph Chatbot")

# if st.sidebar.button("➕ New Chat"):
#     reset_chat()
#     st.rerun()

# st.sidebar.divider()
# st.sidebar.subheader("My Conversations")

# for tid in st.session_state["chat_threads"]:
#     label = get_last_user_question(tid)
#     is_active = tid == st.session_state["thread_id"]

#     if st.sidebar.button(
#         label,
#         key=tid,
#         type="primary" if is_active else "secondary",
#     ):
#         st.session_state["thread_id"] = tid
#         msgs = load_conversation(tid)
#         st.session_state["message_history"] = [
#             {
#                 "role": "user" if isinstance(m, HumanMessage) else "assistant",
#                 "content": m.content,
#             }
#             for m in msgs
#         ]
#         st.rerun()

# # ======================================================
# # Main Chat UI
# # ======================================================

# for msg in st.session_state["message_history"]:
#     with st.chat_message(msg["role"]):
#         st.text(msg["content"])

# user_input = st.chat_input("Type here...")

# if user_input:

#     tid = st.session_state["thread_id"]

#     with st.chat_message("user"):
#         st.text(user_input)

#     CONFIG = {
#         "configurable": {"thread_id": tid},
#         "metadata": {"thread_id": tid},
#     }

#     # 👉 RUN GRAPH (NO STREAMING)
#     chatbot.invoke(
#         {"messages": [HumanMessage(content=user_input)]},
#         config=CONFIG,
#     )

#     # 👉 Reload messages from LangGraph
#     messages = load_conversation(tid)

#     # 👉 Get ONLY last AIMessage
#     final_answer = None
#     for msg in reversed(messages):
#         if isinstance(msg, AIMessage):
#             final_answer = msg.content
#             break

#     with st.chat_message("assistant"):
#         st.text(final_answer or "Sorry, no response generated.")

#     # Update UI state
#     st.session_state["message_history"] = [
#         {
#             "role": "user" if isinstance(m, HumanMessage) else "assistant",
#             "content": m.content,
#         }
#         for m in messages
#     ]

#     # Move active thread to top
#     if tid in st.session_state["chat_threads"]:
#         st.session_state["chat_threads"].remove(tid)
#     st.session_state["chat_threads"].insert(0, tid)




# import streamlit as st
# from langgraph_tool_backend import chatbot, retrieve_all_threads
# from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
# import uuid

# # =========================== Utilities ===========================
# def generate_thread_id():
#     return uuid.uuid4()

# def reset_chat():
#     thread_id = generate_thread_id()
#     st.session_state["thread_id"] = thread_id
#     add_thread(thread_id)
#     st.session_state["message_history"] = []

# def add_thread(thread_id):
#     if thread_id not in st.session_state["chat_threads"]:
#         st.session_state["chat_threads"].append(thread_id)

# def load_conversation(thread_id):
#     state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
#     # Check if messages key exists in state values, return empty list if not
#     return state.values.get("messages", [])

# # ======================= Session Initialization ===================
# if "message_history" not in st.session_state:
#     st.session_state["message_history"] = []

# if "thread_id" not in st.session_state:
#     st.session_state["thread_id"] = generate_thread_id()

# if "chat_threads" not in st.session_state:
#     st.session_state["chat_threads"] = retrieve_all_threads()

# add_thread(st.session_state["thread_id"])

# # ============================ Sidebar ============================
# st.sidebar.title("LangGraph Chatbot")

# if st.sidebar.button("New Chat"):
#     reset_chat()

# st.sidebar.header("My Conversations")
# for thread_id in st.session_state["chat_threads"][::-1]:
#     if st.sidebar.button(str(thread_id)):
#         st.session_state["thread_id"] = thread_id
#         messages = load_conversation(thread_id)

#         temp_messages = []
#         for msg in messages:
#             role = "user" if isinstance(msg, HumanMessage) else "assistant"
#             temp_messages.append({"role": role, "content": msg.content})
#         st.session_state["message_history"] = temp_messages

# # ============================ Main UI ============================

# # Render history
# for message in st.session_state["message_history"]:
#     with st.chat_message(message["role"]):
#         st.text(message["content"])

# user_input = st.chat_input("Type here")

# if user_input:
#     # Show user's message
#     st.session_state["message_history"].append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.text(user_input)

#     CONFIG = {
#         "configurable": {"thread_id": st.session_state["thread_id"]},
#         "metadata": {"thread_id": st.session_state["thread_id"]},
#         "run_name": "chat_turn",
#     }

#     # Assistant streaming block
#     with st.chat_message("assistant"):
#         # Use a mutable holder so the generator can set/modify it
#         status_holder = {"box": None}

#         def ai_only_stream():
#             for message_chunk, metadata in chatbot.stream(
#                 {"messages": [HumanMessage(content=user_input)]},
#                 config=CONFIG,
#                 stream_mode="messages",
#             ):
#                 # Lazily create & update the SAME status container when any tool runs
#                 if isinstance(message_chunk, ToolMessage):
#                     tool_name = getattr(message_chunk, "name", "tool")
#                     if status_holder["box"] is None:
#                         status_holder["box"] = st.status(
#                             f"🔧 Using `{tool_name}` …", expanded=True
#                         )
#                     else:
#                         status_holder["box"].update(
#                             label=f"🔧 Using `{tool_name}` …",
#                             state="running",
#                             expanded=True,
#                         )

#                 # Stream ONLY assistant tokens
#                 if isinstance(message_chunk, AIMessage):
#                     yield message_chunk.content

#         ai_message = st.write_stream(ai_only_stream())

#         # Finalize only if a tool was actually used
#         if status_holder["box"] is not None:
#             status_holder["box"].update(
#                 label="✅ Tool finished", state="complete", expanded=False
#             )

#     # Save assistant message
#     st.session_state["message_history"].append(
#         {"role": "assistant", "content": ai_message}
#     )