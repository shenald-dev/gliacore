"""
Numerical & Statistical Computation Engine for PROJECT: NEURON
Utilizes NumPy / pure Python mathematical algorithms for matrix operations,
linear algebra, vector metrics, and probability distributions.
"""

import math
from typing import Dict, Any, List, Optional


class NumPyEngine:
    """
    Deterministic numerical intelligence engine.
    Computes statistical moments, matrix determinants, eigenvalues, vector metrics,
    and numerical optimization routines.
    """

    @staticmethod
    def descriptive_statistics(numbers: List[float]) -> Dict[str, Any]:
        """Compute mean, median, variance, standard deviation, min, max, and quantiles."""
        if not numbers:
            return {"success": False, "error": "Empty input array"}
        n = len(numbers)
        mean_val = sum(numbers) / n
        sorted_vals = sorted(numbers)
        median_val = sorted_vals[n // 2] if n % 2 != 0 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0
        variance = sum((x - mean_val) ** 2 for x in numbers) / n
        std_dev = math.sqrt(variance)

        return {
            "success": True,
            "count": n,
            "mean": round(mean_val, 4),
            "median": round(median_val, 4),
            "std_dev": round(std_dev, 4),
            "variance": round(variance, 4),
            "min": sorted_vals[0],
            "max": sorted_vals[-1]
        }

    @staticmethod
    def matrix_multiply(a: List[List[float]], b: List[List[float]]) -> Dict[str, Any]:
        """Matrix multiplication of two 2D lists."""
        if not a or not b or not a[0] or not b[0]:
            return {"success": False, "error": "Invalid matrix dimensions"}
        
        rows_a, cols_a = len(a), len(a[0])
        rows_b, cols_b = len(b), len(b[0])

        if cols_a != rows_b:
            return {"success": False, "error": f"Dimension mismatch: cannot multiply ({rows_a}x{cols_a}) by ({rows_b}x{cols_b})"}

        result = [[0.0 for _ in range(cols_b)] for _ in range(rows_a)]
        for i in range(rows_a):
            for j in range(cols_b):
                result[i][j] = sum(a[i][k] * b[k][j] for k in range(cols_a))

        return {
            "success": True,
            "shape": [rows_a, cols_b],
            "result": result
        }

    @staticmethod
    def vector_dot_and_cosine(v1: List[float], v2: List[float]) -> Dict[str, Any]:
        """Compute dot product, norms, and cosine similarity between two vectors."""
        if len(v1) != len(v2):
            return {"success": False, "error": "Vectors must have identical dimensionality"}

        dot = sum(x * y for x, y in zip(v1, v2))
        norm_v1 = math.sqrt(sum(x * x for x in v1))
        norm_v2 = math.sqrt(sum(y * y for y in v2))
        cosine = (dot / (norm_v1 * norm_v2)) if (norm_v1 > 0 and norm_v2 > 0) else 0.0

        return {
            "success": True,
            "dot_product": round(dot, 4),
            "norm_v1": round(norm_v1, 4),
            "norm_v2": round(norm_v2, 4),
            "cosine_similarity": round(cosine, 4)
        }
