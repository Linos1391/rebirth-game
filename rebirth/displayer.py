# pylint: disable=no-member
"""The function to display stuff."""

from threading import Thread
from random import randint
import time
import curses

import i18n

try: # We all know why
    from . import variables
except ImportError:
    import variables

def _heading_health(stdscr: curses.window):
    variables.currentPlayerHealth -= 1

    win = stdscr.subwin(1, curses.COLS - 62, 2, 61)
    win.clear()
    win.addstr(f"{i18n.t("text.heading.health")}: {variables.currentPlayerHealth*"█"}")
    win.refresh()
    del win

    if variables.currentPlayerHealth == 0:
        variables.currentNarrative = "text.ending.0"
        variables.isPlaying = False

def _heading_time(stdscr: curses.window):
    win = stdscr.subwin(1, curses.COLS - 62, 3, 61)
    win.clear()
    m, s = 0, 0
    while variables.isPlaying:
        win.clear()
        win.addstr(f"{i18n.t("text.heading.time")}: \
{str(m) if m > 9 else f"0{m}"}m\
{str(s) if s > 9 else f"0{s}"}s")
        win.refresh()

        time.sleep(1) # Delay 1 sec.
        s += 1
        if s == 60:
            m += 1
            s = 0

def _control_panel(win: curses.window, controls: dict, chosen: list):
    win.clear()
    if controls.get("inspect") == ["cloak"]:
        controls.update(
            {"inspect": [k if v else "opt_unknown" for k, v in variables.REQUIREMENT.items()]}
        )

    for i, m in enumerate(controls.keys()):
        if i == chosen[0]:
            win.addstr(f"\n[X] {i18n.t(f"text.control.{m}")}", curses.A_STANDOUT)
            if chosen[1] != -1:
                for j, n in enumerate(controls.get(m)):
                    if j == chosen[1]:
                        win.addstr(f"\n  [X] {i18n.t(f"text.control.{n}")}", curses.A_STANDOUT)
                    else:
                        win.addstr(f"\n  [X] {i18n.t(f"text.control.{n}")}")
        else:
            win.addstr(f"\n[X] {i18n.t(f"text.control.{m}")}")
    win.refresh()

def _event_panel(stdscr: curses.window, events: list[str], is_enemy: bool = False):
    if events == ["outsiders"]:
        events = ["shield", "sword", "bow"]
    for index, event in enumerate(events):
        win = stdscr.subwin(8, 16, 15, 1+index*16)
        win.border()
        win.refresh()
        del win

        win = stdscr.subwin(6, 14, 16, 2+index*16)
        win.clear()
        if is_enemy and index == 0:
            win.addstr(variables.EVENT.get(event), curses.A_STANDOUT)
        else:
            win.addstr(variables.EVENT.get(event))
        win.refresh()
        del win

def display_start(stdscr: curses.window):
    """Show the start scene."""
    nar_key: str = variables.currentNarrative
    display_scene(stdscr, "title")

    win = stdscr.subwin(curses.LINES - 6, curses.COLS - 62, 6, 61)
    win.addstr(f"{i18n.t(nar_key)}\n")
    win.refresh()

    # Create a new window.
    loc = win.getyx()
    win = stdscr.subwin(curses.LINES-6-loc[0], curses.COLS-62-loc[1], 6+loc[0], 61)
    del loc

    # Display the panel.
    chosen: int = [-1, -1]
    while True:
        langs: list = []
        win.clear()
        for i, m in enumerate(["play", "reset", "language", "exit"]):
            if i == chosen[0]:
                win.addstr(f"\n[X] {i18n.t(f"text.start.{m}.heading")}", curses.A_STANDOUT)
                if i == 2 and chosen[1] != -1:
                    cur_lang: str = i18n.get("locale")
                    for j, n in enumerate(i18n.translations.container.keys()):
                        i18n.set("locale", n)
                        langs.append(n)
                        if j == chosen[1]:
                            win.addstr(f"\n  [X] {i18n.t("text.lang")}", curses.A_STANDOUT)
                        else:
                            win.addstr(f"\n  [X] {i18n.t("text.lang")}")
                    i18n.set("locale", cur_lang)
            else:
                win.addstr(f"\n[X] {i18n.t(f"text.start.{m}.heading")}")
        win.refresh()

        match stdscr.getch():
            case curses.KEY_UP:
                if chosen[1] == -1 and chosen[0] > 0:
                    chosen[0] -= 1
                elif chosen[1] not in (-1, 0):
                    chosen[1] -= 1
            case curses.KEY_DOWN:
                if chosen[1] == -1 and chosen[0] != 3:
                    chosen[0] += 1
                elif chosen[1] not in (-1, len(langs)-1):
                    chosen[1] += 1
            case curses.KEY_LEFT:
                if chosen[0] != 2:
                    continue
                chosen[1] = -1
            case curses.KEY_RIGHT:
                if chosen[0] != 2:
                    continue
                if chosen[1] == -1:
                    chosen[1] = 0
            case curses.KEY_ENTER | 10 | 13:
                match chosen[0]:
                    case 0:
                        variables.isPlaying = True
                    case 1:
                        variables.currentNarrative = "text.start.reset.content"
                        variables.fixed_setting("reset")
                    case 2:
                        if chosen[1] == -1:
                            continue
                        i18n.set("locale", langs[chosen[1]])
                        variables.currentNarrative = "text.start.play.content"
                    case 3:
                        variables.isPlaying = True
                        variables.isExit = True
                break

