import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from bot import dp
from database import db_functions
from handlers.keyboards import inline_keybords
from handlers.models.categories_deletion_model import CategoriesAddingForm


@dp.callback_query_handler(text_contains='add:category:button', state=CategoriesAddingForm.start)
async def add_category_handler(call: CallbackQuery) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку добавления, отправляя запрос на предоставление имени категории.
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Добавляем категорию. Пользователь с id {call.from_user.id}.")
        await call.answer()
        await CategoriesAddingForm.add_category.set()
        categories = await db_functions.return_all_categories(str(call.from_user.id))
        string = ""
        num = 1
        for key in categories:
            string += f"{num}) {key}\n"
            num += 1
        await call.message.answer(f"Отправьте имя новой категории. Вот список текущих:\n{string}")
    except Exception as e:
        logging.error(f"{add_category_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await CategoriesAddingForm.start.set()


@dp.callback_query_handler(text_contains='delete:subcategory:button', state=CategoriesAddingForm.start)
async def delete_subcategory_handler(call: CallbackQuery) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку добавления, отправляя запрос на предоставление имени категории.
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Удаляем подкатегорию. Пользователь с id {call.from_user.id}.")
        await call.answer()
        await CategoriesAddingForm.delete_subcategory.set()
        categories = (await db_functions.return_all_categories(str(call.from_user.id))).keys()
        keyboard = await inline_keybords.generate_category_choice_keyboard(list(categories))
        await call.message.answer(f"Выберете, у какой категории будем удалять подкатегорию.", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"{delete_subcategory_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await CategoriesAddingForm.start.set()


@dp.callback_query_handler(text_contains='delete:category:button', state=CategoriesAddingForm.start)
async def delete_category_handler(call: CallbackQuery) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку добавления, отправляя запрос на предоставление имени категории.
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Удаляем категорию. Пользователь с id {call.from_user.id}.")
        await call.answer()
        await CategoriesAddingForm.delete_category.set()
        categories = (await db_functions.return_all_categories(str(call.from_user.id))).keys()
        keyboard = await inline_keybords.generate_category_choice_keyboard(list(categories))
        await call.message.answer(f"Выберите категорию, которую будем удалять (удаляются и все подкатегории):",
                                  reply_markup=keyboard)
    except Exception as e:
        logging.error(f"{delete_category_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await CategoriesAddingForm.start.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('choice:category:'),
                           state=CategoriesAddingForm.delete_subcategory)
async def delete_subcategory_callback_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая реагирует на выбор категории кнопкой, добавляя информацию в состояние.
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(
            f"Получаем категорию и отправляем запрос на имя подкатегории для удаления. Пользователь с id {call.from_user.id}.")
        category = call.data[16:]
        await call.message.delete()
        await state.update_data(delete_subcategory=str(category))
        subcategories = (await db_functions.return_all_categories(str(call.from_user.id)))[str(category)]
        await CategoriesAddingForm.delete_subcategory_by_category.set()
        keyboard = await inline_keybords.generate_category_choice_keyboard(subcategories)
        await call.message.answer(f"Выберите подкатегорию, которую будем удалять.", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"{delete_subcategory_callback_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.delete()
        await call.message.answer("Произошла непредвиденная ошибка, попробуйте удалить подкатегорию снова!")
        await CategoriesAddingForm.start.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('choice:category:'),
                           state=CategoriesAddingForm.delete_subcategory_by_category)
async def delete_subcategory_message_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая реагирует на выбор категории кнопкой, удаляя ее.
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(
            f"Получаем подкатегорию для удаления. Пользователь с id {call.from_user.id}.")
        subcategory = call.data[16:]
        await call.message.delete()
        category = (await state.get_data())["delete_subcategory"]
        await db_functions.delete_subcategory(str(call.from_user.id), category, subcategory)
        await call.message.answer(f"Удалили подкатегорию {subcategory} в категории {category}!")
        await CategoriesAddingForm.start.set()
    except Exception as e:
        logging.error(f"{delete_subcategory_message_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.delete()
        await call.message.answer("Произошла непредвиденная ошибка, попробуйте удалить категорию снова!")
        await CategoriesAddingForm.start.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('choice:category:'),
                           state=CategoriesAddingForm.delete_category)
async def add_subcategory_message_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая реагирует на выбор категории кнопкой, удаляя ее.
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(
            f"Получаем категорию для удаления. Пользователь с id {call.from_user.id}.")
        category = call.data[16:]
        await call.message.delete()
        await db_functions.delete_category(str(call.from_user.id), category)
        await call.message.answer(f"Удалили категорию {category}!")
        await CategoriesAddingForm.start.set()
    except Exception as e:
        logging.error(f"{delete_category_callback_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.delete()
        await call.message.answer("Произошла непредвиденная ошибка, попробуйте удалить категорию снова!")
        await CategoriesAddingForm.start.set()


@dp.message_handler(state=CategoriesAddingForm.add_category, content_types=['text'])
async def add_category_message_handler(message: types.Message) -> None:
    """
    Функция, которая реагирует на отправление любого сообщения, после нажатия на кнопку добавления категории.
    :param message: Экземпляр сообщения.
    """
    try:
        logging.debug(f"Получаем имя категории. Пользователь с id {message.from_user.id}.")
        try:
            await dp.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        except Exception as e:
            logging.debug(e)
        print(message.text)
        categories = await db_functions.return_all_categories(str(message.from_user.id))
        if str(message.text) in categories.keys():
            await message.delete()
            await message.answer("Имя категории не должно быть уже добавлено, повторите ввод, снова отправьте имя.")
            await CategoriesAddingForm.add_category.set()
        elif len(categories) >= 12:
            await message.delete()
            await message.answer("На данный момент добавление категорий невозможно, их 12."
                                 " Удалите категорию, чтобы добавить другую!")
            await CategoriesAddingForm.start.set()
        elif len(message.text) > 75:
            await message.delete()
            await message.answer(
                "Имя категории не должно быть больше 75 символов, повторите ввод, снова отправьте имя.")
            await CategoriesAddingForm.add_category.set()
        else:
            await message.delete()
            await db_functions.add_new_category(str(message.from_user.id), str(message.text))
            await message.answer(f"Категория: {str(message.text)} добавлена!")
            await CategoriesAddingForm.start.set()
    except Exception as e:
        logging.error(f"{add_category_message_handler.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await message.delete()
        await message.answer("Произошла непредвиденная ошибка, попробуйте добавить категорию снова!")
        await CategoriesAddingForm.start.set()


@dp.callback_query_handler(text_contains='add:subcategory:button', state=CategoriesAddingForm.start)
async def add_subcategory_handler(call: CallbackQuery) -> None:
    """
    Функция, которая обрабатывает нажатие на кнопку добавления, отправляя запрос на предоставление имени категории.
    :param call: Запрос от кнопки.
    """
    try:
        logging.debug(f"Добавляем подкатегорию. Пользователь с id {call.from_user.id}.")
        await call.answer()
        await CategoriesAddingForm.add_subcategory.set()
        categories = (await db_functions.return_all_categories(str(call.from_user.id))).keys()
        keyboard = await inline_keybords.generate_category_choice_keyboard(list(categories))
        await call.message.answer(f"Выберете, к какой категории будем добавлять подкатегорию.", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"{add_subcategory_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await CategoriesAddingForm.start.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('choice:category:'),
                           state=CategoriesAddingForm.add_subcategory)
async def add_subcategory_message_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая реагирует на выбор категории кнопкой, добавляя информацию в состояние.
    :param call: Вызов от кнопки.
    :param state: Состояние.
    """
    try:
        logging.debug(
            f"Получаем категорию и отправляем запрос на имя подкатегории. Пользователь с id {call.from_user.id}.")
        category = call.data[16:]
        await call.message.delete()
        await state.update_data(add_subcategory=str(category))
        await CategoriesAddingForm.add_subcategory_by_category.set()
        categories = await db_functions.return_all_categories(str(call.from_user.id))
        string = ""
        num = 1
        for key in categories[str(category)]:
            string += f"{num}) {key}\n"
            num += 1
        await call.message.answer(f"Отправьте имя новой подкатегории. Вот список текущих:\n{string}")
    except Exception as e:
        logging.error(f"{delete_category_callback_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await call.message.delete()
        await call.message.answer("Произошла непредвиденная ошибка, попробуйте добавить подкатегорию снова!")
        await CategoriesAddingForm.start.set()


@dp.message_handler(state=CategoriesAddingForm.add_subcategory_by_category, content_types=['text'])
async def delete_category_callback_handler(message: types.Message, state: FSMContext) -> None:
    """
    Функция, которая реагирует на отправление любого сообщения, после нажатия на кнопку добавления категории.
    :param state: Состояние.
    :param message: Экземпляр сообщения.
    """
    try:
        logging.debug(f"Получаем имя подкатегории. Пользователь с id {message.from_user.id}.")
        try:
            await dp.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        except Exception as e:
            logging.debug(e)
        now_category = (await state.get_data())['add_subcategory']
        categories = await db_functions.return_all_categories(str(message.from_user.id))
        if str(message.text) in categories[now_category]:
            await message.delete()
            await message.answer("Имя подкатегории не должно быть уже добавлено, повторите ввод, снова отправьте имя.")
            await CategoriesAddingForm.add_subcategory_by_category.set()
        elif len(categories[now_category]) >= 12:
            await message.delete()
            await message.answer("На данный момент добавление подкатегорий невозможно, их 12."
                                 " Удалите подкатегорию, чтобы добавить другую!")
            await CategoriesAddingForm.start.set()
        elif len(message.text) > 75:
            await message.delete()
            await message.answer(
                "Имя подкатегории не должно быть больше 75 символов, повторите ввод, снова отправьте имя.")
            await CategoriesAddingForm.add_subcategory_by_category.set()
        else:
            await message.delete()
            await db_functions.add_new_subcategory(str(message.from_user.id), str(now_category), str(message.text))
            await message.answer(f"Подкатегория: {str(message.text)} в категорию {now_category} добавлена!")
            await CategoriesAddingForm.start.set()
    except Exception as e:
        logging.error(f"{delete_category_callback_handler.__name__}: {e}. Пользователь с id {message.from_user.id}.")
        await message.delete()
        await message.answer("Произошла непредвиденная ошибка, попробуйте добавить подкатегорию снова!")
        await CategoriesAddingForm.start.set()


@dp.callback_query_handler(text_contains='category:delete', state=CategoriesAddingForm.add_subcategory)
async def cancel_category_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет выбор категории, возвращая в прошлое состояние с сохранением данных
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Отменяем выбор категории. Пользователь с id {call.from_user.id}.')
        await call.answer()
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(CategoriesAddingForm.start)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_category_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(CategoriesAddingForm.start)


@dp.callback_query_handler(text_contains='category:delete', state=CategoriesAddingForm.delete_category)
async def cancel_category_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет выбор категории, возвращая в прошлое состояние с сохранением данных
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Отменяем выбор категории. Пользователь с id {call.from_user.id}.')
        await call.answer()
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(CategoriesAddingForm.start)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_category_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(CategoriesAddingForm.start)


@dp.callback_query_handler(text_contains='category:delete', state=CategoriesAddingForm.delete_subcategory)
async def cancel_category_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет выбор категории, возвращая в прошлое состояние с сохранением данных
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Отменяем выбор категории. Пользователь с id {call.from_user.id}.')
        await call.answer()
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(CategoriesAddingForm.start)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_category_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(CategoriesAddingForm.start)


@dp.callback_query_handler(text_contains='category:delete', state=CategoriesAddingForm.delete_subcategory_by_category)
async def cancel_category_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая отменяет выбор категории, возвращая в прошлое состояние с сохранением данных
    :param call: Запрос от кнопки
    :param state: Состояние.
    """
    try:
        logging.debug(f'Отменяем выбор категории. Пользователь с id {call.from_user.id}.')
        await call.answer()
        await call.message.delete()
        data = await state.get_data()
        await state.set_state(CategoriesAddingForm.start)
        await state.set_data(data)
    except Exception as e:
        logging.error(f"{cancel_category_handler.__name__}: {e}. Пользователь с id {call.from_user.id}.")
        await state.set_state(CategoriesAddingForm.start)
