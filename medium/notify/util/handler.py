from discord.ext import commands
from datetime import datetime
from config.loader import cfg
import asyncio


class Handler(commands.Cog):
    def __init__(self, client, lang, logger, db, cursor):
        self.client = client
        self.lang = lang
        self.logger = logger

        self.db = db
        self.cursor = cursor

    async def notify(self, event, user_id, delay):
        """
            Calculates datetime for notification
                Args:
                    event(string): ID of an event
                    user(string): User ID
                    delay(int): delay in sec.

        """

        await asyncio.sleep(delay)

        user = self.client.get_user(int(user_id))
        if user:
            sql = "SELECT Name, Time FROM Event WHERE ID = %s;"
            self.cursor.execute(sql, [event])
            result = self.cursor.fetchone()

            guild = self.client.get_guild(int(cfg['guild']))
            nickname = guild.get_member(int(user_id)).display_name

            await user.send(self.lang["notify_global"]["noti"].format(nickname, str(result[0]), str(result[1])))

    @commands.Cog.listener()
    async def on_ready(self):
        sql = "SELECT n.User, n.Time, n.Event FROM Notify n, User u \
                WHERE n.User = u.ID AND u.Notify AND n.Time >= CURDATE();"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        for elem in result:
            now = datetime.now()
            delta = (elem[1]-now).total_seconds()
            if delta > 0:
                await self.notify(elem[2], elem[0], delta)

