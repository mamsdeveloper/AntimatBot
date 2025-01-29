import logging
import traceback

from aiogram import Router
from aiogram.types.error_event import ErrorEvent

logger = logging.getLogger(__name__)

router = Router()


@router.errors()
async def errors_handler(event: ErrorEvent):
    logger.error(f'Error processing update [{event.update}]: {event.exception}')
    logger.error(''.join(traceback.format_exception(event.exception)))
