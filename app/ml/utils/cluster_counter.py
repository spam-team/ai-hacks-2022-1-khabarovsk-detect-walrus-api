import joblib
import faiss
import numpy as np
from sklearn.cluster import DBSCAN

from typing import Tuple


count_resolver = joblib.load('../models/random_forest_counter.joblib')


class SegmentCounter:
    """ Класс-помощник для работы с кластерами.
    Уменьшаем входное изображение, чтобы ускорить время работы алгоритмов кластерого анализа.
    Гипотеза заключается в том, что моржи с большой высоты имеют одинаковую площадь в изображениях,
    поэтому производится поиск медианного размера кластера, а затем высчитывается количество моржей
    как отношение общей площади к медианной.
    Далее производится кластерное разбиение на найденное количество моржей.
    """
    DEFAULT_SIZE = (1090, 920)

    def _get_mask_points(self, mask: np.array) -> np.array:
        points = np.array([
            (i, j)
            for i in range(mask.shape[0])
            for j in range(mask.shape[1])
            if mask[i, j] != 0
        ])

        return points

    def _get_animal_count_by_cluster(self, cluster_counts: np.array) -> int:
        features = [cluster_counts.std(), cluster_counts.mean(), np.median(cluster_counts), cluster_counts.sum(), len(cluster_counts)]
        delimeter = count_resolver.predict([features])[0]

        return int(sum(cluster_counts) / delimeter)

    def _get_count_by_area(self, points: np.array) -> int:
        dbscan = DBSCAN(eps=1)
        dbscan.fit(points)

        cluster_counts = np.unique(dbscan.labels_, return_counts=True)[1]
        animal_count = self._get_animal_count_by_cluster(cluster_counts)

        return animal_count

    def get_animal_count(self, segment_mask: np.array) -> int:
        points = self._get_mask_points(segment_mask)
        count = self._get_count_by_area(points)

        return count

    def get_centroids(self, segment_mask: np.array) -> Tuple[np.array, int]:
        points = self._get_mask_points(segment_mask)
        animal_count = self.get_animal_count(segment_mask)

        niter = 3
        verbose = False
        d = points.shape[1]
        kmeans = faiss.Kmeans(d, animal_count, niter=niter, verbose=verbose, gpu=False)
        kmeans.train(points)

        return kmeans.centroids
