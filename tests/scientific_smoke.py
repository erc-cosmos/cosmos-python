"""Exercise the standalone scientific stack: pixi run --locked python tests/scientific_smoke.py."""
import unittest

import numba
import numpy as np
import pandas as pd
import scipy
from scipy import linalg, optimize
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import torch


class ScientificStackTests(unittest.TestCase):
    def test_numpy_scipy_linear_algebra(self):
        matrix = np.array([[3., 1.], [1., 2.]])
        rhs = np.array([9., 8.])
        np.testing.assert_allclose(linalg.solve(matrix, rhs), [2., 3.])

    def test_scipy_optimization(self):
        fit = optimize.least_squares(lambda x: np.array([x[0] - 3., 2 * (x[1] + 1.)]), [0., 0.])
        self.assertTrue(fit.success)
        np.testing.assert_allclose(fit.x, [3., -1.], atol=1e-7)

    def test_numba_numpy_compilation(self):
        @numba.njit
        def sum_squares(values):
            return np.sum(values * values)
        values = np.arange(10, dtype=np.float64)
        self.assertEqual(sum_squares(values), 285.)
        self.assertTrue(sum_squares.nopython_signatures)

    def test_pandas_numba_rolling(self):
        values = pd.Series([1., 2., 3., 4.])
        actual = values.rolling(2).mean(engine='numba').to_numpy()
        np.testing.assert_allclose(actual, [np.nan, 1.5, 2.5, 3.5], equal_nan=True)

    def test_pandas_sklearn_pipeline(self):
        data = pd.DataFrame({'x': np.arange(10, dtype=float)})
        target = 3 * data['x'] + 2
        model = make_pipeline(StandardScaler(), LinearRegression()).fit(data, target)
        np.testing.assert_allclose(model.predict(pd.DataFrame({'x': [10., 11.]})), [32., 35.])

    def test_torch_numpy_interop_and_autograd(self):
        values = np.array([1., 2., 3.], dtype=np.float64)
        tensor = torch.from_numpy(values)
        tensor[0] = 4.
        self.assertEqual(values[0], 4.)
        tensor.requires_grad_(True)
        (tensor * tensor).sum().backward()
        np.testing.assert_allclose(tensor.grad.numpy(), 2 * values)
        np.testing.assert_allclose(tensor.detach().numpy(), values)


if __name__ == '__main__':
    for module in (np, pd, numba, scipy, sklearn, torch):
        print(f'{module.__name__}: {module.__version__}', flush=True)
    unittest.main(verbosity=2)