def display_scene(stdscr: curses.window, scene: str):
    """Change into new scene."""
    # Remove first label.
    try:
        variables.FIRST.remove(scene)
    except ValueError:
        pass

    win = stdscr.subwin(22, 58, 1, 1) # Show a scene in 22x57 (minus the \n in the end of line)
    win.clear()
    win.addstr(variables.SCENE.get(scene))
    win.refresh()
    del win

    if scene in ("title", "dead", "end"): #Ignore these
        return
    win = stdscr.subwin(1, curses.COLS - 62, 1, 61) # This show the location's name in the heading
    win.clear()
    win.addstr(i18n.t(f"text.control.{"lake" if scene == "mirror" else scene}").upper())
    win.refresh()
    del win

def display_paused_narrative(stdscr: curses.window, ending: str | None = None):
    """Pause for special narrative."""
    win = stdscr.subwin(curses.LINES - 6, curses.COLS - 62, 6, 61)
    win.clear()
    if ending:
        win.addstr(f"{i18n.t("text.ending.heading")} {ending}\n\n")
    win.addstr(f"{i18n.t(variables.currentNarrative)}\n\n{i18n.t("text.ending.continue")}")
    win.refresh()
    win.getkey()

def display_narrative(stdscr: curses.window):
    """Create the narrative screen on the lower right side."""
    nar_key: str = variables.currentNarrative
    _, _, cur_scene, _event = nar_key.split(".", 3)

    controls: dict = variables.control_get(cur_scene, _event.split(".")[0])
    del _event
    if "inspect" in list(controls.keys()):
        if controls.get("inspect")[0] in ("opt_unknown", "opt_king", "opt_outsider", "opt_zombie"):
            controls.update({"inspect": ["cloak"]}) # Return to normal.
        _event_panel(stdscr, controls.get("inspect"))
    elif variables.ENEMY.get(cur_scene):
        _event_panel(stdscr, variables.ENEMY.get(cur_scene)[0], True)

    win = stdscr.subwin(curses.LINES - 6, curses.COLS - 62, 6, 61)
    win.addstr(f"{i18n.t(nar_key)}\n")
    win.refresh()

    # Create a new window for control panel
    loc = win.getyx()
    win = stdscr.subwin(curses.LINES-6-loc[0], curses.COLS-62-loc[1], 6+loc[0], 61)
    del loc

    # Display the control panel.
    chosen: list[int] = [-1, -1]
    while True:
        # Display the control panel.
        _control_panel(win, controls, chosen)
        match stdscr.getch():
            case curses.KEY_UP:
                if chosen[1] == -1 and chosen[0] > 0:
                    chosen[0] -= 1
                elif chosen[1] not in (-1, 0):
                    chosen[1] -= 1
            case curses.KEY_DOWN:
                if chosen[1] == -1 and chosen[0] != len(controls)-1:
                    chosen[0] += 1
                elif chosen[1] not in (-1, len(list(controls.values())[chosen[0]])-1):
                    chosen[1] += 1
            case curses.KEY_LEFT:
                if chosen[0] == -1:
                    continue
                chosen[1] = -1
            case curses.KEY_RIGHT:
                if chosen[0] == -1:
                    continue
                if chosen[1] == -1:
                    chosen[1] = 0
            case curses.KEY_ENTER | 10 | 13: # Also think of `\n` and `\r`
                if chosen[1] == -1:
                    continue

                match list(controls.keys())[chosen[0]]:
                    case "inspect":
                        event: str = controls.get("inspect").pop(chosen[1])
                        if variables.CONTROL.get(cur_scene).get("inspect") == []:
                            variables.CONTROL.get(cur_scene).pop("inspect")

                        match event:
                            case "outsiders": # Special for fight outsiders
                                variables.currentNarrative = "text.location.road.greet"
                            case "clean": # special case for clean scene
                                cur_scene = "mirror"
                                variables.currentNarrative = "text.location.lake.clean"
                                variables.REQUIREMENT.update({"opt_zombie": True})
                            case "newspaper":
                                variables.currentNarrative = f"text.location.{cur_scene}.newspaper"
                                match cur_scene:
                                    case "kitchen":
                                        variables.REQUIREMENT.update({"opt_outsider": True})
                                    case "camp":
                                        variables.REQUIREMENT.update({"opt_king": True})
                            case "opt_unknown":
                                if any(variables.REQUIREMENT.values()):
                                    controls.get("inspect").insert(chosen[1], event)
                                    continue # Ignore if player choose `???`
                                else:
                                    variables.currentNarrative = "text.ending.1"
                                    variables.isPlaying = False
                                    break
                            case "opt_king" | "opt_outsider":
                                variables.currentNarrative = "text.ending.2"
                                variables.isPlaying = False
                                break
                            case "opt_zombie":
                                variables.currentNarrative = "text.ending.3"
                                variables.isPlaying = False
                                break
                            case _:
                                variables.currentNarrative = \
