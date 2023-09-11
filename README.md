# Kwork Telegram Notifier

Kwork Telegram Notifier is a Python script designed to periodically fetch new projects from [Kwork.ru](kwork.ru) and notify a Telegram group about them. It uses the Kwork API to retrieve project details and sends notifications to a specified Telegram group.

## Features

- Fetches new projects from [Kwork.ru](kwork.ru) based on specified categories.
- Sends project notifications to a Telegram group.
- Uses the Apscheduler library for job scheduling.
- Stores project IDs in an SQLite database to avoid duplicate notifications.

## Requirements

- Python 3.6 or higher
- Dependencies listed in `requirements.txt`
- A Telegram Bot Token (obtain one from @BotFather on Telegram)
- [Kwork.ru](kwork.ru) account credentials (LOGIN, PASSWORD, PHONE_LAST)
- SQLite database for storing project IDs (default: `projects.db`)
- Configuration via environment variables (see `.env` file)

## Installation

1. Clone this repository:

   ```shell
   git clone https://github.com/hoosnick/kwork-projects-parser.git
   cd kwork-projects-parser
   ```

2. Install the required dependencies using pip:

   ```shell
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory and add your environment variables:

   ```
   TG_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   TG_GROUP=YOUR_TELEGRAM_GROUP_ID
   TG_TOPIC_ID=YOUR_TELEGRAM_TOPIC_ID

   LOGIN=YOUR_KWORK_LOGIN
   PASSWORD=YOUR_KWORK_PASSWORD
   PHONE_LAST=YOUR_KWORK_PHONE_LAST
   ```

4. Run the script:
   ```shell
   python main.py
   ```

## Usage

The script fetches new projects from [Kwork.ru](kwork.ru) at regular intervals (default: every 10 minutes) based on specified categories. When a new project is found, it sends a notification to the Telegram group with project details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
