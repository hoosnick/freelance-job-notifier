# Kwork Telegram Notifier

Kwork Telegram Notifier is a Python script designed to periodically fetch new projects from popular freelance platforms (at the moment: [Kwork.ru](https://kwork.ru) and [Upwork.com](https://upwork.com)) and notify a Telegram group about them. It uses the API, RSS Feed to retrieve project details and sends notifications to a specified Telegram group.

## Features

- Fetches new [project/job]s based on specified categories.
- Sends project notifications to a Telegram group.
- Uses the Apscheduler library for job scheduling.
- Stores project IDs in an SQLite database to avoid duplicate notifications.

## Requirements

- Python 3.9 or higher
- Dependencies listed in `requirements.txt`
- A Telegram Bot Token (obtain one from @BotFather on Telegram)
- For [Kwork.ru](https://kwork.ru) - account credentials (LOGIN, PASSWORD, PHONE_LAST, CATEGORIES). You can find a complete list of project categories in the [assets/kwork-categories.json](assets/kwork-categories.json) file to further search for projects by their ID. (see `.env` file)
- For [Upwork.com](https://upwork.com) - log in to your account and create a search query for jobs by following this [link](https://www.upwork.com/nx/jobs/search) and get the credentials from the query parameters in the rss feed url that was generated for you. (see `.env` file)
- SQLite database for storing project IDs (default: `projects.db`)
- Configuration via environment variables (see `.env` file)

## Installation

1. Clone this repository:

   ```shell
   git clone https://github.com/hoosnick/freelance-job-parser.git
   cd freelance-job-parser
   ```

2. Install the required dependencies using pip:

   ```shell
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory and add your environment variables:

   ```bash
   # telegram bot/group/topic
   TG_TOKEN=telegram-token
   TG_GROUP=telegram-group-id
   TG_TOPIC_ID=thread/topic-id

   # kwork.ru (credentials for api)
   KW_LOGIN=login
   KW_PASSWORD=password
   KW_PHONE_LAST=phone-last
   KW_CATEGORIES=1,2,3,4,5,6 # category IDs

   # upwork.com (credentials from rss url)
   UP_SECURITYTOKEN=security-token
   UP_USERUID=user-id
   UP_ORGUID=org-id
   UP_QUESTION=(python OR django OR drf) # your search query
   UP_SUBCATEGORIES=None # subcategory IDs or None
   ```

4. Run the script:
   ```shell
   python main.py
   ```

## Usage

The script fetches new projects and jobs at regular intervals based on specified categories. When a new project/job is found, it sends a notification to the Telegram group with project/job details.

## Thanks

Thanks a lot [@kesha1225](https://github.com/kesha1225) for [pykwork](https://github.com/kesha1225/pykwork)! Your work is greatly appreciated!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
