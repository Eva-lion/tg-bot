import asyncio
import uuid

from loguru import logger
from pathlib import Path

from src.constants import TASKS_DIR, DATA_DIR
from src.database import Task, async_session


def find_file(file_stem: str, files: list, is_necessarily: bool = True):
    dir_ = DATA_DIR / "new"
    try:
        files.append(list(dir_.rglob(f'{file_stem}.*'))[0])
    except IndexError:
        if is_necessarily:
            raise FileNotFoundError(f"Didn't find {file_stem}.* file")
        else:
            logger.warning(f"Didn't find {file_stem}.* file, but it's not necessarily")


def check_new_dir() -> list[Path]:
    files = []

    find_file('conditions', files)
    find_file('solution', files, is_necessarily=False)
    find_file('picture', files)

    return files


async def main():
    id_ = str(uuid.uuid4())[:32]
    if (TASKS_DIR / id_).exists():
        raise FileExistsError(f'{TASKS_DIR / id_}')

    task_dir = TASKS_DIR / id_
    where_it_research = input("Где это изучают: ") # TODO: Ввести что-то
    files = check_new_dir()
    print(files)
    task_dir.mkdir()

    for file in files:
        file.rename(task_dir / file.name)

    async with async_session() as session:
        task = Task(id=id_, where_it_research=where_it_research)
        session.add(task)
        await session.commit()

    print(f'New tasks dir {task_dir}')


if __name__ == '__main__':
    asyncio.run(main())
