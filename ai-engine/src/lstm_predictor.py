"""
LSTM Traffic Prediction Engine
Predicts per-node congestion load for the next N timesteps.
Input window: last 20 load readings per node.
Output: predicted load for each node in the next timestep.
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models


WINDOW = 20   # input sequence length
N_NODES = 11  # number of mesh nodes


def build_lstm_model(n_nodes: int = N_NODES, window: int = WINDOW) -> tf.keras.Model:
    inp = tf.keras.Input(shape=(window, n_nodes))
    x = layers.LSTM(64, return_sequences=True)(inp)
    x = layers.Dropout(0.2)(x)
    x = layers.LSTM(32)(x)
    x = layers.Dense(n_nodes, activation="sigmoid")(x)
    model = models.Model(inputs=inp, outputs=x)
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model


class LSTMPredictor:
    def __init__(self, n_nodes: int = N_NODES, window: int = WINDOW):
        self.n_nodes = n_nodes
        self.window  = window
        self.model   = build_lstm_model(n_nodes, window)
        self.history: list[np.ndarray] = []
        self._pretrain()

    def _pretrain(self):
        """Warm-start the model on synthetic sine-wave traffic data."""
        rng = np.random.default_rng(42)
        t   = np.linspace(0, 4 * np.pi, 1000)
        data = np.stack([
            0.2 + 0.15 * np.sin(t + rng.uniform(0, 2 * np.pi))
            + 0.05 * rng.random(len(t))
            for _ in range(self.n_nodes)
        ], axis=1)

        X, y = [], []
        for i in range(len(data) - self.window):
            X.append(data[i : i + self.window])
            y.append(data[i + self.window])

        X = np.array(X)
        y = np.array(y)
        self.model.fit(X, y, epochs=5, batch_size=32, verbose=0)

    def update(self, load_vector: np.ndarray):
        """Push a new load observation (shape: [n_nodes])."""
        self.history.append(load_vector.copy())
        if len(self.history) > self.window * 5:
            self.history.pop(0)

    def predict(self) -> np.ndarray:
        """Return predicted next-step loads, or latest observed if not enough history."""
        if len(self.history) < self.window:
            if self.history:
                return self.history[-1]
            return np.full(self.n_nodes, 0.3)

        window_arr = np.array(self.history[-self.window:])
        x = window_arr[np.newaxis, ...]  # shape (1, window, n_nodes)
        pred = self.model.predict(x, verbose=0)[0]
        return pred

    def rmse(self, actual: np.ndarray) -> float:
        pred = self.predict()
        return float(np.sqrt(np.mean((pred - actual) ** 2)))
