from typing import TypedDict, Annotated, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
llm = ChatOpenAI(model="gpt-5")

# @tool
# def calculator(first_num:float, second_num: float, operation: str)-> dict:
#     """
#     perform a basic arithmatic operation on two numbers.
#     Supported operations: add, sub, mul, div
#     """
#     try:
#         if operation == "add":
#             result = first_num + second_num
#         elif operation == "sub":
#             result = first_num - second_num
#         elif operation == "mul":
#             result = first_num * second_num
#         elif operation == "div":
#             if second_num == 0:
#                 return{"error":"Division by zero is not allowed"}
#             result = first_num / second_num
#         else:
#             return{"error":f"Unsupported operation '{operation}'"}
        
#         return {"first_num":first_num, "second_num":second_num,"operation":operation,"result":result}
    
#     except Exception as e:
#         return {"error":str(e)}


client = MultiServerMCPClient(
    {
        "arith":{
            "transport":"stdio",
            "command":"python",
            "args":["C:/Users/Lenovo/OneDrive/Documents/Chatbot-In-Langgraph/Chatbot-In-Langgraph/MCP_server.py"]
        },
        "expense":{
            "transport":"streamable_http",
            "url":"https://splendid-gold-dingo.fastmcp.app/mcp"
        }
    }
)
    

# tools = [calculator]

# llm_with_tools = llm.bind_tools(tools)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]

async def build_graph():
    tools = await client.get_tools()
    # print(tools)
    llm_with_tools = llm.bind_tools(tools)

    async def chat_node(state:ChatState):
        messages = state["messages"]
        response =await llm_with_tools.ainvoke(messages)
        return {'messages':[response]}
    
    tool_node = ToolNode(tools)

    graph = StateGraph(ChatState)

    graph.add_node("chat_node",chat_node)
    graph.add_node("tools",tool_node)

    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge("tools","chat_node")

    chatbot = graph.compile()

    return chatbot

async def main():
    chatbot = await build_graph()

    # result =await chatbot.ainvoke({"messages":[HumanMessage(content="Find the sum of 130 and 23 and give the answer like a cricket commentator.")]})
    # result =await chatbot.ainvoke({"messages":[HumanMessage(content="Add an expence - Rs 3000 on Dinner on 10th December")]})
    result =await chatbot.ainvoke({"messages":[HumanMessage(content="give me all my expences for the month of December")]})
    print(result['messages'][-1].content)


if __name__ == '__main__':
    asyncio.run(main())

        




