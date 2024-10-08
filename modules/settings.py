import configparser
import colorama
import os
import subprocess
from modules import cprint, clear, menu

gray = colorama.Fore.LIGHTBLACK_EX
cyan = colorama.Fore.CYAN
green = colorama.Fore.GREEN
red = colorama.Fore.RED
yellow = colorama.Fore.YELLOW
white = colorama.Fore.WHITE


def bot_nuker_config(OnlyOption=None):
    try:
        if not OnlyOption:
            clear()
            menu()
            print(f"""            {gray}[{cyan}1{gray}]{white} Read Current Config
            {gray}[{cyan}2{gray}]{white} bot_token
            {gray}[{cyan}3{gray}]{white} spam_message
            {gray}[{cyan}4{gray}]{white} role_name
            {gray}[{cyan}5{gray}]{white} channel_name
            {gray}[{cyan}6{gray}]{white} dm_message
            {gray}[{cyan}7{gray}]{white} ban_reason
            {gray}[{cyan}8{gray}]{white} server_name""")

        config = configparser.ConfigParser()
        config.read('config.ini')
        option = int(input(f"\n{white}Choose Option: "))
        print(" ")
        if option == 1:
            for key in config['bot_nuker_config']:
                spaces = " "
                for _ in range(12 - len(key)):
                    spaces = f"{spaces} "
                if key == "spam_message":
                    print(f"{cyan}{key}{spaces}{gray}|{white} spam_message.txt")
                else:
                    print(f"{cyan}{key}{spaces}{gray}|{white} {config['bot_nuker_config'][key]}")
            bot_nuker_config(True)

        elif option == 2:
            key = "bot_token"
        elif option == 3:
            key = "spam_message"
        elif option == 4:
            key = "role_name"
        elif option == 5:
            key = "channel_name"
        elif option == 6:
            key = "dm_message"
        elif option == 7:
            key = "ban_message"
        elif option == 8:
            key = "server_name"

        if option != 1:
            if key == "spam_message":
                if not os.path.exists('spam_message.txt'):
                    with open('spam_message.txt', 'w') as f:
                        f.write("When you're done just save and close this.")
                    cprint("Created new spam_message.txt file with default message.", 0)

                if os.name == 'nt':  # Windows
                    os.system(f'notepad spam_message.txt')
                else:  # Unix-based systems
                    os.system(f'nano spam_message.txt')

                with open('spam_message.txt', 'r') as f:
                    new = f.read().strip()
                print(f"Current {key}: spam_message.txt")
            else:
                print(f"Current {key}: {config['bot_nuker_config'][key]}")
                new = input(f"New {key}: ")

            config['bot_nuker_config'][f'{key}'] = new

            with open('config.ini', 'w') as configfile:
                config.write(configfile)

            cprint("The config has been updated!", 0)

            bot_nuker_config(True)

    except KeyboardInterrupt:
        clear()
        return

configtype = {
    1: bot_nuker_config,
}


def config():
    try:
        clear()
        menu()
        print(f"""    {gray}[{cyan}1{gray}]{white} Bot Nuker Config""")
        choice = int(input(colorama.Fore.WHITE + "\nChoose Option: "))
        configtype[choice]()
    except KeyboardInterrupt:
        clear()
        return
