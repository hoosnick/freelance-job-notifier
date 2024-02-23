from typing import Dict

import g4f

g4f.debug.logging = False
g4f.debug.version_check = False


PROMPT = {
    "ru": "НАПИШИ НА РУССКОМ.\n\n"
          "Проект с фриланс-биржи пойман, пора браться за него. Что предложить? До 800 символов (минимум 150).\n"
          "Представь, что ты фрилансер, хочешь заработать. Думай как фрилансер. Напиши от моего имени (я, мой, моего и т.д.).\n"
          "Опиши, как я собираюсь выполнить задание, выдели ключевые моменты. Не используй сложные слова. Не используй Markdown, просто обычный текст.\n"
          "Вкратце укажи клиенту пару подходящих (стеков, библиотек, решения, технологии) для этого проекта!\n\n"
          "Стартуй предложение услугу (с уважением и уникальный): 'Здравствуйте! Я готов ...'",

    "en": "A project from a freelance platform has been caught, it’s time to take it. What can I offer? Up to 800 characters (minimum 150).\n"
          "Imagine that you are a freelancer and want to make money. Think like a freelancer. Write in my name (I, my, mine, etc.).\n"
          "Describe how I am going to complete the task, highlight the key points. Don't use difficult words. Don't use Markdown just Plain text.\n"
          "Briefly point out to the client a couple of suitable ones (stacks, libraries, solutions, technologies) for this project!\n\n"
          "Start offering a service (respectfully and uniquely): 'Hello! I'm ready ...'"
}


async def generate_offer(project_description: str, lang: str) -> Dict[str, bool | str]:
    try:
        response = await g4f.ChatCompletion.create_async(
            model="gpt-3.5-turbo",
            messages=[
                {"content": PROMPT.get(lang, 'en'), "role": "system"},
                {"role": "user", "content": f"Project: {project_description}"}
            ]
        )
        return {'ok': True, 'response': str(response)}
    except BaseException as e:
        # TODO: Too Long Error Message Issue
        return {'ok': False, 'err': f"{e.__class__.__name__}"}