f"text.location.{variables.currentNarrative.split(".")[2]}.{event}"
                        display_scene(stdscr, cur_scene)
                        break
                    case "move":
                        scene: str = list(controls.values())[chosen[0]][chosen[1]]
                        # I know this not so great.
                        if scene in variables.FIRST:
                            event = "first"
                        elif variables.ENEMY.get(scene) == [[], []]:
                            event = "after"
                        else:
                            event = "default"
                        variables.currentNarrative = f"text.location.{scene}.{event}"
                        display_scene(stdscr, scene)
                        break
                    case "fight":
                        action: str = list(controls.values())[chosen[0]][chosen[1]]
                        cur_enemy: str = variables.ENEMY.get(cur_scene)[0][0]
                        if variables.currentEnemyHealth == 0: # Next one
                            match cur_enemy :
                                case "zombie":
                                    variables.currentEnemyHealth = 2
                                case "shield":
                                    variables.currentEnemyHealth = 10
                                case "sword":
                                    variables.currentEnemyHealth = 5
                                case "bow":
                                    variables.currentEnemyHealth = 5

                        if variables.ENEMY.get(cur_scene)[1][0] == action: # weakness? DIE!
                            variables.currentEnemyHealth = 0
                        else:
                            variables.currentEnemyHealth -= 1

                        if variables.currentEnemyHealth == 0: # Congratulation, you won.
                            if cur_enemy == "bow": # For special ending
                                variables.currentNarrative = "text.ending.5"
                                variables.isPlaying = False
                                break
                            variables.ENEMY.get(cur_scene)[0].pop(0)
                            variables.ENEMY.get(cur_scene)[1].pop(0)
                            if not variables.ENEMY.get(cur_scene)[0]: # Killed all.
                                variables.currentNarrative = f"text.location.{cur_scene}.after"
                            else:
                                variables.currentNarrative = f"text.location.{cur_scene}.fight.2"
                        else: # Not dead, then it hit.
                            if randint(0, 1): # 50% hit
                                variables.currentNarrative = f"text.location.{cur_scene}.fight.1"
                                _heading_health(stdscr)
                            else:
                                variables.currentNarrative = f"text.location.{cur_scene}.fight.0"
                        display_scene(stdscr, cur_scene)
                        _event_panel(stdscr, variables.ENEMY.get(cur_scene)[0], True)
                        break
                    case "defend":
                        passed: bool = False
                        match list(controls.values())[chosen[0]][chosen[1]]:
                            case "block":
                                if randint(0, 1): # 50% hit
                                    variables.currentNarrative=f"text.location.{cur_scene}.defend.1"
                                    _heading_health(stdscr)
                                else:
                                    variables.currentNarrative=f"text.location.{cur_scene}.defend.0"
                                    passed = True
                            case "dodge":
                                if randint(0, 3): # 25% dodge
                                    variables.currentNarrative=f"text.location.{cur_scene}.defend.2"
                                    passed = True
                                elif randint(0, 10): # 90% got hit once
                                    variables.currentNarrative=f"text.location.{cur_scene}.defend.3"
                                else: # Bye 2 health.
                                    variables.currentNarrative=f"text.location.{cur_scene}.defend.4"
                                    _heading_health(stdscr)
                        if passed and not randint(0, 20): # 5% counter attack when success.
                            variables.currentEnemyHealth = 0
                            variables.currentNarrative = f"text.location.{cur_scene}.defend.5"
                            display_paused_narrative(stdscr)

                            if variables.ENEMY.get(cur_scene)[0][0] == "bow": # For special ending
                                variables.currentNarrative = "text.ending.5"
                                variables.isPlaying = False
                                break
                            variables.ENEMY.get(cur_scene)[0].pop(0)
                            variables.ENEMY.get(cur_scene)[1].pop(0)
                            if not variables.ENEMY.get(cur_scene)[0]: # Killed all.
                                variables.currentNarrative = f"text.location.{cur_scene}.after"
                            else:
                                variables.currentNarrative = f"text.location.{cur_scene}.fight.2"

                        display_scene(stdscr, cur_scene)
                        _event_panel(stdscr, variables.ENEMY.get(cur_scene)[0], True)
                        break

