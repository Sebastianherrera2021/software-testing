# utils/recorder.py - records a short video of each test run (evidence of what Selenium does)
# AI usage note: drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.
#
# Selenium has no built-in video recording, so this listener takes a screenshot
# after every navigation, click and typing action, writes the step name on it,
# and joins the frames into an MP4 (or an animated GIF if MP4 support is missing).

import io
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw
from selenium.webdriver.support.events import AbstractEventListener

FRAME_SECONDS = 1.2     # how long each step stays on screen in the video


class StepRecorder(AbstractEventListener):

    def __init__(self):
        self.frames = []          # list of (PIL image, caption)

    # ------------------------------------------------------------ capture
    def capture(self, driver, caption):
        try:
            png = driver.get_screenshot_as_png()
        except Exception:
            return
        image = Image.open(io.BytesIO(png)).convert("RGB")
        self.frames.append((image, caption))

    @staticmethod
    def _describe(element):
        try:
            name = (element.get_attribute("name") or element.get_attribute("id")
                    or element.text or element.tag_name)
        except Exception:
            name = "element"
        return str(name).strip().replace("\n", " ")[:40]

    # ------------------------------------------------------------ Selenium events
    def after_navigate_to(self, url, driver):
        self.capture(driver, f"Open {url}")

    def before_click(self, element, driver):
        # describe the element now: after the click it may no longer exist
        self._pending = f"Click '{self._describe(element)}'"

    def after_click(self, element, driver):
        self.capture(driver, getattr(self, "_pending", "Click"))

    def after_change_value_of(self, element, driver):
        field = self._describe(element)
        caption = "Type password (hidden)" if "password" in field.lower() else f"Type into '{field}'"
        self.capture(driver, caption)

    # ------------------------------------------------------------ output
    def save(self, path_without_suffix):
        """Write the video; returns the file path, or None if nothing was captured."""
        if not self.frames:
            return None
        size = self.frames[0][0].size
        images = []
        for number, (image, caption) in enumerate(self.frames, start=1):
            frame = image.resize(size)
            draw = ImageDraw.Draw(frame)
            label = f"Step {number}: {caption}"
            draw.rectangle([0, size[1] - 40, size[0], size[1]], fill=(17, 17, 17))
            draw.text((12, size[1] - 30), label, fill=(255, 255, 255))
            images.append(frame)

        path = Path(path_without_suffix)
        path.parent.mkdir(exist_ok=True)
        try:
            import imageio.v2 as imageio  # needs imageio + imageio-ffmpeg (requirements.txt)
            video = path.with_suffix(".mp4")
            fps = 10
            with imageio.get_writer(video, fps=fps, codec="libx264", macro_block_size=8) as writer:
                for frame in images:
                    data = _even(frame)
                    for _ in range(int(FRAME_SECONDS * fps)):
                        writer.append_data(data)
            return video
        except Exception:
            gif = path.with_suffix(".gif")
            small = [img.resize((size[0] // 2, size[1] // 2)) for img in images]
            small[0].save(gif, save_all=True, append_images=small[1:],
                          duration=int(FRAME_SECONDS * 1000), loop=0)
            return gif


def _even(image):
    """Crop to a multiple of 8 pixels, which every H.264 player accepts."""
    import numpy as np
    w, h = image.size
    return np.asarray(image.crop((0, 0, w - w % 8, h - h % 8)))


def video_name(test_name):
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in test_name)
    return f"{safe}_{datetime.now():%Y%m%d_%H%M%S}"
