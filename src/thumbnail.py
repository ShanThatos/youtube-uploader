import random
import cv2

from PIL import Image, ImageDraw, ImageFont

from .utils import resource_path


def create_thumbnails(video_filepath: str, options: dict = {}):
    vidcap = cv2.VideoCapture(video_filepath)
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    amount = options["amount"]
    font_size = options["font_size"]
    title = options["title"]

    results = []
    for _ in range(amount):
        random_frame = random.randint(total_frames // 10, total_frames * 9 // 10)
        results.append(create_thumbnail_frame(vidcap, random_frame, title, font_size))
    return results


def create_thumbnail_frame(vidcap: cv2.VideoCapture, frame: int, title: str, font_size: int) -> Image:
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame)
    success, image_cv2 = vidcap.read()
    if not success:
        raise ValueError("Failed to read frame")
    image_cv2 = cv2.resize(image_cv2, (2560, 1440))
    image_cv2 = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)

    image = Image.fromarray(image_cv2)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(resource_path("./assets/ProtestRiot-Regular.ttf").as_posix(), font_size)
    _, _, w, h = draw.textbbox((0, 0), title, font=font, align="center")
    draw.text(
        ((image.width - w) // 2, (image.height - h) // 2),
        title,
        font=font,
        align="center",
        fill="white",
        stroke_fill="black",
        stroke_width=20,
    )

    return image
