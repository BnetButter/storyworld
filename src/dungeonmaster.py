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
            model="o3-mini",  # Specify the model you're using
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "generate the initial world state in JSON according to the specified format"}
            ],
            timeout=20.0  # Set timeout in seconds
        )

        # Parse the response and extract the JSON output
        game_state = json.loads(response.choices[0].message.content.strip())
        return game_state

    except Exception as e:
        return TEST_RESPONSE


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

        self.pickedup_items = []

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
            
            for journal in JOURNALS:
                symbol = journal["ascii_symbol"]
                name = journal["name"]
                y, x = world.random_valid_point(self.world)
                self.world[y][x] = ord(symbol)
                self.location_index[y,x] = { "type": "journal" } | journal
    

            self.init_state = game_state
        threading.Thread(target=init).start()
    
    def add_item(self, item):
        if item not in self.pickedup_items:
            self.pickedup_items.append(item)
    
    def has_journal(self, num):
        for f in self.pickedup_items:
            if f["type"] == "journal" and f["id"] == num:
                return True
        return False

    def converse_with_npc(self, npc: NPC) -> Callable:
        if "chat_history" not in npc:
            chat_history = npc["chat_history"] = [
                {"role": "system", "content": SYSTEM_PROMPT + f"{self.init_state}"},
                {"role": "system", "content": f"You are {npc['name']}. Respond in text, not JSON. Keep to 150 word responses or less"},
                {"role": "user", "content": f"Introduce yourself"}
            ]
        else:
            chat_history = npc["chat_history"]
        
        def prompt(user_text) -> Generator:
            for line in chat_history:
                logger.debug(line["content"])

            if len(chat_history) >= 5:
                new_chat_history = list(chat_history[1:])
            else:
                new_chat_history = list(chat_history)
            
            if self.pickedup_items:
                content = f"User has these items. Use this to inform the assistant prompts and guide conversations. You are {npc['name']}. Do not break character."    
                for i, p in enumerate(self.pickedup_items):
                    key = "item_description" if p["type"] == "item" else "description"
                    name_key = "item_name" if p["type"] == "item" else "name"
                    name = p[name_key]
                    description = p[key]
                    content += f"{i+1}. <item><item name>{name}</item name> <item description>{description}</item description></item>"
                new_chat_history.append({ "role": "system", "content": content })
             
            try:
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=new_chat_history + [{
                        "role": "user", "content": user_text
                    }],
                    temperature=1,
                    max_tokens=4096,
                    stream=True
                )

                full_reply = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        partial = chunk.choices[0].delta.content
                        full_reply += partial
                        yield partial  # stream to caller
                chat_history.append({"role": "user", "content": user_text})
                chat_history.append({"role": "assistant", "content": full_reply})
            
            except Exception as e:
                yield "[Error occurred]"
        
        return prompt


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
    "ascii_symbol": an ascii symbol to be rendered. must be a single char
}

backstory will not be visible to the user, but will be used during prompt.

also in json format, generate items with item descriptions. these will be collected by the user. keep these descriptions to less than 120 words. some items will and will not have relevance to the plot of the story. some items should merely illuminate the player about the world the character is in.

the item description will be like so

{
    "item_name": "name"
    "item_description": item_description
    "ascii_symbol": an ascii symbol to be rendered on the terminal. should be unique. single char
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

JOURNALS = [
    {
        "id": 1,
        "name": "MB Archive #4481 : Pre-Expedition Downtim",
        "description": """Pre-expedition downtime. He was watching episode 386 of Sanctuary moon. In it corporate greed and neglect led to a disaster, which reminded him of his governor malfunction.""",
        "ascii_symbol": "J"
    },
    {
        "id": 2,
        "name": "MB Tactical Decision Review #4532",
        "description": """Murderbot acts somewhat autonomously and recommends a safer course of action when visiting the other habitat when they are planning the mission.""",
        "ascii_symbol": "J"
    },
    {
        "id": 3,
        "name": "CM. Mensah Personal Log",
        "description": """Volescue had been in shock after the fauna attack. Murderbot acted empathetically to help talk him out of that situation""",
        "ascii_symbol": "J"
    },
    {
        "id": 4,
        "name": "P. Ratthi : Conflicted Log #77",
        "description": """ P. Ratthi POV
They left the slaughter at the other facility behind. Murderbot said that an override module had been inserted and he would be forced to attack him. They froze, murderbot shot himself, to protect the humans""",
        "ascii_symbol": "J"
    },
    {
        "id": 5,
        "name": "A. Pin-Lee : Post-Incident Log #88",
        "description": "SecUnits are supposed to be disposable. But we all accepted that he wasn’t, and worked to save him.",
        "ascii_symbol": "J"
    },
    {
        "id": 6,
        "name": "G. Gurathin : Systems Analysis Debrief #55",
        "description": "I found that he hacked his governor module in his logs. He killed ~57 miners before, and calls himself murderbot. When the conversation turned to his name, I answered murderbot for him.",
        "ascii_symbol": "J"
    }
]

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
