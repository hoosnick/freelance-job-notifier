# Freelance Jobs Telegram Notifier

Freelance Jobs Notifier is a Python script designed to periodically fetch new projects from popular freelance platforms (at the moment: [Kwork.ru](https://kwork.ru) and [Upwork.com](https://upwork.com)) and notify a Telegram group about them. It uses the API, RSS Feed to retrieve project details and sends notifications to a specified Telegram group.

https://github.com/hoosnick/freelance-job-notifier/assets/73847672/5dd67ffd-cd27-49c0-8a2a-8bee4c38184e

---

## 🍰 Features

#### [Jan 15, 2024]

- Now you can generate an offer from the description of each job with the help of AI.
- User friendly Telegram Web App to view the generated offers.
- PremiumUsers, Unlimited Generates and etc.

#### [Sep 12, 2023]

- Fetches new [project/job]s based on specified categories.
- Sends project notifications to a Telegram group.
- Uses the Apscheduler library for job scheduling.
- Stores project IDs in an SQLite database to avoid duplicate notifications.

---

## ⚙️ Requirements

- Python 3.11 or higher
- Dependencies listed in `requirements.txt`
- A Telegram Bot Token (obtain one from @BotFather on Telegram)
- For [Kwork.ru](https://kwork.ru) - account credentials (LOGIN, PASSWORD, PHONE_LAST, CATEGORIES). You can find a complete list of project categories in the [assets/kwork-categories.json](assets/kwork-categories.json) file to further search for projects by their ID. (see `.env` file)
- For [Upwork.com](https://upwork.com) - log in to your account and create a search query for jobs by following this [link](https://www.upwork.com/nx/jobs/search) and get the credentials from the query parameters in the rss feed url that was generated for you. (see `.env` file)
- Configuration via environment variables (see `.env` file)

---

## 💽 Installation

1. Clone this repository:

   ```shell
   git clone https://github.com/hoosnick/freelance-job-notifier.git
   ```

   ```shell
   cd freelance-job-notifier
   ```

2. Install the required dependencies using pip:

   ```shell
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory and add your environment variables from [.sample.env](.sample.env) file.

4. Run the script:
   ```shell
   python -m app
   ```

---

## ❤️ Thanks a lot

- [@kesha1225](https://github.com/kesha1225) for [pykwork](https://github.com/kesha1225/pykwork)
- [Contributors of G4F](https://github.com/xtekky/gpt4free/graphs/contributors) for [gpt4free](https://github.com/xtekky/gpt4free)

---

## 📃 License

- This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a href="https://www.buymeacoffee.com/hoosnick" target="_blank"><img alt="Buy Me A Coffee" height="41" width="174" src="https://github.com/hoosnick/freelance-job-notifier/assets/73847672/79a76ef6-a9f8-4c26-bd7d-72bc8048eb25"></a>
