import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import create_db, save_user_profile, find_matches, get_user_profile, update_user_field

BOT_TOKEN = "8312367183:AAHxq19CBL8VUhuMXXiAWEgTbMPuJCCIQcc"
ADMIN_ID = 6108183074

class Form(StatesGroup):
    real_age = State()
    partner_age = State()
    my_orientation_virt = State()
    my_position_virt = State()
    my_orientation_rj = State()
    partner_orientation_virt = State()
    partner_position_virt = State()
    partner_orientation_rj = State()
    zodiac = State()
    country = State()
    city = State()
    partner_country = State()
    partner_city = State()
    timezone = State()
    partner_timezone = State()
    character_person = State()
    partner_character = State()
    strict_no = State()
    about_me = State()
    roleplayer = State()
    partner_roleplayer = State()
    available_time = State()
    my_gender_rj = State()
    partner_gender = State()
    relationship_type = State()
    username = State()
    photo = State()
    review_profile = State()
    editing = State()

def generate_anketa_text(user_data):
    """Генерирует текст анкеты в формате HTML для отправки."""
    return (
        f"<b>Имя пользователя:</b> {user_data.get('username')}\n"
        f"<b>Возраст:</b> {str(user_data.get('real_age'))}\n"
        f"<b>Ищет оппонента возрастом:</b> {user_data.get('partner_age')}\n"
        f"<b>Ориентация (вирт):</b> {user_data.get('my_orientation_virt')}\n"
        f"<b>Позиция (вирт):</b> {user_data.get('my_position_virt')}\n"
        f"<b>Ориентация (рж):</b> {user_data.get('my_orientation_rj')}\n"
        f"<b>Ищет оппонента ориентации (вирт):</b> {user_data.get('partner_orientation_virt')}\n"
        f"<b>Ищет оппонента позиции (вирт):</b> {user_data.get('partner_position_virt')}\n"
        f"<b>Ищет оппонента ориентации (рж):</b> {user_data.get('partner_orientation_rj')}\n"
        f"<b>Знак зодиака:</b> {user_data.get('zodiac')}\n"
        f"<b>Страна:</b> {user_data.get('country')}\n"
        f"<b>Город:</b> {user_data.get('city')}\n"
        f"<b>Страна оппонента:</b> {user_data.get('partner_country')}\n"
        f"<b>Город оппонента:</b> {user_data.get('partner_city')}\n"
        f"<b>Часовой пояс:</b> {user_data.get('timezone')}\n"
        f"<b>Часовой пояс оппонента:</b> {user_data.get('partner_timezone')}\n"
        f"<b>Персонаж:</b> {user_data.get('character_person')}\n"
        f"<b>Персонаж оппонента:</b> {user_data.get('partner_character')}\n"
        f"<b>Строго нельзя:</b> {user_data.get('strict_no')}\n"
        f"<b>О себе:</b> {user_data.get('about_me')}\n"
        f"<b>Ролевик:</b> {user_data.get('roleplayer')}\n"
        f"<b>Ролевик оппонент:</b> {user_data.get('partner_roleplayer')}\n"
        f"<b>Доступное время:</b> {user_data.get('available_time')}\n"
        f"<b>Пол (рж):</b> {user_data.get('my_gender_rj')}\n"
        f"<b>Ищет партнера пола:</b> {user_data.get('partner_gender')}\n"
        f"<b>Тип отношений:</b> {user_data.get('relationship_type')}"
    )

async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Чтобы заполнить анкету, отправьте /anketa.\n"
        "Вашу анкету никто, кроме админа, не увидит.\n"
        "⚠️ Пожалуйста, используйте минимум текста в ответах. "
        "Это нужно, чтобы вся анкета уместилась в одно сообщение."
    )

async def cmd_anketa(message: types.Message, state: FSMContext):
    await state.set_state(Form.real_age)
    await message.answer("Сколько вам лет?\nНе ставьте в конце точку")

