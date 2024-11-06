from typing import Annotated, TypedDict, List
from langgraph.graph.message import add_messages
from .models import SimpleTask

def add_tasks(left: List[SimpleTask], right: List[SimpleTask]) -> List[SimpleTask]:
    """Custom reducer for tasks that handles merging by ID"""
    if not left:
        left = []
    if not right:
        right = []

    tasks_by_id = {task.id: task for task in left}

    for task in right:
        tasks_by_id[task.id] = task

    return list(tasks_by_id.values())

class State(TypedDict):
    msgs: Annotated[list, add_messages]
    tasks: Annotated[List[SimpleTask], add_tasks] 