

def create_mods():
    from unreal_auto_mod import (
        engine,
        enums,
        game_runner,
        packing,
        script_states,
        thread_constant,
        thread_game_monitor,
        utilities,
    )

    script_states.ScriptState.set_script_state(enums.ScriptStateType.INIT)
    thread_constant.constant_thread()
    script_states.ScriptState.set_script_state(enums.ScriptStateType.POST_INIT)
    utilities.clean_working_dir()
    engine.toggle_engine_off()
    packing.make_mods()
    if not utilities.get_skip_launching_game():
        game_runner.run_game()
        thread_game_monitor.game_monitor_thread()
        engine.toggle_engine_on()
    thread_constant.stop_constant_thread()
    utilities.clean_working_dir()
