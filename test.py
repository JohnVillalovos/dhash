import io
import os
import unittest
from typing import Union

import PIL
import PIL.ImageDraw
import wand.image  # type: ignore[import]

import dhash

IMGDIR = os.path.dirname(__file__)


def pil_to_wand(image: PIL.Image.Image, format: str = "png") -> wand.image.Image:
    with io.BytesIO() as fd:
        image.save(fd, format=format)
        fd.seek(0)
        return wand.image.Image(file=fd)


class TestDHash(unittest.TestCase):
    def test_get_grays_pil(self) -> None:
        with PIL.Image.open(os.path.join(IMGDIR, "dhash-test.jpg")) as image:
            self._test_get_grays(image, delta=1)

    def test_get_grays_wand(self) -> None:
        image = wand.image.Image(filename=os.path.join(IMGDIR, "dhash-test.jpg"))
        self._test_get_grays(image, delta=2)

    def _test_get_grays(
        self, image: Union[PIL.Image.Image, wand.image.Image], delta: int
    ) -> None:
        result = dhash.get_grays(image, 9, 9)[:18]

        expected = [
            93, 158, 210, 122, 93, 77, 74, 74, 77,
            95, 117, 122, 111, 92, 74, 81, 80, 77,
        ]  # fmt: skip

        self.assertEqual(len(result), len(expected))
        for r, e in zip(result, expected):
            self.assertAlmostEqual(r, e, delta=delta)

    def test_fill_transparency(self) -> None:
        "Ensure transparent colors in PIL Images are ignored in hashes"

        # grayscale image, completely white and also completely transparent
        # FIXME(jlvillal): Ignore type issue until PR merged:
        # https://github.com/python/typeshed/pull/10406
        im1 = PIL.Image.new(mode="LA", size=(100, 100), color=(0xFF, 0))  # type: ignore[arg-type]

        im2 = im1.copy()
        # replace most of it with "transparent black"
        # FIXME(jlvillal): Ignore type issue until PR merged:
        # https://github.com/python/typeshed/pull/10406
        PIL.ImageDraw.Draw(im2).rectangle(xy=(10, 10, 90, 90), fill=(0, 0))  # type: ignore[arg-type]

        self.assertEqual(dhash.dhash_row_col(im1), dhash.dhash_row_col(im2))

        # same with Wand version of images
        pm1, pm2 = pil_to_wand(im1), pil_to_wand(im2)
        self.assertEqual(dhash.dhash_row_col(pm1), dhash.dhash_row_col(pm2))


if __name__ == "__main__":
    unittest.main()
