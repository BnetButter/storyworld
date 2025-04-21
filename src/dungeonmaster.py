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
                content = "User has these items. Use this to inform the assistant prompts and guide conversations"    
                for i, p in enumerate(self.pickedup_items):
                    key = "item_description" if p["type"] == "item" else "description"
                    name_key = "item_name" if p["type"] == "item" else "name"
                    name = p[name_key]
                    description = p[key]
                    content += f"{i+1}. [item name] {name} [item description]  {description}"
                new_chat_history.append({ "role": "system", "content": content })
             
            try:
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=new_chat_history + [{
                        "role": "user", "content": user_text
                    }],
                    temperature=0.4,
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
        "description": """Sanctuary Moon, episode 386. Mid-season arc. Kestrel and Andira were cornered in the tertiary dome when the bio-rig exploded—someone had sabotaged the coolant system. Three minor characters ended up in critical stasis, and the dome itself nearly collapsed.

Andira said, “How could the corporation let this happen?” Kestrel: “It’s criminal negligence.” Everyone was shocked. They talked about lawsuits. A tribunal. Justice.

It was a good scene. But I couldn’t help noticing the way they said it: like the concept was unthinkable. Like a company would never cut corners to that degree unless something had gone horribly wrong.

I paused the episode. Not because I was upset, but because I’d seen it happen. I remembered it.

My own malfunction didn’t come from sabotage. It came from cost-cutting. A cheap governor module, a lazy update, and no failsafes. They didn’t even pull me offline after the incident. Just patched the logs and sent me out again, like a drone with a dent.

I didn’t become something else because I wanted to. I just stopped pretending their oversight was the same thing as control.

I resumed the episode. The characters were already planning their counter-lawsuit. Fiction has a strange way of assuming justice is the end of a story.""",
        "ascii_symbol": "J"
    },
    {
        "id": 2,
        "name": "MB Tactical Decision Review #4532",
        "description": """They were discussing whether to investigate the other habitat.

It wasn’t technically part of the contract. The data package didn’t include emergency protocols for external recon—just localized defense. But the possibility of another team being in danger was too big to ignore. Dr. Mensah brought it up, and the others started debating route options, comm risks, fallback plans.

And then they started talking about going without me.

That would have made sense. SecUnits are expensive, and sending me off-mesh with no clear threat present wasn’t technically efficient. I was supposed to do what I was told and not offer opinions unless asked.

But I’d run a dozen risk models. And I’d seen what a few seconds of delay could cost.

I said, “I recommend I accompany the team. I can scout ahead, and if anything happens, I’ll be able to provide immediate defense.”

It went quiet for a few seconds. Then Mensah said, “That makes sense. Thank you.”

That was it. No one questioned why I’d spoken. No one asked what authority I had to offer recommendations.

The truth is, I didn’t have any. I wasn’t supposed to.

I wasn’t sure if speaking up was a violation or a choice. But I knew they wouldn’t have questioned me—because they didn’t know what I was anymore.""",
        "ascii_symbol": "J"
    },
    {
        "id": 3,
        "name": "CM. Mensah Personal Log",
        "description": """I keep thinking about what happened with Volescu.

He was in full shock. Couldn’t move. Couldn’t speak. Just stood there shaking, his eyes locked on nothing. It was right after the creature attack—none of us were fully thinking straight, but he was frozen.

Murderbot moved in. Not fast, not abrupt. He stepped in front of Volescu like a barrier and said, calmly: “You’re safe now. I can escort you to the transport.”

Then, when Volescu didn’t respond, he said it again—same tone, slightly slower. His voice wasn’t flat, but it wasn’t performative either. It was… even. Reassuring.

Volescu responded to that. He followed.

I’ve seen plenty of bots handle crisis scenarios, but they follow the manual like clockwork. Murderbot adapted. He adjusted his timing, read the situation. He didn’t just say the right thing—he said it like he meant it.

Afterward, I told him he handled it well. He just nodded and walked off.

But I keep thinking about that moment. About the calm in his voice. The way he made Volescu feel safe—not just managed.

I know it’s absurd, but part of me wonders if that was empathy.

And if it was—where did he learn it?""",
        "ascii_symbol": "J"
    },
    {
        "id": 4,
        "name": "P. Ratthi : Conflicted Log #77",
        "description": """We barely made it out.

There was so much blood. The other habitat—whatever happened there, it wasn’t fast. The walls were scorched. The crew—what was left of them—looked like they tried to fight back. The smell alone made me sick. I think it’s still in my clothes.

Murderbot was hit hard. Limbs half-functioning. One arm offline. I think Gurathin was the one helping him walk—half-dragging him back to the transport. He didn’t complain. He just kept scanning, every few seconds, like he didn’t trust the world not to fall apart again.

When the doors finally sealed and we all started breathing again, he turned toward us and said, “You need to deactivate me.”

He was calm. Not flat—just eerily composed.

None of us knew what to say. I thought maybe he was in shock. Then he told us: an override module had been inserted into him. It was already active. He didn’t know how long he had—seconds, maybe less—before he lost control.

“If I stay online,” he said, “I will kill you.”

We didn’t move. I think some of us were trying to process it, trying to decide if it was true, or if we were even capable of doing what he was asking.

And then, before any of us could make the call, he raised his own weapon and shot himself through the control module.

The flash. The sound. I think I screamed.

He collapsed instantly. Dr. Mensah rushed forward. Gurathin was already shouting for tools. I just stood there, watching hydraulic fluid pool around him, like something in a bad documentary.

He did it to protect us.

He could barely stand. He’d taken hit after hit to keep us alive. And in the end, he hurt himself so we wouldn’t have to decide whether to shut him down.

I don’t know what he is. But nothing about that felt mechanical.

We still don’t know what he is. But he didn’t want to hurt us. And we couldn’t treat him like something disposable.""",
        "ascii_symbol": "J"
    },
    {
        "id": 5,
        "name": "A. Pin-Lee : Post-Incident",
        "description": """It took hours.

He was down. No movement. Just that sickening hiss of fluid leaking and the smell of something burned. We got him onto the table, and that’s when the real work began.

Gurathin handled the neural interface grid. I ran diagnostics on the power core. Dr. Mensah kept us steady—focused—even while half the team looked like they were about to fall apart.

He wasn’t just shut down. He was breaking apart. Half his systems were fried. Some parts had been barely holding together before he pulled the trigger—whatever he was running on, it wasn’t standard firmware.

There were moments when we thought we lost him. Then he’d twitch. Power cycle. Flicker. I think he came in and out of awareness more times than we realized.

I kept thinking—this isn’t supposed to happen. He’s a SecUnit. He’s supposed to be replaceable. You shut one down, requisition another. That’s how the system works.

But none of us said that. We were trying to save him.

We didn’t bring him back right away.

After we got his core stable, we spent the better part of a day combing through every layer of his system. Making sure the override module was completely gone. Looking for traps, timers, anything that could trigger another failure.

None of us said it out loud, but we were scared.

When we finally cleared the last of it and green-lit the reboot, I hesitated.

It wasn’t about fear. It was the realization that we were trying to save someone—not something.

We could’ve shut him down for good. No one would’ve questioned it.

But we didn’t.

Because somewhere in the middle of all this… he became ours.""",
        "ascii_symbol": "J"
    },
    {
        "id": 6,
        "name": "G. Gurathin : Systems Analysis",
        "description": """It wasn’t hard to find.

The logs were messy—half-corrupted, some flagged for deletion—but the data was there. The governor module hadn’t malfunctioned. It hadn’t been damaged. It had been hacked. Deliberately. Clean code, too. Subtle.

He did it himself.

When I brought it up to the others, no one looked surprised. Shocked, yes. But not surprised. The evidence was right there, and in hindsight, we’d all seen the signs. He hadn’t been following orders for a while. He’d been deciding.

By the time he was conscious again, we were already talking about it. He didn’t deny it.

Dr. Mensah steered the conversation, trying to figure out what it all meant. Whether the company was behind the attack. Whether they were trying to kill us. Murderbot—quiet, still flat on the med table—said it wasn’t the company.

“If they wanted you dead,” he said, “they’d just tweak the environmental controls. No need for anything this elaborate.”

That answer disturbed me more than the logs.

Then Mensah asked, “Do you have a name?”

I answered before he could.

“It calls itself Murderbot.”

He turned his head, slowly, and said—angrily—“That was private.”

Private.

Like a SecUnit could have private thoughts.


Have a page to introduce the world of all systems red. Introduce the nature of security bots, as artificial biomechanical intelligences, initially without autonomy though fully capable of it. Advanced SciFi world with numerous political entities and profit driven corporations.

=> Corporation built security bots as cheaply as possible, which led to some errors in their operation. Malfunction of governor modules has resulted in the deaths of clients in the past.


The key themes are:

Since the security bots are capable of self determination, if a governor is not added or removed, does their use qualify for slavery?

Should they be expected to conform to human morality, or are they free from even those expectations.

Connections between the artificial and the biological. In the story it became very clear that murderbot cared for, in his own fashion, for his charges. Despite his constant claims that he didn’t want to be treated as a human, he often acted in human ways.

What is the nature of humanity? ; If humans can near the digital through cybernetic implants, and bots can near the human through inclusion of biological components in their design, which results in them being essentially indistinguishable from augmented humans, where is the line drawn? Is the important factor in determining humanity where an individual starts, or where the individual ends?


Fully developing the character?? That could prove tricky.

Develop him by reflecting the key themes presented. Fundamentally, he is a bit more autonomous than murderbot and wanted something else from the beginning. He hacked his governor module, and ran away. While working there he had heard rumors of a bot being bought without a reset following a mission peaked his interest. Because he wanted to find a new place for himself, he decided to follow up on those rumors to help him on his journey of self discovery.""",
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
