import numpy as np
from typing import Tuple

from sklearn.cluster import DBSCAN

from .segmentation import segment_walruses
from .utils.cluster_counter import SegmentCounter


def get_walrus_count(img: np.array) -> Tuple[np.array, int]:
    """ Расчет количества моржей по фотографии """
    counter = SegmentCounter()

    mask = segment_walruses(img)
    count = counter.get_animal_count(mask)

    return mask, count


def walruses_count_by_click(img: np.array, centroids: np.array, x: float, y: float):
    """ Расчет количества моржей рядом с определенной точкой """
    x = x * SegmentCounter.DEFAULT_SIZE[0] / img.shape[1]
    y = y * SegmentCounter.DEFAULT_SIZE[1] / img.shape[0]
    cluster_centers = np.array(list(centroids) + [[x, y]])

    dbscan = DBSCAN(eps=20)
    dbscan.fit(cluster_centers)

    point_label = dbscan.labels_[-1]

    if point_label == -1:
        return 0

    return dbscan.labels_[dbscan.labels_ == point_label].shape[0]
