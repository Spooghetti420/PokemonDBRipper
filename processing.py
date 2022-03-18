import os
import requests
import re
import traceback


def get_pokedex():
    POKEDEX_URL = "https://pokemondb.net/pokedex/all"
    pokedex_page = requests.get(POKEDEX_URL)
    if pokedex_page.ok:
        pokedex_content = pokedex_page.content.decode("utf-8")
    else:
        raise Exception("Pokédex could not be fetched.")

    return pokedex_content


POKEDEX_PATTERN = re.compile(
    r'<a class="ent-name" href="\/pokedex\/([\s\S]+?)".+?View Pokedex for #(\d{3}) ([\s\S]+?)">.+?<\/a>.+?type\/\w+">(\w+)<\/a>(?:<br> *<a class="type-icon.+?"\/type\/\w+">(\w+))?[\s\S]+?<td class="cell-total">(?:\d+)<\/td>\s+<td class="cell-num">(\d+)<\/td>\s<td class="cell-num">(\d+)<\/td>\s<td class="cell-num">(\d+)<\/td>\s<td class="cell-num">(\d+)<\/td>\s<td class="cell-num">(\d+)<\/td>\s<td class="cell-num">(\d+)<\/td>\s')


def get_pokemon_list(page: str):
    all_pokemon = re.finditer(POKEDEX_PATTERN, page)
    out_data = []
    existing_names = set()
    for p in all_pokemon:
        try:
            if p.group(3) in existing_names:
                continue

            print(f"Downloading Pokémon {p.group(3)}: ", end="\n\t")
            existing_names.add(p.group(3))

            group_list = [(p.group(i) if p.group(i) is not None else "none")
                          for i in range(2, 12)]
            group_list[0] = str(int(group_list[0]))
            group_list[2] = group_list[2].lower()
            group_list[3] = group_list[3].lower()

            print(
                f"Extracted stats ({', '.join([f'{stat} = {p.group(i+6)}' for i, stat in enumerate(('HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed'))])})", end="\n\t")

            FRONT_URL_BASE = "https://img.pokemondb.net/sprites/platinum/normal/"
            BACK_URL_BASE = "https://img.pokemondb.net/sprites/platinum/back-normal/"
            END = p.group(1) + ".png"

            front_img_url = FRONT_URL_BASE + END
            back_img_url = BACK_URL_BASE + END

            for (url, folder, suffix) in (
                (front_img_url, "frontSprites", "_front"),
                (back_img_url, "backSprites", "")
            ):
                filename = f"{p.group(1)}{suffix}.png"
                if os.path.exists(os.path.join(folder, filename)):
                    print(f"Skipped downloading existing file {filename}", end="\n\t")
                    continue

                os.makedirs(folder, exist_ok=True)
                img = requests.get(url)
                with open(os.path.join(folder, filename), mode="wb") as image:
                    image.write(img.content)
                    print(f"Downloaded {filename}", end="\n\t")

            print()
            group_list.append(f"{p.group(1)}.png")
            group_list.append(f"{p.group(1)}_front.png")
            group_list.append("placeholder")

            out_data.append(",".join(group_list))

            if p.group(3) == "Arceus":
                # Generation 4 has been fully catalogued
                break

        except KeyboardInterrupt:
            break

        except Exception as e:
            print("Failed to get Pokémon:\n\t")
            traceback.print_exception(e)

    with open("pokemon_data.csv", mode="w", encoding="utf-8") as pokemon_data:
        pokemon_data.write("\n".join(out_data))
