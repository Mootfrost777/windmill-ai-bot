from typing import Callable, Dict, Any, Awaitable

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ContentType, TelegramObject, FSInputFile
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.db import async_session
from app.dependencies import get_session
from app.config import config
from aiogram import BaseMiddleware

from app.ml import predict
from app.models import Task, Result
from datetime import datetime

bot = Bot(config.token)
dp = Dispatcher()


class DatabaseSessionMiddleware(BaseMiddleware):

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        async with async_session() as session:
            data['session'] = session
            return await handler(event, data)


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Meow meow!")


@dp.message(F.content_type == ContentType.PHOTO)
async def photo(msg: Message, session: AsyncSession):
    img_uuid = uuid.uuid4()
    await bot.download(msg.photo[-1], destination=f'{config.images_dir}/{img_uuid}.jpg')
    task = Task(image_uuid=img_uuid, user_id=msg.from_user.id, timestamp=datetime.now())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    await msg.answer("Task created!")


@dp.message(Command("execall"))
async def exec_all(msg: Message, session: AsyncSession):
    # tasks = await session.execute(
    #     select(Task).where(Task.user_id == msg.from_user.id and Task.results is None)
    # )
    # tasks = tasks.scalars().all()
    result_alias = aliased(Result)
    tasks = await session.execute(
        select(Task)
        .outerjoin(result_alias, Task.id == result_alias.task_id).where(result_alias.id == None)
        .where(Task.user_id == msg.from_user.id)
    )
    tasks = tasks.scalars().all()

    if not tasks:
        return await msg.answer("No unprocessed tasks")

    results = predict([x.image_uuid for x in tasks])
    for task, result in zip(tasks, results):
        session.add(Result(result=result[1], task_id=task.id))
        ph = FSInputFile(f'{config.images_dir}/{result[0]}.jpg')
        await msg.answer_photo(ph, f'Image {result[0]} classified as {result[1]}!')
    await session.commit()


dp.message.middleware(DatabaseSessionMiddleware())