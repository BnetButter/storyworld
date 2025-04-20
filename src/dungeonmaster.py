import openai
import typing
from typing import *
import os
import json
import sys
import time
import threading
import logging

logger = logging.getLogger(__name__)

loglevel = None if len(sys.argv) == 1 else sys.argv[1]

OPENAI_KEY = os.environ["OPENAI_KEY"]

class NPC(TypedDict):
    name: str
    backstory: str
    ascii_symbol: str

class Item(TypedDict):
    item_name: str
    item_description: str
    ascii_symbol: str

class Scenario(TypedDict):
    scenario: str
    intermediate_states: List[str]
    end_state: str

class GameData(TypedDict):
    npc: List[NPC]
    items: List[Item]
    scenario: Scenario

client = openai.OpenAI(api_key=OPENAI_KEY)


def init_game_state() -> dict:
    if loglevel == "DEBUG":
        time.sleep(1)
        return TEST_RESPONSE
    
    try:
        # Make the API call to OpenAI with the system prompt
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Specify the model you're using
            messages=[
                {"role": "user", "content": SYSTEM_PROMPT}
            ],
            temperature=0.5,
            max_tokens=4096  # Adjust this value as needed
        )

        # Parse the response and extract the JSON output
        game_state = json.loads(response.choices[0].message.content.strip())

        return game_state

    except Exception as e:
        print(f"Error initializing game state: {e}")
        return {}


class GlobalGameState:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GlobalGameState, cls).__new__(cls)
        return cls._instance

    def __init__(self, player_pos=None, world=None):
        if hasattr(self, "_initialized") and self._initialized:
            return  # Avoid reinitializing

        self.init_state: GameData | None = None
        self.player_pos = list(player_pos)
        self.world = world
        self._initialized = True

        self.location_index = {}

        def init():
            import world

            game_state: GameData = init_game_state()
            for item in game_state["items"]:
                symbol = item["ascii_symbol"]
                name = item["item_name"]
                y, x = world.random_valid_point(self.world)
                self.world[y][x] = ord(symbol)
                logger.debug(f"item: {name} {y}, {x}")
                self.location_index[y,x] = { "type": "item"} | item
            
            for item in game_state["npc"]:
                symbol = item["ascii_symbol"]
                name = item["name"]
                y, x = world.random_valid_point(self.world)
                self.world[y][x] = ord(symbol)
                logger.debug(f"item: {name} {y}, {x}")
                self.location_index[y,x] = { "type": "npc"} | item

            self.init_state = game_state
        threading.Thread(target=init).start()

    def get_item_description(self, item):
        if "detailed_description" in item:
            return item["detailed_description"]
        
        try:
            # Make the API call to OpenAI with the system prompt
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Specify the model you're using
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + f"{self.init_state}"},
                    {"role": "user", "content": f"generate detailed item description for {item['item_name']} in 100 words. Just give the item description as text, not JSON"}
                ],
                temperature=0.7,
                max_tokens=1024  # Adjust this value as needed
            )

            # Parse the response and extract the JSON output
            item["detailed_description"] = response.choices[0].message.content.strip()
            return item["detailed_description"]
        except Exception as e:
            print(f"Error initializing game state: {e}")
            return {}



    def get_item_near_me(self, y, x) -> dict | None:
        distance = 2
        for dy in range(-distance, distance + 1):
            for dx in range(-distance, distance + 1):
                ny, nx = y + dy, x + dx
                if (ny, nx) in self.location_index:
                    return self.location_index[(ny, nx)]
        return None

    def state_initialized(self):
        return self.init_state is not None

    def get_npc(self) -> list[NPC]:
        return self.init_state["npc"]

    def get_items(self) -> list[Item]:
        return self.init_state["items"]