def init_screen(stdscr: curses.window):
    """Initialize the screen."""    
    # Clear screen.
    stdscr.clear()
    stdscr.keypad(True)
    curses.noecho()

    # The window on the left side, show the scene in ASCII.
    _l = stdscr.subwin(24, 60, 0, 0)
    _l.border()
    _l.refresh()
    del _l

    # The window on the upper right side, give user the heading infomation.
    _u_r = stdscr.subwin(5, curses.COLS - 60, 0, 60)
    _u_r.border()
    _u_r.refresh()
    del _u_r

    while not variables.isPlaying:
        display_start(stdscr)
    if variables.isExit:
        return

    # Update contents.
    display_scene(stdscr, "bedroom") # Show the bedroom scene and name of the location.
    _heading_health(stdscr) # Display health
    Thread(target=_heading_time, args=[stdscr]).start()
    variables.currentNarrative = "text.location.bedroom.first"
    while variables.isPlaying:
        display_narrative(stdscr)

    # Give ending.
    match variables.currentNarrative:
        case "text.ending.0":
            display_scene(stdscr, "dead")
        case 1 | 2 | 3 | 5: #TODO - See if any donors help drawing this...
            display_scene(stdscr, "end")
    ending: str = variables.currentNarrative.split(".")[2]
    if ending in ("1", "2", "3"):
        variables.fixed_setting(ending)
    # End scene
    if variables.check_setting(): # Ending 4
        variables.currentNarrative = "text.ending.4.0"
        display_scene(stdscr, "bedroom")
        display_paused_narrative(stdscr, "4")
        variables.currentNarrative = "text.ending.4.1"
        display_scene(stdscr, "tomb")
        display_paused_narrative(stdscr, "4")
        variables.currentNarrative = "text.ending.4.2"
        display_scene(stdscr, "end")
        display_paused_narrative(stdscr, "4")
    else:
        display_paused_narrative(stdscr, ending)

def end_screen():
    """End everything."""
    variables.isPlaying = False
