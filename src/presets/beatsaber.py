import subprocess
import re

from typing import override
from InquirerPy import inquirer

from .preset import Preset
from ..thumbnail import create_thumbnails
from ..utils import get_local_path

DESCRIPTION_TEMPLATE = """\
🎵 __TITLE__

Decided to post some VR content for fun. 

Modding/Recording Guides:
https://www.youtube.com/watch?v=DGRi8A0p1cY
https://www.youtube.com/watch?v=bFK3XH_K9Jg\
"""


class BeatSaberPreset(Preset):
    def taggify(self, value):
        return re.sub(r"[^a-z0-9]", "", value.lower())

    def construct(self):
        match = re.match(r"^(.*) - (.*) \(Standard (.*)\)$", self.path.stem)
        self.artist = match.group(1).strip()
        self.song = match.group(2).strip()
        difficulty = match.group(3).strip()

        title = f"Beat Saber: {self.song} - {self.artist} ({difficulty})"
        description = DESCRIPTION_TEMPLATE.replace("__TITLE__", title)

        self.options.title = title
        self.options.description = description
        self.options.tags = [
            "beatsaber",
            "vr",
            "gaming",
            self.taggify(self.song),
        ] + [self.taggify(x.strip()) for x in self.artist.split(",")]
        self.options.category_id = 20
        self.options.playlist_id = "PLBpN2wEoKkxmPRLdfAPO91rhEoZ5nzDeH"

    @override
    def confirm(self):
        super().confirm()
        self.confirm_thumbnail()

    def confirm_thumbnail(self):
        options = {
            "amount": 3,
            "font_size": 300,
            "title": f"{self.song}\n{self.artist}",
        }
        while True:
            print(f"\nCreating {options["amount"]} thumbnails ")
            images = create_thumbnails(str(self.options.file), options)
            choices = ["Regenerate"]
            thumbnails_path = get_local_path("./temp/thumbnails")
            thumbnails_path.mkdir(parents=True, exist_ok=True)
            for i, image in enumerate(images):
                file_name = f"thumbnail_{i}.jpg"
                thumbnail_file_path = thumbnails_path.joinpath(file_name)
                image.save(thumbnail_file_path.as_posix())
                choices.append(file_name)
            choices.append("Change Settings")

            exp_path = str(get_local_path(".\\temp\\thumbnails\\thumbnail_0.jpg"))
            subprocess.Popen(f"explorer /select, {exp_path}")

            choice = inquirer.select(
                message="Choose a thumbnail:",
                choices=choices,
            ).execute()

            if choice == "Regenerate":
                continue

            if choice == "Change Settings":
                options["amount"] = int(inquirer.text(
                    message="Amount:",
                    default=str(options["amount"]),
                ).execute())
                options["font_size"] = int(inquirer.text(
                    message="Font Size:",
                    default=str(options["font_size"]),
                ).execute())
                options["title"] = inquirer.text(
                    message="Title:",
                    multiline=True,
                    default=options["title"],
                ).execute().strip()
                continue

            self.options.thumbnail_path = thumbnails_path.joinpath(choice).as_posix()
            break
