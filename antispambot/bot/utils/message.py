from aiogram.types import Message


def get_full_text(message: Message) -> str:
    if message.text is not None:
        text = message.text
        if message.entities is not None:
            for entity in message.entities:
                if entity.url is not None:
                    text += '\nlink( {url} )\n'.format(url=entity.url)

    elif message.caption is not None:
        text = message.caption
        if message.caption_entities is not None:
            for entity in message.caption_entities:
                if entity.url is not None:
                    text += '\nlink( {url} )\n'.format(url=entity.url)
    else:
        text = ''

    if message.contact:
        text += '\ncontact( {number} )\n'.format(
            number=message.contact.phone_number
        )

    return text
