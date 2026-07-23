import aiosqlite

DB = "levels.db"


async def setup_database():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
        """)
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DB) as db:
        result = await db.execute(
            "SELECT xp, level FROM users WHERE user_id=?",
            (user_id,)
        )
        user = await result.fetchone()

        if user:
            return user

        await db.execute(
            "INSERT INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        await db.commit()

        return 0, 1


async def update_user(user_id, xp, level):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET xp=?, level=? WHERE user_id=?",
            (xp, level, user_id)
        )
        await db.commit()


async def add_xp(user_id, amount):
    xp, level = await get_user(user_id)

    xp += amount
    needed = level * 100
    up = False

    if xp >= needed:
        xp -= needed
        level += 1
        up = True

    await update_user(user_id, xp, level)

    return xp, level, up


async def leaderboard():
    async with aiosqlite.connect(DB) as db:
        result = await db.execute(
            """
            SELECT user_id, level, xp
            FROM users
            ORDER BY level DESC, xp DESC
            LIMIT 10
            """
        )

        return await result.fetchall()
