import sys
sys.path.insert(0, "/Users/brassfieldventuresllc/.hermes/hermes-agent")

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
import operator

class TestState(TypedDict):
    items: list[str]
    results: Annotated[list[str], operator.add]
    __budget_spent: float
    __current_node: str

def node1(state: TestState):
    print(f"node1 state keys: {list(state.keys())}")
    print(f"node1 __budget_spent: {state.get('__budget_spent')}")
    return {"__budget_spent": 0.5, "__current_node": "node1", "results": ["a"]}

def node2(state: TestState):
    print(f"node2 state keys: {list(state.keys())}")
    print(f"node2 __budget_spent: {state.get('__budget_spent')}")
    return {"__budget_spent": 1.0, "__current_node": "node2", "results": ["b"]}

builder = StateGraph(TestState)
builder.add_node("n1", node1)
builder.add_node("n2", node2)
builder.add_edge(START, "n1")
builder.add_edge("n1", "n2")
builder.add_edge("n2", END)

graph = builder.compile()
result = graph.invoke({"items": ["x"], "results": [], "__budget_spent": 0.0, "__current_node": ""})
print(f"Result keys: {list(result.keys())}")
print(f"Result: {result}")
