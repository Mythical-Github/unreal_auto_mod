import threading
import time

import script_states
from enums import ScriptStateType


def constant_thread_runner(tick_rate: float = 0.01):
    while run_constant_thread:
        time.sleep(tick_rate)
        constant_thread_logic()


def constant_thread_logic():
    script_states.routine_checks(ScriptStateType.CONSTANT)


def start_constant_thread():
    global constant_thread
    global run_constant_thread
    run_constant_thread = True
    constant_thread = threading.Thread(target=constant_thread_runner, daemon=True)
    constant_thread.start()


def constant_thread():
    if script_states.is_script_state_used(ScriptStateType.CONSTANT):
        start_constant_thread()
        print('constant thread started')
    else:
        print('constant thread not used in config, so not activated')         


def stop_constant_thread():
    if script_states.is_script_state_used(ScriptStateType.CONSTANT):
        global run_constant_thread
        run_constant_thread = False