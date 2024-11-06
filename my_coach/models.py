from typing import Literal, Optional, List
from pydantic import BaseModel

VIEW_STYLE = Literal["list", "board"]


class Project(BaseModel):
    color: str
    comment_count: int
    id: str
    is_favorite: bool
    is_inbox_project: Optional[bool]
    is_shared: bool
    is_team_inbox: Optional[bool]
    can_assign_tasks: Optional[bool]
    name: str
    order: int
    parent_id: Optional[str]
    url: str
    view_style: VIEW_STYLE


class Section(BaseModel):
    id: str
    name: str
    order: int
    project_id: str


class Due(BaseModel):
    date: str
    is_recurring: bool
    string: str
    datetime: Optional[str] = None
    timezone: Optional[str] = None


class Duration(BaseModel):
    amount: int
    unit: str


class Task(BaseModel):
    assignee_id: Optional[str]
    assigner_id: Optional[str]
    comment_count: int
    is_completed: bool
    content: str
    created_at: str
    creator_id: str
    description: str
    due: Optional[Due]
    id: str
    labels: Optional[List[str]]
    order: int
    parent_id: Optional[str]
    priority: int
    project_id: str
    section_id: Optional[str]
    url: str
    duration: Optional[Duration]
    sync_id: Optional[str] = None


class QuickAddResult(BaseModel):
    task: Task
    resolved_project_name: Optional[str] = None
    resolved_assignee_name: Optional[str] = None
    resolved_label_names: Optional[List[str]] = None
    resolved_section_name: Optional[str] = None


class Collaborator(BaseModel):
    id: str
    email: str
    name: str


class Attachment(BaseModel):
    resource_type: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    file_url: Optional[str] = None
    file_duration: Optional[int] = None
    upload_state: Optional[str] = None
    image: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    url: Optional[str] = None
    title: Optional[str] = None


class Comment(BaseModel):
    attachment: Optional[Attachment]
    content: str
    id: str
    posted_at: str
    project_id: Optional[str]
    task_id: Optional[str]


class Label(BaseModel):
    id: str
    name: str
    color: str
    order: int
    is_favorite: bool


class AuthResult(BaseModel):
    access_token: str
    state: Optional[str]


class Item(BaseModel):
    id: str
    user_id: str
    project_id: str
    content: str
    description: str
    priority: int
    child_order: int
    collapsed: bool
    labels: List[str]
    checked: bool
    is_deleted: bool
    added_at: str
    due: Optional[Due] = None
    parent_id: Optional[int] = None
    section_id: Optional[str] = None
    day_order: Optional[int] = None
    added_by_uid: Optional[str] = None
    assigned_by_uid: Optional[str] = None
    responsible_uid: Optional[str] = None
    sync_id: Optional[str] = None
    completed_at: Optional[str] = None


class ItemCompletedInfo(BaseModel):
    item_id: str
    completed_items: int


class CompletedItems(BaseModel):
    items: List[Item]
    total: int
    completed_info: List[ItemCompletedInfo]
    has_more: bool
    next_cursor: Optional[str] = None


class SimpleTask(BaseModel):
    """Simplified task model for agent state management"""

    id: str
    content: str
    description: str
    priority: int
    is_completed: bool
    due: Optional[Due]
    labels: Optional[List[str]] = None
    timezone: Optional[str] = None


class UserPreferences(BaseModel):
    """User preferences for notifications"""

    user_id: int
    timezone: str = "UTC"
    daily_summary_enabled: bool = True
    daily_summary_time: str = "07:00"
    overdue_reminders_enabled: bool = True
    overdue_check_interval: int = 60  # minutes
