from typing import Iterable
from models import Group, Dictionary

GREETING = 'Привет! Я помогу тебе удалять сообщения со стоп-словами.'

NO_AVAILABLE_GROUPS = 'У вас нет подключенных групп. Обратитесь к администратору бота.'

ASK_WORDS = 'Укажите слова/фразы через запятую:'

SUCCESSFUL_UPDATE_WORDS = 'Слова успешно обновлены'
SUCCESSFUL_DROP_WORDS = 'Словарь успешно очищен'
SUCCESSFUL_REPAIR_WORDS = 'Словарь в исходном состоянии'

DELETE_MESSAGE_REASON = 'Причина: {reason}'

DELETE_MESSAGE_EVENT = '''
Сообщение удалено.
<b>Группа:</b> {title}
<b>Пользователь:</b> {full_name}, https://t.me/{username}
<b>Причина:</b> {reason}
<b>Текст сообщение:</b> 
<code>{text}</code>

<b>Шаблон при ошибке:</b>
<code>
Здравствуйте, уважаемая(ый) {full_name}! 
Бот удалил Ваше сообщение за {reason}, переформулируйте, пожалуйста и опубликуйте вновь.
</code>
'''


STRIKE_MEMBER_EVENT = '''
Пользователь получает бан.
<b>Группа:</b> {title}
<b>Пользователь:</b> {full_name}, https://t.me/{username}
<b>Причина:</b> 3 сообщения со стоп-словами
'''

WEIRD_NAME_RESTRICTED = '''
Пользователь с ником {full_name} забанен, так как его ник не соответствует правилам.
Нажмите на кнопку ниже, чтобы разбанить его и разрешить использовать ник.

<b>Группа:</b> {title}
<b>Пользователь:</b> https://t.me/{username}

<b>Шаблон при ошибке:</b>
<code>

Здравствуйте, уважаемая(ый) {full_name}! 
Бот не разрешил Вам вход в чат за некорректный ник (содержит менее двух букв / содержит арабские буквы / содержит bot). Попробуйте войти в чат снова.
</code>
'''

STRIKES_ENABLED = 'Баны за стоп-слова активированы'
STRIKES_DISABLED = 'Баны за стоп-слова отключены'
ASK_STRIKE_LIMIT = 'Укажите число сообщений со стоп-словами, после которого пользователь должен быть забанен:'
STRIKE_LIMIT_NOT_DIGIT = 'Необходимо ввести число'
STRIKE_LIMIT_UPDATED = 'Лимит бана установлен'

def build_words_list(group_title: str, full_words: Iterable[str], partial_words: Iterable[str]) -> str:
    return f'''
<b>Группа:</b> {group_title}

<b>Полные слова:</b>
{", ".join(full_words)}

<b>Частичные слова:</b>
{", ".join(partial_words)}

'''


ASK_IGNORED_USER = 'Введите полное имя пользователя:'
IGNORED_USERS_UPDATED = 'Список исключений обновлен'


def build_groups_list(groups_and_dicts: list[tuple[Group, Dictionary]]) -> str:
    text = 'Ваши группы:\n'
    for group, dictionary in groups_and_dicts:
        text += '\n- <b>Группа</b>: ' + group.title
        text += '\n  <b>Бан за стоп-слова</b>: ' + ('активирован' if group.strike_mode else 'выключен')
        text += '\n  <b>Кол-во сообщений для бана</b>: ' + str(group.strike_limit)
        text += '\n  <b>Размер словаря</b>: ' + str(len(dictionary.full_words) + len(dictionary.partial_words))
        text += '\n'

    return text


def build_ignored_users_list(group: Group) -> str:
    return f'''
<b>Группа:</b> {group.title}

<b>Пользователи, чьи сообщения не проверяются:</b>
{", ".join(group.ignored_users)}

'''