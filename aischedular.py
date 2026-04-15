from typing import TypedDict, Sequence, Annotated, Dict
from langchain.messages import HumanMessage, AIMessage
from langchain.messages import ToolMessage, AnyMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import tkinter as tk
import json
import os
from pydantic import BaseModel, Field, ConfigDict

from gui import ProcessInputApp
from utils import FCFS, PR, RR, SJF, SRTF
from visualize_algo import generate_visualizations

load_dotenv()

# DATA SCHEMA
class Process(BaseModel):
    name: str
    arrival_time: int = Field(..., alias="AT")
    burst_time: int = Field(..., alias="BT")
    priority: int = Field(..., alias="PR")

    model_config = ConfigDict(
        populate_by_name=True
    )

class Processes(BaseModel):
    processes: list[Process]

# AGENT STATE
class AgentState(TypedDict):
    messages: Sequence[AnyMessage]
    process_data: Processes


#tool declaration

def run_scheduler(scheduler, algo: str, processes: Processes):
    scheduler(processes)
    generate_visualizations(algo)

@tool
def round_robin(processes: Processes):
    """This tool makes used to Round Robin Algorithm to schedule processes"""
    run_scheduler(RR, "RR", processes)
    return "Round Robin scheduling completed."

@tool
def priority(processes: Processes):
    """This tool makes used to Priority Algorithm to schedule processes"""
    run_scheduler(PR, "PR", processes)
    return "Priority scheduling completed."

@tool
def shortest_job_first(processes: Processes):
    """This tool makes used to Shortest Job First Algorithm to schedule processes"""
    run_scheduler(SJF, "SJF", processes)
    return "Shortest Job First scheduling completed."

@tool
def shortest_remaining_time_first(processes: Processes):
    """This tool makes used to Shortest Remaining Time First Algorithm to schedule processes"""
    run_scheduler(SRTF, "SRTF", processes)
    return "Shortest Remaining Time First scheduling completed."

@tool
def first_come_first_served(processes: Processes):
    """This tool makes used to First Come First Served Algorithm to schedule processes"""
    run_scheduler(FCFS, "FCFS", processes)
    return "First Come First Served scheduling completed."

tools = [round_robin, priority, shortest_job_first, shortest_remaining_time_first, first_come_first_served]


# LLM settings
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",).bind_tools(tools)


# AGENT NODES

# reading data
def read_data(state: AgentState)->AgentState:
    """
    This node takes process input from users and appends it ot AgentState.

    :param state:
    :return AgentState:
    """

    # GUI LOGIC
    root = tk.Tk()
    app = ProcessInputApp(root)
    root.mainloop()

    with open("data.json") as f:
        data = json.load(f)

        processes = Processes(
            processes=[
                Process(name=name, **values)
                for item in data
                for name, values in item.items()
            ]
        )

        state["process_data"] = processes
    return state

# LLM node
def model_call(state: AgentState)-> AgentState:
    system_prompt = SystemMessage(content="""
You are a CPU scheduling expert.
Given process data, you MUST:
1. Analyze the processes
2. Select the BEST scheduling algorithm
3. CALL the appropriate tool
You MUST call exactly one tool. Do NOT respond with text only.
""")
    # pprint(state['process_data'])
    resp = model.invoke([
        system_prompt,
        HumanMessage(content=state["process_data"].model_dump_json())
    ])

    # pprint(resp)

    state['messages'] = [resp]
    return state

# conditional node
def should_continue(state: AgentState)->str:
    cont = input("Do you have more process batches? [Y/N]").lower()
    while True:
        if cont == "y":
            return "continue"
        elif cont == "n":
            return "end"
        else:
            cont = input("Please enter a valid response [Y/N]").lower()


# graph settings

graph = StateGraph(AgentState)

graph.add_node("read", read_data)
graph.add_edge(START, "read")

graph.add_node("llm", model_call)
graph.add_edge("read", "llm")

tool_node = ToolNode(tools=tools)
graph.add_node("tool_node", tool_node)
graph.add_edge("llm", "tool_node")

graph.add_conditional_edges(
    source="tool_node",
    path=should_continue,
    path_map={
        "continue": "read",
        "end": END,
    }
)

app = graph.compile()

app.invoke({"messages": "hello"})
# print(app.get_graph().draw_mermaid())
