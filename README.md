# Personal Development Coach Telegram Bot

## Introduction

The **Personal Development Coach Telegram Bot** is an intelligent assistant designed to help users manage their personal development goals seamlessly through Telegram. Integrated with Todoist, it allows users to track tasks and receive personalized coaching advice powered by advanced AI models.

## Features

- **Task Management:** Sync and manage Todoist tasks directly within Telegram.
- **Personalized Coaching:** Receive tailored advice on goal setting, motivation, and personal growth.
- **Natural Language Processing:** Advanced AI understands and responds to user queries effectively.
- **Real-time Updates:** Get instant feedback and task updates through the Todoist API.
- **User-Friendly Interface:** Simple commands and interactions designed for ease of use.

## Architecture

The bot leverages a modular architecture to ensure scalability and maintainability:

- **Telegram Bot:** Built using Aiogram, handles user interactions and commands.
- **Todoist Client:** Interfaces with the Todoist API to manage tasks and projects.
- **AI Engine:** Powered by LangGraph and LangChain, utilizes OpenAI's GPT models for generating human-like responses.
- **State Management:** Maintains user-specific states and task information for personalized experiences.
- **Logging:** Comprehensive logging for monitoring and debugging purposes.

## Technology Stack

- **Programming Language:** Python
- **Frameworks & Libraries:**
  - [FastAPI](https://fastapi.tiangolo.com/) for asynchronous operations
  - [Aiogram](https://docs.aiogram.dev/en/latest/) for Telegram bot development
  - [LangGraph](https://langgraph.org/) and [LangChain](https://langchain.readthedocs.io/) for AI integrations
  - [Todoist API](https://developer.todoist.com/) for task management
- **Others:**
  - [HTTPX](https://www.python-httpx.org/) for asynchronous HTTP requests
  - [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
  - [APScheduler](https://apscheduler.readthedocs.io/) for scheduling tasks

## Installation

### Prerequisites

- Python 3.8 or higher
- [Git](https://git-scm.com/)
- [Todoist Account](https://todoist.com/)
- [Telegram Account](https://telegram.org/)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/saminkhan1/focuscoach.git
   cd personal-dev-coach-bot   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt   ```

## Configuration

1. **Environment Variables**

   Create a `.env` file in the root directory and add the following variables:

   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TODOIST_API_TOKEN=your_todoist_api_token   ```

   - **TELEGRAM_BOT_TOKEN:** Obtain from [BotFather](https://telegram.me/BotFather) on Telegram.
   - **TODOIST_API_TOKEN:** Get from [Todoist Integration Settings](https://todoist.com/prefs/integrations).

2. **Additional Configuration**

   You can customize other settings such as logging levels or API endpoints by modifying the respective configuration files or environment variables as needed.

## Usage

1. **Start the Bot**

   ```bash
   python telegram_bot.py   ```

   The bot will start polling for messages. Ensure that your environment variables are correctly set.

2. **Interact with the Bot**

   - **/start:** Initialize your session and receive a welcome message.
   - **General Messages:** Ask questions or seek advice on personal development topics.

3. **Task Management Commands**

   - **Add Task:** You can add tasks to your Todoist directly through the bot.
   - **Close Task:** Mark tasks as completed via bot commands.
   - **View Tasks:** Retrieve and view your current tasks.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add some feature"   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature   ```

5. **Open a Pull Request**

   Submit a pull request detailing your changes for review.
