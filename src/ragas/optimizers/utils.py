import numpy as np


def hamming_distance(vectors: np.ndarray) -> np.ndarray:
    """
    计算多组向量两两之间的汉明距离（对应位置不同的个数）。
    用于遗传算法中根据预测向量的差异选交叉配对个体。
    Calculate the Hamming distance between pairs of vectors in a list of lists.
    """

    # 校验：所有向量维度必须一致
    length = len(vectors[0])
    if any(len(v) != length for v in vectors):
        raise ValueError("All vectors must have the same dimensions.")

    # 计算所有向量对的汉明距离矩阵（仅上三角，i<j）
    distances = np.zeros((len(vectors), len(vectors)), dtype=int)
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            distance = np.sum(vectors[i] != vectors[j])
            distances[i][j] = distance

    return distances
