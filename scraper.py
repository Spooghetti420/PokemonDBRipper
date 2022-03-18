from processing import get_pokedex, get_pokemon_list

def main():
    pokedex = get_pokedex()
    get_pokemon_list(pokedex)

if __name__ == "__main__":
    main()