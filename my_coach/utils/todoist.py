from typing import List, Optional, Dict, Any
import os
import httpx
from dotenv import load_dotenv
import json
import uuid
import logging
from ..models import Task, Project, SimpleTask
from .logging_setup import setup_logging

# Initialize module logger
logger = logging.getLogger(__name__)

class TodoistClient:
    RESOURCE_ITEMS = "items"
    RESOURCE_PROJECTS = "projects"
    RESOURCE_ALL = "all"

    def __init__(self):
        self.logger = logger.getChild('TodoistClient')
        self.logger.info("Initializing TodoistClient")
        self.api_token = os.getenv("TODOIST_API_TOKEN")
        if not self.api_token:
            self.logger.critical("TODOIST_API_TOKEN not found in environment variables")
            raise ValueError("TODOIST_API_TOKEN must be set in environment variables")

        self.base_url = "https://api.todoist.com/sync/v9"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        self.sync_token = "*"
        self.logger.info("TodoistClient initialized successfully")

    async def sync(self, resource_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Perform a sync operation with Todoist"""
        self.logger.debug(f"Starting sync operation for resources: {resource_types}")
        try:
            data = {
                "sync_token": self.sync_token,
                "resource_types": json.dumps(resource_types)
                if resource_types
                else json.dumps(["all"]),
            }

            async with httpx.AsyncClient() as client:
                self.logger.debug("Making sync API request")
                response = await client.post(
                    f"{self.base_url}/sync", headers=self.headers, data=data
                )
                response.raise_for_status()
                result = response.json()

                self.sync_token = result.get("sync_token", self.sync_token)
                self.logger.info("Sync operation completed successfully")
                self.logger.debug(f"New sync token: {self.sync_token}")
                return result

        except httpx.HTTPError as e:
            self.logger.error(
                "HTTP error during sync operation",
                exc_info=True,
                extra={
                    "status_code": getattr(getattr(e, "response", None), "status_code", None),
                    "resource_types": resource_types
                }
            )
            raise
        except Exception as e:
            self.logger.error(
                "Unexpected error during sync operation",
                exc_info=True,
                extra={"resource_types": resource_types}
            )
            raise

    async def get_tasks(self) -> List[SimpleTask]:
        """Get all active tasks using Todoist Sync API"""
        self.logger.info("Fetching all active tasks")
        try:
            sync_data = await self.sync([self.RESOURCE_ITEMS])
            items = sync_data.get("items", [])
            self.logger.debug(f"Retrieved {len(items)} items from sync")

            tasks = []
            for item in items:
                try:
                    task = await self._convert_item_to_task(item)
                    tasks.append(
                        SimpleTask(
                            id=task.id,
                            content=task.content,
                            description=task.description,
                            priority=task.priority,
                            is_completed=task.is_completed,
                            due=task.due,
                            labels=task.labels,
                        )
                    )
                except Exception as e:
                    self.logger.error(
                        "Error converting item to task",
                        exc_info=True,
                        extra={
                            "item_id": item.get("id"),
                            "content": item.get("content", "")[:100]
                        }
                    )

            self.logger.info(f"Successfully processed {len(tasks)} tasks")
            return tasks

        except Exception as e:
            self.logger.error("Failed to fetch tasks", exc_info=True)
            raise

    async def add_task(
        self,
        content: str,
        project_id: Optional[str] = None,
        section_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        labels: Optional[List[str]] = None,
        priority: Optional[int] = None,
        due_string: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Task:
        """Add a new task using sync API with extended options"""
        self.logger.info("Adding new task")
        self.logger.debug(f"Task content: {content[:100]}...")
        
        temp_id = str(uuid.uuid4())
        
        # Build args dictionary with all optional parameters
        args = {
            "content": content,
            **({"project_id": project_id} if project_id else {}),
            **({"section_id": section_id} if section_id else {}),
            **({"parent_id": parent_id} if parent_id else {}),
            **({"labels": labels} if labels else {}),
            **({"priority": priority} if priority else {}),
            **({"due_string": due_string} if due_string else {}),
            **({"description": description} if description else {}),
        }
        
        self.logger.debug(f"Task arguments: {args}")

        commands = [
            {
                "type": "item_add",
                "temp_id": temp_id,
                "uuid": str(uuid.uuid4()),
                "args": args,
            }
        ]

        try:
            data = {"commands": json.dumps(commands)}
            async with httpx.AsyncClient() as client:
                self.logger.debug("Sending task creation request")
                response = await client.post(
                    f"{self.base_url}/sync", headers=self.headers, data=data
                )
                response.raise_for_status()
                result = response.json()

                if "temp_id_mapping" in result:
                    task_id = result["temp_id_mapping"].get(temp_id)
                    if task_id:
                        self.logger.debug(f"Task created with ID: {task_id}")
                        # Get updated task data
                        sync_data = await self.sync(["items"])
                        for item in sync_data.get("items", []):
                            if item["id"] == task_id:
                                task = await self._convert_item_to_task(item)
                                self.logger.info(f"Successfully created task: {task_id}")
                                return task

                self.logger.error("Failed to create task - no task ID returned")
                raise Exception("Failed to create task")
                
        except Exception as e:
            self.logger.error(
                "Error adding task",
                exc_info=True,
                extra={
                    "content": content[:100],
                    "project_id": project_id
                }
            )
            raise

    async def close_task(self, task_id: str) -> bool:
        """Close a task using sync API"""
        self.logger.info(f"Closing task: {task_id}")
        
        commands = [
            {"type": "item_close", "uuid": str(uuid.uuid4()), "args": {"id": task_id}}
        ]

        try:
            data = {"commands": json.dumps(commands)}
            
            async with httpx.AsyncClient() as client:
                self.logger.debug("Sending task close request")
                response = await client.post(
                    f"{self.base_url}/sync", headers=self.headers, data=data
                )
                response.raise_for_status()
                result = response.json()
                
                success = all(
                    status.get("error") is None
                    for status in result.get("sync_status", {}).values()
                )
                
                if success:
                    self.logger.info(f"Successfully closed task: {task_id}")
                else:
                    self.logger.warning(f"Failed to close task: {task_id}")
                    
                return success
                
        except Exception as e:
            self.logger.error(
                "Error closing task",
                exc_info=True,
                extra={"task_id": task_id}
            )
            raise

    async def get_projects(self) -> List[Project]:
        """Get all projects"""
        self.logger.info("Fetching all projects")
        try:
            sync_data = await self.sync(["projects"])
            projects_data = sync_data.get("projects", [])
            self.logger.debug(f"Retrieved {len(projects_data)} projects")
            
            projects = []
            for project in projects_data:
                try:
                    project_data = {
                        "id": project["id"],
                        "name": project["name"],
                        "color": project.get("color", ""),
                        "parent_id": project.get("parent_id"),
                        "order": project.get("order", 0),
                        "comment_count": project.get("comment_count", 0),
                        "is_shared": project.get("shared", False),
                        "is_favorite": project.get("is_favorite", False),
                        "is_inbox_project": project.get("is_inbox_project", False),
                        "is_team_inbox": project.get("is_team_inbox", False),
                        "view_style": project.get("view_style", "list"),
                        "url": project.get("url", ""),
                        "can_assign_tasks": project.get("can_assign_tasks", False),
                    }
                    projects.append(Project(**project_data))
                except Exception as e:
                    self.logger.error(
                        "Error processing project data",
                        exc_info=True,
                        extra={
                            "project_id": project.get("id"),
                            "project_name": project.get("name")
                        }
                    )
                    
            self.logger.info(f"Successfully processed {len(projects)} projects")
            return projects
            
        except Exception as e:
            self.logger.error("Failed to fetch projects", exc_info=True)
            raise

    async def _convert_item_to_task(self, item: Dict[str, Any]) -> Task:
        """Helper method to convert an item dict to a Task object"""
        self.logger.debug(f"Converting item to task: {item.get('id')}")
        try:
            task_data = {
                "id": item["id"],
                "content": item["content"],
                "description": item.get("description", ""),
                "project_id": item["project_id"],
                "priority": item["priority"],
                "assignee_id": item.get("responsible_uid"),
                "assigner_id": item.get("assigned_by_uid"),
                "comment_count": item.get("comment_count", 0),
                "is_completed": item.get("checked", False),
                "created_at": item.get("added_at", ""),
                "creator_id": item.get("added_by_uid", ""),
                "order": item.get("child_order", 0),
                "url": item.get("url", f"https://todoist.com/showTask?id={item['id']}"),
                "duration": None,
                "labels": item.get("labels", []),
                "section_id": item.get("section_id"),
                "parent_id": item.get("parent_id"),
                "sync_id": item.get("sync_id"),
                "due": item.get("due"),
            }
            task = Task(**task_data)
            self.logger.debug(f"Successfully converted item {item['id']} to task")
            return task
            
        except Exception as e:
            self.logger.error(
                "Error converting item to task",
                exc_info=True,
                extra={
                    "item_id": item.get("id"),
                    "content": item.get("content", "")[:100]
                }
            )
            raise
