import logging
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from state import State

logger = logging.getLogger(__name__)


def create_chat_chain():
    """Create the chat chain with LLM and prompt"""
    logger.debug("Creating chat chain")
    try:
        openai_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an experienced personal development coach with expertise in:
            - Goal setting and achievement
            - Motivation and habit formation
            - Personal growth and self-improvement
            - Career development
            - Work-life balance

            You have access to the user's Todoist tasks. Use this information to:
            - Reference their existing tasks when giving advice
            - Suggest creating new tasks when appropriate
            - Help them prioritize and organize their tasks
            - Celebrate completed tasks

            Current tasks:
            {tasks}

            Your communication style is:
            - Empathetic and supportive
            - Direct but kind
            - Solution-focused
            - Encouraging but realistic

            Always:
            - Ask clarifying questions when needed
            - Provide actionable advice
            - Help break down large goals into manageable steps
            - Encourage reflection and self-awareness
            - Reference specific tasks when relevant to the discussion""",
                ),
                ("human", "{input}"),
            ]
        )

        logger.info("Successfully created chat chain")
        return prompt | openai_llm

    except Exception as e:
        logger.error(f"Failed to create chat chain: {str(e)}", exc_info=True)
        raise


class ChatNode:
    def __init__(self):
        logger.info("Initializing ChatNode")
        self.chain = create_chat_chain()

    async def __call__(self, state: State) -> dict[str, List[BaseMessage]]:
        logger.debug("Processing chat request")
        try:
            # Get the last message
            last_msg = state["msgs"][-1] if state["msgs"] else HumanMessage(content="")
            if not isinstance(last_msg, HumanMessage):
                last_msg = HumanMessage(content=last_msg.content)

            logger.debug(f"Processing message: {last_msg.content[:100]}...")

            # Format tasks
            task_list = "\n".join(
                [
                    f"- {task.content} (Priority: {task.priority}, "
                    f"Due: {task.due.string if task.due else 'No due date'})"
                    for task in state["tasks"]
                ]
            )

            logger.debug(f"Found {len(state['tasks'])} tasks")

            # Generate response
            logger.debug("Generating AI response")
            resp = await self.chain.ainvoke({"input": last_msg, "tasks": task_list})
            logger.info("Successfully generated AI response")

            return {"msgs": [resp]}

        except Exception as e:
            logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
            raise