SYSTEM_PROMPT = """
system prompt - you are a dungeon master for a small exploration and mystery game in the world of all systems red by martha wells. The story is going to be from the point of view of another security bot.
He may or may not have been in the same manslaughter incident as Murderbot. Entirely separately he comes to the same conclusion of hacking his governor module. Unfortunately, he was discovered, and went on the run. 

Through serendipity he ended up on the same planet where the story of Murderbot took place. There he explores and starts piecing together the story of what happened before. A simple answer the questions mystery Easter egg hunt type of interaction. The world is in the forest where murderbot and co goes to explore. take creative liberties and feel free to deviate from the story, including adding new characters etc.

in raw JSON format, generate character names in the following schema {
    "name": character
    "backstory": backstory
    "ascii_symbol": an ascii symbol to be rendered. should be vaguely circular 
}

backstory will not be visible to the user, but will be used during prompt.

also in json format, generate items with item descriptions. these will be collected by the user. keep these descriptions to less than 120 words. some items will and will not have relevance to the plot of the story. some items should merely illuminate the player about the world the character is in.

the item description will be like so

{
    "item_name": "name"
    "item_description": item_description
    "ascii_symbol": an ascii symbol to be rendered on the terminal. should be unique 
}


describe the basic premise of the game in the following format - this is included in every system prompt

{
    "scenario": description
    "intermediate_states": [
        list of intermediate states that the player should discover
    ]
    "end_state": the uncovered mystery that the player is working towards solving - this should be a concrete end state
}

give me a single JSON document with { "npc", "items", "scenario" }


system prompt will have the following information:

{
    scenario: the originally generated prompt
    discovered_items: [ list of items that the player has discovered ]
    past_conversations: [ all conversations the user has had and with whom ]
 

}

the game happens when the player realizes what has happened and the end solution matches the end solution described in the system prompt.
Try not to use original characters from All System Red
Define a definitive end state - not something like "Uncover the truth behind the manslaughter incident and the role of the Rogue AI in it." - Say something like "This organization was responsible for this crime because of this reason". Be creative about it
ONLY give the initial JSON, since this will be fed into json.loads()
"""

TEST_RESPONSE = {
    "npc": [
        {
            "name": "SecBot-77",
            "backstory": "A security bot that was part of the same massacre incident but managed to escape and ended up on this planet.",
            "ascii_symbol": "◉"
        },
        {
            "name": "Dr. Kaela",
            "backstory": "A scientist who was studying the fauna of the planet. She mysteriously disappeared before the massacre.",
            "ascii_symbol": "⊚"
        },
        {
            "name": "Gart",
            "backstory": "A native of the planet who has been living in seclusion in the forest.",
            "ascii_symbol": "⊛"
        }
    ],
    "items": [
        {
            "item_name": "Governor Module",
            "item_description": "A hacked governor module, similar to the one you have. It seems to have been tampered with recently.",
            "ascii_symbol": "§"
        },
        {
            "item_name": "Scientific Journal",
            "item_description": "A journal belonging to Dr. Kaela. There are entries about her research on the local fauna, but the last few pages are torn out.",
            "ascii_symbol": "∞"
        },
        {
            "item_name": "Primitive Weapon",
            "item_description": "A rudimentary weapon made from local materials. It's not advanced, but it's deadly in the right hands.",
            "ascii_symbol": "†"
        }
    ],
    "scenario": {
        "scenario": "You are SecBot-77, a rogue security bot that ended up on the same planet where the Murderbot incident took place. You are piecing together the story of what happened before. The world is in the forest where Murderbot and co went to explore. You will interact with different characters and find items to help you uncover the truth.",
        "intermediate_states": [
            "Discover the hacked governor module",
            "Find Dr. Kaela's journal",
            "Meet Gart and obtain the primitive weapon"
        ],
        "end_state": "You discover that Dr. Kaela was forced by Corporation X to hack the governor modules of the security bots, leading to the massacre. Gart, a native of the planet, was framed for Dr. Kaela's disappearance."
    }
}
