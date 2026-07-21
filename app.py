from typing import TypedDict
import os

from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

os.environ["GROQ_API_KEY"] = "Your_API_Key"

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
)

class CodeState(TypedDict):
    user_prompt: str
    research_notes: str
    generated_code: str
    error: str
    corrected_code: str
    retry_count: int

def research_agent(state: CodeState):
    print("🔍 Research Agent Running...")

    prompt = f"""
    Research the following programming task.
    Task:
    {state["user_prompt"]}
    Return:
    - Best approach
    - Libraries to use
    - Important tips
    - Common mistakes
    """

    response = llm.invoke(prompt)

    return {
        "research_notes": response.content
    }

def code_agent(state: CodeState):
    print("💻 Code Agent Running...")

    prompt = f"""
    Using the research below, generate complete Python code.That must contain only 300-400 line of code
    Research:
    {state["research_notes"]}
    Task:
    {state["user_prompt"]}
    Return only Python code.
    """

    response = llm.invoke(prompt)

    return {
        "generated_code": response.content
    }

def checker_agent(state: CodeState):
    print("✅ Checker Agent Running...")

    code = state["generated_code"]

    prompt = f"""
    Check the following Python code.
    If it has errors, explain them briefly.
    If it is correct, reply ONLY with:
    NO_ERROR

    Code:
    {code}
    """

    response = llm.invoke(prompt)
    result = response.content.strip()

    return {
        "error": "" if result == "NO_ERROR" else result
    }

def self_correct_agent(state: CodeState):
    print("🔧 Self Correct Agent Running...")

    prompt = f"""
    Fix the Python code using the error message.
    Error:
    {state["error"]}
    Code:
    {state["generated_code"]}
    Return only the corrected Python code.
    """

    response = llm.invoke(prompt)

    return {
        "generated_code": response.content,
        "corrected_code": response.content,
        "retry_count": state["retry_count"] + 1
    }

def check_result(state: CodeState):
    if state["error"] == "":
        return "success"
    return "retry"

MAX_RETRIES = 3

def route_after_checker(state: CodeState):
    if state["error"] == "":
        return END
    elif state["retry_count"] >= MAX_RETRIES:
        return END
    else:
        return "SelfCorrectAgent"
    

graph = StateGraph(CodeState)

# Nodes
graph.add_node("ResearchAgent", research_agent)
graph.add_node("CodeAgent", code_agent)
graph.add_node("CheckerAgent", checker_agent)
graph.add_node("SelfCorrectAgent", self_correct_agent)

# Edges
graph.add_edge(START, "ResearchAgent")
graph.add_edge("ResearchAgent", "CodeAgent")
graph.add_edge("CodeAgent", "CheckerAgent")

# Conditional Routing
def route_after_checker(state: CodeState):
    if state["error"] == "":
        return END
    return "SelfCorrectAgent"

graph.add_conditional_edges(
    "CheckerAgent",
    route_after_checker,
    {
        END: END,
        "SelfCorrectAgent": "SelfCorrectAgent",
    }
)

# Retry after correction
graph.add_edge("SelfCorrectAgent", "CheckerAgent")

# Compile
workflow = graph.compile()


user_input = input("Enter your coding task: ")

initial_state = {
    "user_prompt": user_input,
    "research_notes": "",
    "generated_code": "",
    "error": "",
    "corrected_code": "",
    "retry_count": 0
}

result = workflow.invoke(initial_state)

print(result["generated_code"])
