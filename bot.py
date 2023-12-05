import asyncio
import aiofiles

from aiogram import types, executor
from aiogram.dispatcher import FSMContext

from datetime import datetime

from src.common import bot, dp
from src.constants import WHICH_COURSE_FILE
from src.database import db
from src.utils import UserStates, kbs


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    await message.answer("Приветствую!\n\nНа каком вы курсе?")
    await state.set_state(UserStates.which_course.state)


@dp.message_handler(state=UserStates.which_course)
async def on_which_course_user(message: types.Message, state: FSMContext):
    async with aiofiles.open(WHICH_COURSE_FILE, 'a') as f:
        current_time = datetime.now().strftime('%d.%m.%Y, %H:%M:%S')
        await f.write(f'{current_time} | ID={message.from_user.id}: {message.text}\n=================\n')

    await message.answer("Благодарю!\nДля продолжения нажмите кнопку ниже ⬇️", reply_markup=kbs.task_reqs_kb)
    await state.set_state(UserStates.task_reqs.state)


@dp.message_handler(lambda message: message.text == "Условие задачи", state=UserStates.task_reqs)
async def get_task_reqs(message: types.Message, state: FSMContext):
    task = await db.get_random_task()
    await message.answer_photo(task.conditions,  # Conditions is telegram photo id
                               caption='Условие задачи ⬆️', reply_markup=kbs.get_solution_kb)
    await state.set_data({'task_id': task.id})
    await state.set_state(UserStates.get_solution.state)


@dp.message_handler(lambda message: message.text == "Обсудить решение", state=UserStates.get_solution)
async def get_solution(message: types.Message, state: FSMContext):
    task_id = (await state.get_data())['task_id']
    task = await db.get_task_by_id(task_id)

    if task.solution is None:
        await message.answer_photo(task.picture, reply_markup=kbs.where_research_it_kb)

    else:
        await message.answer_photo(task.solution,  # Solution is telegram photo id
                                   caption='Решение ⬆️')
        await asyncio.sleep(1.5)
        await message.answer_photo(task.picture, reply_markup=kbs.where_research_it_kb)
    await state.set_state(UserStates.where_research_it.state)


@dp.message_handler(lambda message: message.text == "Где такое исследуют?", state=UserStates.where_research_it)
async def where_research_it(message: types.Message, state: FSMContext):
    task_id = (await state.get_data())['task_id']
    task = await db.get_task_by_id(task_id)
    await message.answer(task.where_it_research, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp)
