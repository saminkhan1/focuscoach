import logging
from typing import List
from state import State
from models import SimpleTask

logger = logging.getLogger(__name__)


class GetTasksNode:
    def __init__(self, todoist_client):
        logger.info("Initializing GetTasksNode")
        self.todoist_client = todoist_client

    async def __call__(self, state: State) -> State:
        """Fetch current tasks from Todoist and merge with existing tasks"""
        logger.debug("Fetching and merging Todoist tasks")
        try:
            existing_tasks = state.get("tasks", [])
            logger.debug(f"Found {len(existing_tasks)} existing tasks")

            updates = await self.todoist_client.get_tasks()
            logger.debug(
                f"Received {len(updates) if updates else 0} task updates from Todoist"
            )

            if not updates:
                logger.info(
                    "No updates received from Todoist, returning existing state"
                )
                return state

            # Merge tasks
            tasks_by_id = {task.id: task for task in existing_tasks}
            logger.debug("Merging tasks with updates")

            for update in updates:
                tasks_by_id[update.id] = update

            merged_tasks = list(tasks_by_id.values())
            logger.info(f"Successfully merged tasks. Total tasks: {len(merged_tasks)}")

            return {"msgs": state.get("msgs", []), "tasks": merged_tasks}

        except Exception as e:
            logger.error("Error fetching/merging Todoist tasks", exc_info=True)
            # Re-raise the exception after logging
            raise
