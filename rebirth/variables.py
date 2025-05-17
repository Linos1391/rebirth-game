"""This python stores all objects that contributes in the gameplay"""

import os
import json

try: # We all know why
    from . import prepare
except ImportError:
    import prepare

# work like self variables
isExit: bool = False
isPlaying: bool = False
currentPlayerHealth: int = 6 # because automatically minus 1 when `_heading_health()`` called
currentNarrative: str = "text.start.play.content"
currentEnemyHealth: int = 2

# Constants
SCENE: dict = prepare.prepare_scene()
EVENT: dict = prepare.prepare_event()

FIRST: list = ["kitchen", "forest", "camp", "graveyard", "tomb", "lake", "road", "castle"]
ENEMY: dict = {
    "forest": [["zombie"], ["kick"]],
    "graveyard": [["zombie"], ["uppercut"]],
    "lake": [["zombie", "zombie", "zombie"], [None, "jab", "kick"]],
    "road": [["shield", "sword", "bow"], [None, None, "uppercut"]],
}
CONTROL: dict = {
    "bedroom": {
        "move": ["kitchen"],
    },
    "kitchen": {
        "inspect": ["newspaper"],
        "move": ["bedroom", "forest"],
    },
    "forest": {
        "move": ["kitchen"],
        "fight": ["jab", "uppercut", "kick"],
        "defend": ["block", "dodge"],
    },
    "forest_after": {
        "move": ["kitchen", "camp", "graveyard", "lake"],
    },
    "camp": {
        "inspect": ["newspaper", "note"],
        "move": ["forest"],
    },
    "graveyard": {
        "move": ["forest"],
        "fight": ["jab", "uppercut", "kick"],
        "defend": ["block", "dodge"],
    },
    "graveyard_after": {
        "move": ["forest", "tomb"],
        },
    "tomb": {
        "inspect": ["crown"],
        "move": ["graveyard"],
    },
    "lake": {
        "move": ["forest"],
        "fight": ["jab", "uppercut", "kick"],
        "defend": ["block", "dodge"],
    },
    "lake_after": {
        "inspect": ["clean"],
        "move": ["forest", "road"],
    },
    "lake_clean": {
        "move": ["forest", "road"],
    },
    "road": {
        "inspect": ["outsiders"],
        "move": ["lake", "castle"],
    },
    "road_greet": {
        "fight": ["jab", "uppercut", "kick"],
        "defend": ["block", "dodge"],
    },
    "road_fight": {
        "fight": ["jab", "uppercut", "kick"],
        "defend": ["block", "dodge"],
    },
    "castle": {
        "inspect": ["cloak"],
        "move": ["road"],
    },
}
REQUIREMENT: dict = {
    "opt_king": False,
    "opt_outsider": False,
    "opt_zombie": False
}

# Method
def check_setting() -> bool:
    """Check if all endings have achieved."""
    f = open(os.path.join(prepare.PROJECT, "assets", "setting.json"), mode="r", encoding="utf-8")
    data: dict = json.load(f)
    f.close()
    return all(data.values())

def fixed_setting(ending: str):
    """One has to do the work, so I choose you, Pikachu!"""
    path: str = os.path.join(prepare.PROJECT, "assets", "setting.json")

    f = open(path, mode="r", encoding="utf-8")
    data: dict = json.load(f)
    f.close()

    if ending == "reset":
        data = {"1": False, "2": False, "3": False}
    else:
        data.update({ending: True})
    f = open(path, mode="w", encoding="utf-8")
    json.dump(data, f, indent=4)
    f.close()

def control_get(scene: str, event: str | None = None) -> dict:
    """A better get."""
    if (event == "greet") or (scene == "road" and event == "defend"):
        return CONTROL.get(f"{scene}_fight")
    elif (event in (None, "first", "default", "defend")) or \
            (scene in ("forest", "lake", "graveyard") and event == "fight"):
        return CONTROL.get(scene)
    else:
        return CONTROL.get(f"{scene}_{event}")
