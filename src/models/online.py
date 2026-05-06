"""Concrete online learners."""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.preprocessing import StandardScaler

from src.models.base import OnlineModel
from src.utils.config import settings


class _StandardizedSGD(OnlineModel):
    """SGDClassifier with logistic loss + on-the-fly standardization."""

    name = "sgd_logistic"

    def __init__(
        self, alpha: float = 1e-4, eta0: float = 0.01, learning_rate: str = "optimal"
    ) -> None:
        self._alpha = alpha
        self._eta0 = eta0
        self._lr = learning_rate
        self.reset()

    def reset(self) -> None:
        self.scaler = StandardScaler(with_mean=True, with_std=True)
        self.clf = SGDClassifier(
            loss="log_loss",
            alpha=self._alpha,
            eta0=self._eta0,
            learning_rate=self._lr,
            random_state=settings.random_seed,
        )
        self._classes = np.array([0, 1])
        self._fitted_scaler = False

    def _standardize(self, X: np.ndarray, training: bool) -> np.ndarray:
        if training and not self._fitted_scaler:
            self.scaler.partial_fit(X)
            self._fitted_scaler = True
        elif training:
            self.scaler.partial_fit(X)
        return self.scaler.transform(X)

    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> None:
        Xs = self._standardize(X, training=True)
        self.clf.partial_fit(Xs, y, classes=self._classes)

    def predict(self, X: np.ndarray) -> np.ndarray:
        Xs = self._standardize(X, training=False)
        return self.clf.predict(Xs)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        Xs = self._standardize(X, training=False)
        try:
            return self.clf.predict_proba(Xs)
        except AttributeError:
            scores = self.clf.decision_function(Xs)
            p = 1.0 / (1.0 + np.exp(-scores))
            return np.stack([1 - p, p], axis=1)


class LogisticBaseline(OnlineModel):
    """Batch logistic regression. partial_fit refits on the buffer; useful as
    a non-adaptive reference for the prequential comparison."""

    name = "logistic_batch"

    def __init__(self, C: float = 1.0, buffer_size: int = 5000) -> None:
        self._C = C
        self.buffer_size = buffer_size
        self.reset()

    def reset(self) -> None:
        self.scaler = StandardScaler()
        self.clf = LogisticRegression(C=self._C, max_iter=200, random_state=settings.random_seed)
        self._buf_X: list[np.ndarray] = []
        self._buf_y: list[np.ndarray] = []
        self._fitted = False

    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._buf_X.append(X)
        self._buf_y.append(y)
        # Trim FIFO buffer.
        total = sum(b.shape[0] for b in self._buf_X)
        while total > self.buffer_size and self._buf_X:
            removed = self._buf_X.pop(0)
            self._buf_y.pop(0)
            total -= removed.shape[0]
        Xb = np.vstack(self._buf_X)
        yb = np.concatenate(self._buf_y)
        if len(np.unique(yb)) < 2:
            return
        Xs = self.scaler.fit_transform(Xb)
        self.clf.fit(Xs, yb)
        self._fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted:
            return np.zeros(X.shape[0], dtype=np.int64)
        return self.clf.predict(self.scaler.transform(X))

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted:
            p = np.full((X.shape[0], 2), 0.5, dtype=np.float64)
            return p
        return self.clf.predict_proba(self.scaler.transform(X))


class HoeffdingTreeAdapter(OnlineModel):
    """river HoeffdingTreeClassifier wrapped in the OnlineModel API."""

    name = "hoeffding_tree"

    def __init__(self, grace_period: int = 200, delta: float = 1e-7) -> None:
        from river.tree import HoeffdingTreeClassifier

        self._cls = HoeffdingTreeClassifier
        self._grace_period = grace_period
        self._delta = delta
        self.reset()

    def reset(self) -> None:
        self.clf = self._cls(grace_period=self._grace_period, delta=self._delta)

    def _row_to_dict(self, row: np.ndarray) -> dict[str, float]:
        return {f"x{i}": float(v) for i, v in enumerate(row)}

    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> None:
        for row, target in zip(X, y, strict=False):
            self.clf.learn_one(self._row_to_dict(row), int(target))

    def predict(self, X: np.ndarray) -> np.ndarray:
        out = np.empty(X.shape[0], dtype=np.int64)
        for i, row in enumerate(X):
            pred = self.clf.predict_one(self._row_to_dict(row))
            out[i] = int(pred) if pred is not None else 0
        return out

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        out = np.zeros((X.shape[0], 2), dtype=np.float64)
        for i, row in enumerate(X):
            p = self.clf.predict_proba_one(self._row_to_dict(row)) or {}
            out[i, 0] = float(p.get(0, 0.0))
            out[i, 1] = float(p.get(1, 0.0))
            s = out[i].sum()
            if s == 0:
                out[i] = [0.5, 0.5]
            else:
                out[i] /= s
        return out
