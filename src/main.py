import json

from pathlib import Path
from pprint import pprint

from googleapiclient.errors import HttpError
from InquirerPy import inquirer
from InquirerPy.utils import color_print

from .constants import SETTINGS_FILE
from .auth import get_authenticated_service
from .upload import initialize_upload
from .presets import PRESETS, Preset
from .utils import load_local_file, save_local_file


def setup() -> Preset:
    settings = json.loads(load_local_file(SETTINGS_FILE, "{}"))
    folder = settings.get("folder", None)
    video_filepath = None
    while not video_filepath:
        if not folder:
            folder = inquirer.filepath(message="Enter the folder path", only_directories=True).execute()

        folder_path = Path(folder)
        if not folder_path.exists() or not folder_path.is_dir():
            color_print([("#FF0000", "Folder does not exist")])
            folder = None
            continue

        settings["folder"] = folder_path.resolve().as_posix()
        save_local_file(SETTINGS_FILE, json.dumps(settings, indent=4))

        color_print([("#00FFFF", f"[{folder}]")])

        video_files = list(folder_path.glob("*.mp4"))
        if not video_files:
            color_print([("#FF0000", "No video files found")])
            folder = None
            continue

        video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        video_files = video_files[:8]

        choices = [video_file.name for video_file in video_files]
        choices.append("Go to a different folder")
        choice = inquirer.select(
            message="Select a video",
            choices=[video_file.name for video_file in video_files],
            default=video_files[0].name,
        ).execute()

        if choice == "Go to a different folder":
            folder = None
            continue

        video_file = next(
            video_file for video_file in video_files if video_file.name == choice
        )

        video_filepath = video_file.resolve()

    preset_name = inquirer.select(
        message="Select a preset",
        choices=[preset["name"] for preset in PRESETS],
        default=PRESETS[0]["name"],
    ).execute()

    preset_entry = next(preset for preset in PRESETS if preset["name"] == preset_name)
    preset = preset_entry["class"](video_filepath)

    return preset


def start():
    preset = setup()
    pprint(preset.options.to_dict())
    proceed = inquirer.confirm(message="Proceed to upload?", default=True).execute()
    if not proceed:
        return

    youtube = get_authenticated_service()

    try:
        initialize_upload(youtube, preset.options)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))


if __name__ == "__main__":
    start()