async def process_real_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not 10 < int(message.text) < 100:
        await message.answer("Введите корректный возраст (число от 10 до 99).")
        return
    await state.update_data(real_age=int(message.text))
    await state.set_state(Form.partner_age)
    await message.answer("Возраст вашего потенциального оппонента? (например, 18-20)")

async def process_partner_age(message: types.Message, state: FSMContext):
    age_input = message.text.strip().replace(" ", "")
    
    if "-" in age_input:
        try:
            min_age, max_age = map(int, age_input.split("-"))
        except ValueError:
            await message.answer("Неверный формат. Пожалуйста, введите два числа через дефис, например, '18-20'.")
            return
        if not 10 < min_age < 100 or not 10 < max_age < 100 or min_age > max_age:
            await message.answer("Введите корректный диапазон возраста (от 10 до 99), где первое число меньше второго.")
            return
        await state.update_data(partner_age=age_input)
    else:
        if not age_input.isdigit() or not 10 < int(age_input) < 100:
            await message.answer("Введите корректный возраст (число от 10 до 99) или диапазон.")
            return
        await state.update_data(partner_age=age_input)

    await state.set_state(Form.my_orientation_virt)
    await message.answer("Ваша ориентация (вирт)?")

async def process_my_orientation_virt(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(my_orientation_virt=message.text)
    
    position_kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Актив"), KeyboardButton(text="Пассив"), KeyboardButton(text="Уни")],
        [KeyboardButton(text="Нет точной")],
    ], resize_keyboard=True)
    await state.set_state(Form.my_position_virt)
    await message.answer("Ваша позиция (вирт)?", reply_markup=position_kb)

