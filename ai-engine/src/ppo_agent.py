"""
PPO Routing Agent (Proximal Policy Optimisation)
Uses Stable-Baselines3 with the custom MeshEnv.
Trained for a short warm-up on startup; can be retrained online.
"""
import threading
import numpy as np
from stable_baselines3 import PPO
from .mesh_env import MeshEnv


class PPOAgent:
    def __init__(self):
        self.env   = MeshEnv()
        self.model = PPO(
            "MlpPolicy",
            self.env,
            verbose=0,
            learning_rate=3e-4,
            n_steps=512,
            batch_size=64,
            n_epochs=10,
        )
        self._lock         = threading.Lock()
        self._last_action  = None
        self._last_reward  = None
        self._train_thread = threading.Thread(target=self._warmup, daemon=True)
        self._train_thread.start()

    def _warmup(self):
        self.model.learn(total_timesteps=4096)
        print("[PPO] warm-up complete")

    def decide(self, load_vector: np.ndarray, edge_active: np.ndarray) -> dict:
        obs = np.concatenate([load_vector, edge_active]).astype(np.float32)
        with self._lock:
            action, _ = self.model.predict(obs, deterministic=True)
        self._last_action = int(action)
        node_ids = [f"N{i}" for i in range(1, 9)] + ["D1", "D2", "SDN"]
        return {
            "action": int(action),
            "target_node": node_ids[int(action)],
            "recommendation": f"Prioritise rerouting through {node_ids[int(action)]}",
        }

    def retrain(self, timesteps: int = 2048):
        def _run():
            with self._lock:
                self.model.learn(total_timesteps=timesteps, reset_num_timesteps=False)
        threading.Thread(target=_run, daemon=True).start()
