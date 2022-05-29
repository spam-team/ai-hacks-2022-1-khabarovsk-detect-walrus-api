import cv2

from counting import get_walrus_count


def test_walrus_counting():
    img = cv2.imread('./examples/268.jpg')
    mask, count = get_walrus_count(img)

    assert count > 20