async def process_my_position_virt(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(my_position_virt=message.text)
    await state.set_state(Form.my_orientation_rj)
    await message.answer("Ваша ориентация (рж)?", reply_markup=ReplyKeyboardRemove())

async def process_my_orientation_rj(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(my_orientation_rj=message.text)
    await state.set_state(Form.partner_orientation_virt)
    await message.answer("Ориентация вашего оппонента (вирт)?")

async def process_partner_orientation_virt(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(partner_orientation_virt=message.text)
    
    position_kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Актив"), KeyboardButton(text="Пассив"), KeyboardButton(text="Уни")],
        [KeyboardButton(text="Нет точной")],
    ], resize_keyboard=True)
    await state.set_state(Form.partner_position_virt)
    await message.answer("Позиция вашего оппонента (вирт)?", reply_markup=position_kb)

async def process_partner_position_virt(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(partner_position_virt=message.text)
    await state.set_state(Form.partner_orientation_rj)
    await message.answer("Ориентация вашего оппонента (рж)?", reply_markup=ReplyKeyboardRemove())

async def process_partner_orientation_rj(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(partner_orientation_rj=message.text)
    await state.set_state(Form.zodiac)
    await message.answer("Ваш знак зодиака?")

async def process_zodiac(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(zodiac=message.text)
    await state.set_state(Form.country)
    await message.answer("Страна?")

async def process_country(message: types.Message, state: FSMContext):
    if len(message.text) > 15:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 15 символов.")
        return
    await state.update_data(country=message.text)
    await state.set_state(Form.city)
    await message.answer("Город (при желании)?")

async def process_city(message: types.Message, state: FSMContext):
    if len(message.text) > 15:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 15 символов.")
        return
    await state.update_data(city=message.text)
    await state.set_state(Form.partner_country)
    await message.answer("Страна вашего оппонента?")

async def process_partner_country(message: types.Message, state: FSMContext):
    if len(message.text) > 15:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 15 символов.")
        return
    await state.update_data(partner_country=message.text)
    await state.set_state(Form.partner_city)
    await message.answer("Город вашего оппонента (при желании)?")

async def process_partner_city(message: types.Message, state: FSMContext):
    if len(message.text) > 15:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 15 символов.")
        return
    await state.update_data(partner_city=message.text)
    await state.set_state(Form.timezone)
    await message.answer("Ваш часовой пояс?")

async def process_timezone(message: types.Message, state: FSMContext):
    if len(message.text) > 15:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 15 символов.")
        return
    await state.update_data(timezone=message.text)
    await state.set_state(Form.partner_timezone)
    await message.answer("Часовой пояс вашего оппонента?")

async def process_partner_timezone(message: types.Message, state: FSMContext):
    if len(message.text) > 15:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 15 символов.")
        return
    await state.update_data(partner_timezone=message.text)
    await state.set_state(Form.character_person)
    await message.answer("Персонаж?")

async def process_character_person(message: types.Message, state: FSMContext):
    if len(message.text) > 15:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 15 символов.")
        return
    await state.update_data(character_person=message.text)
    await state.set_state(Form.partner_character)
    await message.answer("Персонаж вашего оппонента?")

async def process_partner_character(message: types.Message, state: FSMContext):
    if len(message.text) > 20:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 20 символов.")
        return
    await state.update_data(partner_character=message.text)
    await state.set_state(Form.strict_no)
    await message.answer("То, чего строго не должно быть в вашем оппоненте? (до 100 символов)")

async def process_strict_no(message: types.Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 100 символов.")
        return
    await state.update_data(strict_no=message.text)
    await state.set_state(Form.about_me)
    await message.answer("Несколько слов о вашем характере, манере общения? (до 100 символов)")

async def process_about_me(message: types.Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 100 символов.")
        return
    await state.update_data(about_me=message.text)
    
    await state.set_state(Form.roleplayer)
    await message.answer("Ролевик (да/нет)?")

async def process_roleplayer(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(roleplayer=message.text)
    
    await state.set_state(Form.partner_roleplayer)
    await message.answer("Ваш оппонент ролевик (да/нет)?")

async def process_partner_roleplayer(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(partner_roleplayer=message.text)
    await state.set_state(Form.available_time)
    await message.answer("Время, в которое вы готовы ответить?")

async def process_available_time(message: types.Message, state: FSMContext):
    if len(message.text) > 15:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 15 символов.")
        return
    await state.update_data(available_time=message.text)
    
    await state.set_state(Form.my_gender_rj)
    await message.answer("Девушка в рж / парень в рж (это про вас)?")

async def process_my_gender_rj(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(my_gender_rj=message.text)
    
    await state.set_state(Form.partner_gender)
    await message.answer("Пол вашего партнера (мж/жн)?")

async def process_partner_gender(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(partner_gender=message.text)
    await state.set_state(Form.relationship_type)
    await message.answer("Кого ищете? (друга/партнера)")

async def process_relationship_type(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
        return
    await state.update_data(relationship_type=message.text)
    await state.set_state(Form.username)
    await message.answer("Напишите ваш юзернейм в телеграмме (@username):")

async def process_username(message: types.Message, state: FSMContext):
    if not re.match(r"^@[A-Za-z0-9_]{5,32}$", message.text):
        await message.answer("Пожалуйста, введите корректный юзернейм в формате @username (от 5 до 32 символов).")
        return
    await state.update_data(username=message.text)
    await state.set_state(Form.photo)
    await message.answer("Пришлите фото вашего персонажа (формат 16:9). Это обязательный шаг.", reply_markup=ReplyKeyboardRemove())

async def process_photo(message: types.Message, state: FSMContext, bot: Bot):
    if not message.photo:
        await message.answer("Пожалуйста, пришлите именно фото. Если вы хотите отменить заполнение, нажмите /start")
        return

    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    user_data = await state.get_data()
    anketa_text = generate_anketa_text(user_data)
    
    review_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Всё верно", callback_data="confirm_anketa"),
         InlineKeyboardButton(text="❌ Исправить", callback_data="decline_anketa")]
    ])

    await message.answer_photo(photo_id, caption="<b>Предпросмотр анкеты:</b>\n" + anketa_text, parse_mode="HTML", reply_markup=review_kb)
    await state.set_state(Form.review_profile)

async def process_review_profile(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()

    if callback_query.data == "confirm_anketa":
        user_data = await state.get_data()
        user_data['user_id'] = callback_query.from_user.id
        
        await save_user_profile(user_data)
        
        anketa_text = generate_anketa_text(user_data)
        
        # Теперь отправляем всегда одно сообщение с фото и текстом, так как лимиты жёстко установлены
        await bot.send_photo(chat_id=ADMIN_ID, photo=user_data.get('photo'), caption=anketa_text, parse_mode="HTML")

        matches = await find_matches(user_data)
        if matches:
            await bot.send_message(ADMIN_ID, f"<b>🎯 Совпадения для {user_data.get('username')}!</b>", parse_mode="HTML")
            matches_usernames = [match['username'] for match in matches if match['username']]
            if matches_usernames:
                matches_text = "Найдено несколько совпадений: " + ", ".join(matches_usernames)
                await bot.send_message(ADMIN_ID, matches_text)
            else:
                await bot.send_message(ADMIN_ID, "Совпадений не найдено или у них нет юзернейма.")

        await bot.send_message(callback_query.from_user.id, "✅ Ваша анкета успешно сохранена и отправлена администратору!", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    
    elif callback_query.data == "decline_anketa":
        await bot.send_message(callback_query.from_user.id, "❌ Хорошо, начните заполнение заново, чтобы исправить анкету. Нажмите /anketa")
        await state.clear()

async def cmd_edit(message: types.Message):
    user_id = message.from_user.id
    user_profile = await get_user_profile(user_id)

    if not user_profile:
        await message.answer("Вы ещё не заполнили анкету. Используйте команду /anketa.")
        return
    
    edit_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Возраст", callback_data="edit_real_age"),
         InlineKeyboardButton(text="Возраст оппонента", callback_data="edit_partner_age")],
        [InlineKeyboardButton(text="Ориентация (вирт)", callback_data="edit_my_orientation_virt"),
         InlineKeyboardButton(text="Позиция (вирт)", callback_data="edit_my_position_virt")],
        [InlineKeyboardButton(text="Ориентация (рж)", callback_data="edit_my_orientation_rj"),
         InlineKeyboardButton(text="Ориентация оппонента (вирт)", callback_data="edit_partner_orientation_virt")],
        [InlineKeyboardButton(text="Позиция оппонента (вирт)", callback_data="edit_partner_position_virt"),
         InlineKeyboardButton(text="Ориентация оппонента (рж)", callback_data="edit_partner_orientation_rj")],
        [InlineKeyboardButton(text="Персонаж", callback_data="edit_character_person"),
         InlineKeyboardButton(text="Персонаж оппонента", callback_data="edit_partner_character")],
        [InlineKeyboardButton(text="О себе", callback_data="edit_about_me"),
         InlineKeyboardButton(text="Строго нельзя", callback_data="edit_strict_no")],
        [InlineKeyboardButton(text="Пол (рж)", callback_data="edit_my_gender_rj"),
         InlineKeyboardButton(text="Пол партнера", callback_data="edit_partner_gender")],
        [InlineKeyboardButton(text="Другое", callback_data="edit_other")],
    ])

    await message.answer("Что бы вы хотели изменить в своей анкете?", reply_markup=edit_kb)

async def process_edit_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    field_to_edit = callback_query.data.replace("edit_", "")

    if field_to_edit == "other":
        other_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Знак зодиака", callback_data="edit_zodiac")],
            [InlineKeyboardButton(text="Страна", callback_data="edit_country"),
             InlineKeyboardButton(text="Город", callback_data="edit_city")],
            [InlineKeyboardButton(text="Страна оппонента", callback_data="edit_partner_country"),
             InlineKeyboardButton(text="Город оппонента", callback_data="edit_partner_city")],
            [InlineKeyboardButton(text="Часовой пояс", callback_data="edit_timezone"),
             InlineKeyboardButton(text="Часовой пояс оппонента", callback_data="edit_partner_timezone")],
            [InlineKeyboardButton(text="Ролевик", callback_data="edit_roleplayer"),
             InlineKeyboardButton(text="Ролевик оппонент", callback_data="edit_partner_roleplayer")],
            [InlineKeyboardButton(text="Доступное время", callback_data="edit_available_time"),
             InlineKeyboardButton(text="Тип отношений", callback_data="edit_relationship_type")],
            [InlineKeyboardButton(text="Юзернейм", callback_data="edit_username"),
             InlineKeyboardButton(text="Фото", callback_data="edit_photo")]
        ])
        await callback_query.message.edit_text("Что еще вы хотите изменить?", reply_markup=other_kb)
        return

    await state.set_state(Form.editing)
    await state.update_data(field_to_edit=field_to_edit)
    
    prompt_text = {
        "real_age": "Введите новый возраст:",
        "partner_age": "Введите новый возраст оппонента (например, 18-20):",
        "my_orientation_virt": "Введите новую ориентацию (вирт): (до 10 символов)",
        "my_position_virt": "Введите новую позицию (вирт): (до 10 символов)",
        "my_orientation_rj": "Введите новую ориентацию (рж): (до 10 символов)",
        "partner_orientation_virt": "Введите новую ориентацию оппонента (вирт): (до 10 символов)",
        "partner_position_virt": "Введите новую позицию оппонента (вирт): (до 10 символов)",
        "partner_orientation_rj": "Введите новую ориентацию оппонента (рж): (до 10 символов)",
        "character_person": "Введите нового персонажа: (до 15 символов)",
        "partner_character": "Введите нового персонажа оппонента: (до 15 символов)",
        "about_me": "Введите новое описание о себе: (до 100 символов)",
        "strict_no": "Введите, чего строго не должно быть в оппоненте: (до 100 символов)",
        "my_gender_rj": "Введите новый пол в рж: (до 10 символов)",
        "partner_gender": "Введите новый пол партнера: (до 10 символов)",
        "zodiac": "Введите новый знак зодиака: (до 10 символов)",
        "country": "Введите новую страну: (до 15 символов)",
        "city": "Введите новый город: (до 15 символов)",
        "partner_country": "Введите новую страну оппонента: (до 15 символов)",
        "partner_city": "Введите новый город оппонента: (до 15 символов)",
        "timezone": "Введите новый часовой пояс: (до 15 символов)",
        "partner_timezone": "Введите новый часовой пояс оппонента: (до 15 символов)",
        "roleplayer": "Введите 'Да' или 'Нет' для ролевика: (до 10 символов)",
        "partner_roleplayer": "Введите 'Да' или 'Нет' для ролевика оппонента: (до 10 символов)",
        "available_time": "Введите новое доступное время: (до 15 символов)",
        "relationship_type": "Введите новый тип отношений: (до 10 символов)",
        "username": "Введите новый юзернейм (@username):",
        "photo": "Пришлите новое фото:",
    }
    
    await callback_query.message.answer(prompt_text.get(field_to_edit, "Введите новое значение:"))

async def process_new_value(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    field_to_edit = user_data.get("field_to_edit")

    if field_to_edit == 'real_age':
        if not message.text.isdigit() or not 10 < int(message.text) < 100:
            await message.answer("Некорректный возраст. Пожалуйста, введите число от 10 до 99.")
            return
    elif field_to_edit == 'username':
        if not re.match(r"^@[A-Za-z0-9_]{5,32}$", message.text):
            await message.answer("Пожалуйста, введите корректный юзернейм в формате @username (от 5 до 32 символов).")
            return
    elif field_to_edit == 'photo':
        if not message.photo:
            await message.answer("Пожалуйста, пришлите именно фото. Если вы хотите отменить редактирование, нажмите /start")
            return
    elif field_to_edit in ['about_me', 'strict_no']:
        if len(message.text) > 100:
            await message.answer("Пожалуйста, сократите текст. Он не должен превышать 100 символов.")
            return
    elif field_to_edit in ['my_orientation_virt', 'my_position_virt', 'my_orientation_rj', 'partner_orientation_virt', 'partner_position_virt', 'partner_orientation_rj', 'my_gender_rj', 'partner_gender', 'relationship_type', 'zodiac']:
        if len(message.text) > 10:
            await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
            return
    elif field_to_edit in ['country', 'city', 'partner_country', 'partner_city', 'timezone', 'partner_timezone', 'character_person', 'partner_character', 'available_time']:
        if len(message.text) > 15:
            await message.answer("Пожалуйста, сократите текст. Он не должен превышать 15 символов.")
            return
    elif field_to_edit in ['roleplayer', 'partner_roleplayer']:
        if len(message.text) > 10:
            await message.answer("Пожалуйста, сократите текст. Он не должен превышать 10 символов.")
            return

    new_value = message.text
    if field_to_edit == 'photo':
        new_value = message.photo[-1].file_id
    
    await update_user_field(message.from_user.id, field_to_edit, new_value)
    
    await message.answer(f"✅ Поле '{field_to_edit}' успешно обновлено.")
    
    review_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Посмотреть анкету", callback_data="show_anketa"),
         InlineKeyboardButton(text="Завершить редактирование", callback_data="finish_editing")]
    ])
    await message.answer("Хотите посмотреть обновлённую анкету или завершить редактирование?", reply_markup=review_kb)

    await state.clear()


async def process_editing_review(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    
    if callback_query.data == "show_anketa":
        user_profile = await get_user_profile(callback_query.from_user.id)
        if user_profile:
            anketa_text = generate_anketa_text(user_profile)
            await bot.send_photo(chat_id=callback_query.from_user.id, photo=user_profile.get('photo'), caption="<b>Ваша обновлённая анкета:</b>\n" + anketa_text, parse_mode="HTML")
        else:
            await callback_query.message.answer("Профиль не найден. Пожалуйста, заполните анкету заново.")

    elif callback_query.data == "finish_editing":
        await callback_query.message.answer("Редактирование завершено. Если что-то ещё нужно, нажмите /edit.")
    
    await state.clear()

async def cmd_myid(message: types.Message):
    await message.answer(f"Ваш Telegram ID: {message.from_user.id}")

async def main():
    await create_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    dp.message.register(cmd_myid, Command('myid'))
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_anketa, Command("anketa"))
    dp.message.register(process_real_age, Form.real_age)
    dp.message.register(process_partner_age, Form.partner_age)
    dp.message.register(process_my_orientation_virt, Form.my_orientation_virt)
    dp.message.register(process_my_position_virt, Form.my_position_virt)
    dp.message.register(process_my_orientation_rj, Form.my_orientation_rj)
    dp.message.register(process_partner_orientation_virt, Form.partner_orientation_virt)
    dp.message.register(process_partner_position_virt, Form.partner_position_virt)
    dp.message.register(process_partner_orientation_rj, Form.partner_orientation_rj)
    dp.message.register(process_zodiac, Form.zodiac)
    dp.message.register(process_country, Form.country)
    dp.message.register(process_city, Form.city)
    dp.message.register(process_partner_country, Form.partner_country)
    dp.message.register(process_partner_city, Form.partner_city)
    dp.message.register(process_timezone, Form.timezone)
    dp.message.register(process_partner_timezone, Form.partner_timezone)
    dp.message.register(process_character_person, Form.character_person)
    dp.message.register(process_partner_character, Form.partner_character)
    dp.message.register(process_strict_no, Form.strict_no)
    dp.message.register(process_about_me, Form.about_me)
    dp.message.register(process_roleplayer, Form.roleplayer)
    dp.message.register(process_partner_roleplayer, Form.partner_roleplayer)
    dp.message.register(process_available_time, Form.available_time)
    dp.message.register(process_my_gender_rj, Form.my_gender_rj)
    dp.message.register(process_partner_gender, Form.partner_gender)
    dp.message.register(process_relationship_type, Form.relationship_type)
    dp.message.register(process_username, Form.username)
    dp.message.register(process_photo, Form.photo)
    dp.message.register(cmd_edit, Command("edit"))
    dp.message.register(process_new_value, Form.editing)
    dp.callback_query.register(process_review_profile, Form.review_profile)
    dp.callback_query.register(process_edit_selection, F.data.startswith("edit_"))
    dp.callback_query.register(process_editing_review, F.data.in_({"show_anketa", "finish_editing"}))
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())