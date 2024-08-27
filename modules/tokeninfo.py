import colorama
import requests
import shutil
from modules import clear
from modules import cprint

gray = colorama.Fore.LIGHTBLACK_EX
cyan = colorama.Fore.CYAN
green = colorama.Fore.GREEN
red = colorama.Fore.RED
yellow = colorama.Fore.YELLOW
white = colorama.Fore.WHITE


def permissions_to_string(permissions):
    useful_permissions = [
        "ADMINISTRATOR", "KICK_MEMBERS", "BAN_MEMBERS", "MANAGE_CHANNELS",
        "MANAGE_GUILD", "MANAGE_ROLES", "MANAGE_WEBHOOKS"
    ]
    other_permissions = [
        "CREATE_INSTANT_INVITE", "ADD_REACTIONS", "VIEW_AUDIT_LOG",
        "PRIORITY_SPEAKER", "STREAM", "VIEW_CHANNEL", "SEND_MESSAGES",
        "SEND_TTS_MESSAGES", "MANAGE_MESSAGES", "EMBED_LINKS", "ATTACH_FILES",
        "READ_MESSAGE_HISTORY", "MENTION_EVERYONE", "USE_EXTERNAL_EMOJIS",
        "VIEW_GUILD_INSIGHTS", "CONNECT", "SPEAK", "MUTE_MEMBERS", "DEAFEN_MEMBERS",
        "MOVE_MEMBERS", "USE_VAD", "CHANGE_NICKNAME", "MANAGE_NICKNAMES",
        "MANAGE_EMOJIS_AND_STICKERS"
    ]

    def format_permission(perm):
        return perm.capitalize()

    useful = []
    rest = []

    for i, perm in enumerate(useful_permissions + other_permissions):
        if permissions & (1 << i):
            if perm in useful_permissions:
                if perm == "ADMINISTRATOR":
                    useful.insert(0, f"{yellow}{format_permission(perm)}{white}")
                else:
                    useful.append(f"{green}{format_permission(perm)}{white}")
            else:
                rest.append(format_permission(perm))

    terminal_width = shutil.get_terminal_size().columns
    useful_str = f"{white}Useful: {', '.join(useful)}"
    rest_str = f"{white}The Rest: {', '.join(rest)}"

    if len(rest_str) > terminal_width:
        available_width = terminal_width - len(f"{white}The Rest: ") - 3  # 3 for "..."
        trimmed_rest = []
        current_length = 0
        for perm in rest:
            if current_length + len(perm) + 2 <= available_width:  # 2 for ", "
                trimmed_rest.append(perm)
                current_length += len(perm) + 2
            else:
                break
        rest_str = f"{white}The Rest: {', '.join(trimmed_rest)}..."

    result = f"{useful_str}\n{rest_str}"
    return result


def token_info():
    token = input(f"{white}Token: ")
    headers = {"Authorization": token}
    response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)

    if response.status_code == 401:
        headers["Authorization"] = f"Bot {token}"
        response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        username = user_data.get("username")
        bio = user_data.get("bio", "No bio set.")
        token_type = "BOT" if "Bot" in headers["Authorization"] else "USER"

        guilds_response = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=headers)
        guilds_data = guilds_response.json()

        terminal_width = shutil.get_terminal_size().columns

        print(f"\n{gray}{'=' * terminal_width}")
        print(f"{cyan}Discord Token Information")
        print(f"{gray}{'=' * terminal_width}\n")

        print(f"{white}Username: {cyan}{username}")
        print(f"{white}Token Type: {cyan}{token_type}")
        print(f"{white}Bio: {cyan}{bio}")
        print(f"{white}Server Count: {cyan}{len(guilds_data)}")

        print(f"\n{gray}{'-' * terminal_width}")
        print(f"{cyan}Servers {username} is in:")
        print(f"{gray}{'-' * terminal_width}")

        for guild in guilds_data:
            print(f"{white}• {cyan}{guild['name']} {gray}(ID: {guild['id']})")
            if token_type == "BOT":
                permissions = permissions_to_string(int(guild['permissions']))
                print(f"{permissions}\n")

        print(f"{gray}{'=' * terminal_width}")
    else:
        cprint("Invalid Token or unexpected response from Discord API.", 1)

    input(f"\n{white}Press enter to continue...")
    clear()