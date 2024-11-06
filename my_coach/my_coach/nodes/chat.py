import logging
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from ..state import State
from ..utils.prompts import system_prompt

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
                    system_prompt,
                ),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="tasks", optional=True)
            ]
        ).partial(
            # Pre-fill system prompt to avoid passing it each time
            system_prompt=system_prompt
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
            task_messages = [
                HumanMessage(content=
                    f"Task: {task.content}\n"
                    f"Priority: {task.priority}\n"
                    f"Due: {task.due.string if task.due else 'No due date'}"
                )
                for task in state["tasks"]
            ]

            # Get chat history excluding the last message
            chat_history = state["msgs"][:-1] if len(state["msgs"]) > 1 else []

            # Generate response with improved context
            logger.debug("Generating AI response")
            resp = await self.chain.ainvoke({
                "input": last_msg.content,
                "chat_history": chat_history,
                "tasks": task_messages
            })
            logger.info("Successfully generated AI response")

            return {"msgs": [resp]}

        except Exception as e:
            logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
            raise
