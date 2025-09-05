import aiosqlite

DB_NAME = 'dating_profiles.db'

async def create_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                real_age INTEGER,
                partner_age TEXT,
                my_orientation_virt TEXT,
                my_position_virt TEXT,
                my_orientation_rj TEXT,
                partner_orientation_virt TEXT,
                partner_position_virt TEXT,
                partner_orientation_rj TEXT,
                zodiac TEXT,
                country TEXT,
                city TEXT,
                partner_country TEXT,
                partner_city TEXT,
                timezone TEXT,
                partner_timezone TEXT,
                character_person TEXT,
                partner_character TEXT,
                strict_no TEXT,
                about_me TEXT,
                roleplayer TEXT,
                partner_roleplayer TEXT,
                available_time TEXT,
                my_gender_rj TEXT,
                partner_gender TEXT,
                relationship_type TEXT,
                photo TEXT
            )
        ''')
        await db.commit()

async def save_user_profile(data):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR REPLACE INTO profiles (
                user_id, username, real_age, partner_age, my_orientation_virt,
                my_position_virt, my_orientation_rj, partner_orientation_virt,
                partner_position_virt, partner_orientation_rj, zodiac,
                country, city, partner_country, partner_city, timezone,
                partner_timezone, character_person, partner_character, strict_no,
                about_me, roleplayer, partner_roleplayer, available_time,
                my_gender_rj, partner_gender, relationship_type, photo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['user_id'], data['username'], data['real_age'], data['partner_age'],
            data['my_orientation_virt'], data['my_position_virt'], data['my_orientation_rj'],
            data['partner_orientation_virt'], data['partner_position_virt'], data['partner_orientation_rj'],
            data['zodiac'], data['country'], data['city'], data['partner_country'],
            data['partner_city'], data['timezone'], data['partner_timezone'],
            data['character_person'], data['partner_character'], data['strict_no'],
            data['about_me'], data['roleplayer'], data['partner_roleplayer'],
            data['available_time'], data['my_gender_rj'], data['partner_gender'],
            data['relationship_type'], data['photo']
        ))
        await db.commit()

async def get_user_profile(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def update_user_field(user_id, field, value):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"UPDATE profiles SET {field} = ? WHERE user_id = ?", (value, user_id))
        await db.commit()

async def find_matches(user_data):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        
        # Получаем все профили, кроме профиля текущего пользователя
        cursor = await db.execute('SELECT * FROM profiles WHERE user_id != ?', (user_data['user_id'],))
        profiles = await cursor.fetchall()
        
        matches = []
        for profile in profiles:
            is_match = (
                user_data['partner_age'] == profile['real_age'] or
                user_data['partner_orientation_virt'] == profile['my_orientation_virt'] or
                user_data['partner_gender'] == profile['my_gender_rj']
            )
            if is_match:
                matches.append(dict(profile))
        return matches