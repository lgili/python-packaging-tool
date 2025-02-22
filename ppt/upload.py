from ppt import _server, SETTINGS
from ppt._aws import upload_file, upload_folder_contents
from ppt.error import PbtError
from ppt.platform import is_linux
from ppt.paths import project_path
from os.path import basename

import json


def _upload_repo(username, password):
    status, response = _server.post_json(
        "start_upload", {"username": username, "password": password}
    )
    unexpected_response = lambda: PbtError(
        "Received unexpected server response %d:\n%s" % (status, response)
    )
    if status // 2 != 100:
        raise unexpected_response()
    try:
        data = json.loads(response)
    except ValueError:
        raise unexpected_response()
    try:
        credentials = data["bucket"], data["key"], data["secret"]
    except KeyError:
        raise unexpected_response()
    dest_path = lambda p: username + "/" + SETTINGS["app_name"] + "/" + p
    installer = project_path("target/${installer}")
    installer_dest = dest_path(basename(installer))
    upload_file(installer, installer_dest, *credentials)
    uploaded = [installer_dest]
    if is_linux():
        repo_dest = dest_path(SETTINGS["repo_subdir"])
        uploaded.extend(
            upload_folder_contents(project_path("target/repo"), repo_dest, *credentials)
        )
        pubkey_dest = dest_path("public-key.gpg")
        upload_file(
            project_path("${build_system_dir}/sign/linux/public-key.gpg"),
            pubkey_dest,
            *credentials
        )
        uploaded.append(pubkey_dest)
    status, response = _server.post_json(
        "complete_upload",
        {"username": username, "password": password, "files": uploaded},
    )
    if status != 201:
        raise unexpected_response()
