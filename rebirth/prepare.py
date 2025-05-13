"""This file prepare in advance everything will have in `main`."""

import os
import pathlib
from typing import Literal

import i18n

PROJECT: pathlib.Path = pathlib.Path(__file__).parent

def _read(key: str, read_type = Literal["scene", "event"]) -> str:
    """Read the ASCII of the scene."""
    try:
        f = open(os.path.join(PROJECT, "assets", read_type, key), "r", encoding="utf-8")
    except FileNotFoundError as err:
        raise FileNotFoundError(f"Cannot find scene '{key}'. Please reinstall.") from err
    res: str = f.read()
    f.close()
    return res

def prepare_scene() -> dict:
    """Return prepared scenes in dict format.

    Returns:
        dict: list of scenes, key are their names.
    """
    return {
        name: _read(f"{name}.txt", "scene") for name in (
            "bedroom", "kitchen", "forest", "camp", "graveyard", "tomb", "lake", "road", "castle",
            "mirror", "dead", "end", "title"
        )
    }

def prepare_event() -> dict:
    """Return prepared events in `inspect` in dict format.

    Returns:
        dict: list of events, key are their names.
    """
    return {
        name: _read(f"{name}.txt", "event") for name in (
            "note", "newspaper", "clean", "crown", "shield", "sword", "bow", "cloak", "zombie"
        )
    }

def prepare_i18n(locale: str = "en"):
    """Set the i18n from written yml."""
    i18n.config.set("locale", locale)
    i18n.load_path.append(os.path.join(PROJECT, "assets", "i18n"))
    i18n.load_everything()
