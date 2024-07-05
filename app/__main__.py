import aiorun as aiorun
from app import bot, dp
from app.db import engine
from app.ml import load_model
from app.models import Base


async def main():
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    load_model()
    await dp.start_polling(bot)


if __name__ == "__main__":
    aiorun.run(main(), stop_on_unhandled_errors=True)
