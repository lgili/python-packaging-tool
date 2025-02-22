from ppt.resources import copy_with_filtering
from os.path import join, dirname
from tempfile import TemporaryDirectory
from unittest import TestCase

import ppt
import ppt.builtin_commands
import ppt._state as pbt_state
from ppt import platform
import json


class PbtTest(TestCase):
    def setUp(self):
        super().setUp()
        # Copy template project to temporary directory:
        self._tmp_dir = TemporaryDirectory()
        self._project_dir = join(self._tmp_dir.name, "project")
        project_template = join(
            dirname(ppt.builtin_commands.__file__), "project_template"
        )
        replacements = {"python_bindings": "PyQt5"}
        copy_with_filtering(
            project_template,
            self._project_dir,
            replacements,
            [
                join(project_template, "src" "${package_name}"),
            ],
        )
        self._update_settings("base.json", {"app_name": "MyApp"})
        # Save ppt's state:
        self._state_before = pbt_state.get()
        self._platform_before = platform.get()

    def init_pbt(self, platform_name=None):
        if platform_name is not None:
            platform.restore(platform_name, None, None)
        ppt.init(self._project_dir)

    def tearDown(self):
        platform.restore(*self._platform_before)
        pbt_state.restore(*self._state_before)
        self._tmp_dir.cleanup()
        super().tearDown()

    def _update_settings(self, json_name, dict_):
        settings = self._read_settings(json_name)
        settings.update(dict_)
        self._write_settings(json_name, settings)

    def _read_settings(self, json_name):
        with open(self._json_path(json_name)) as f:
            return json.load(f)

    def _write_settings(self, json_name, dict_):
        with open(self._json_path(json_name), "w") as f:
            json.dump(dict_, f)

    def _json_path(self, name):
        return join(self._project_dir, "build_system", "build", "settings", name)
