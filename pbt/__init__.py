from pbt import _state
from pbt._state import LOADED_PROFILES
from pbt.error import PbtError
from pbt._fbs import get_core_settings, get_default_profiles
from pbt._settings import load_settings, expand_placeholders, expand_all_placeholders
from pbt.paths import (
    fix_path,
    get_settings_paths,
    get_configurable_settings,
    get_project_root,
)
from pbt._variables import resolve_variables
from os.path import abspath

"""
pbt populates SETTINGS with the current build settings. A typical example is
SETTINGS['app_name'], which you define in build_system/build/settings/base.json.
"""
SETTINGS = _state.SETTINGS


def init(project_dir):
    """
    Call this if you are invoking neither `pbt` on the command line nor
    pbt.cmdline.main() from Python.
    """
    SETTINGS.update(get_core_settings(abspath(project_dir)))
    SETTINGS.update(get_configurable_settings())
    for profile in get_default_profiles():
        activate_profile(profile)


def activate_profile(profile_name):
    """
    By default, pbt only loads some settings. For instance,
    build_system/build/settings/base.json and .../`os`.json where `os` is one of "mac",
    "linux" or "windows". This function lets you load other settings on the fly.
    A common example would be during a release, where release.json contains the
    production server URL instead of a staging server.
    """
    LOADED_PROFILES.append(profile_name)
    json_paths = get_settings_paths(LOADED_PROFILES)
    project_dir = get_project_root()
    settings = get_core_settings(project_dir)
    SETTINGS.update(load_settings(json_paths, settings))
    #resolve_variables()
    expand_all_placeholders(SETTINGS)
