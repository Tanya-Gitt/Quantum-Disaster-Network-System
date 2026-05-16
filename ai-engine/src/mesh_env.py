"""
Gymnasium environment for the mesh network.
The PPO agent observes node loads and link states,
then selects which offline nodes to reroute around.
"""
import numpy as np
import networkx as nx
import gymnasium as gym
from gymnasium import spaces

N_NODES = 11
N_EDGES = 12  # max edges in the mesh


class MeshEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self):
        super().__init__()
        # Observation: [node_loads x11] + [edge_active x12] = 23 floats
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(N_NODES + N_EDGES,), dtype=np.float32
        )
        # Action: select one of N_NODES to prioritise for rerouting
        self.action_space = spaces.Discrete(N_NODES)

        self._reset_graph()

    def _reset_graph(self):
        self.g = nx.Graph()
        self.node_ids = [f"N{i}" for i in range(1, 9)] + ["D1", "D2", "SDN"]
        self.loads    = np.random.uniform(0.1, 0.5, N_NODES).astype(np.float32)
        self.alive    = np.ones(N_NODES, dtype=np.float32)

        edge_list = [(0,1),(0,4),(0,10),(1,2),(1,6),(2,5),(2,3),(3,7),(3,10),(4,6),(5,7),(6,10)]
        self.edges = edge_list
        self.edge_active = np.ones(N_EDGES, dtype=np.float32)
        for src, dst in edge_list:
            self.g.add_edge(src, dst)

    def _obs(self) -> np.ndarray:
        return np.concatenate([self.loads * self.alive, self.edge_active])

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._reset_graph()
        # Randomly kill 1-3 nodes
        n_kill = self.np_random.integers(1, 4)
        killed = self.np_random.choice(N_NODES - 1, n_kill, replace=False)
        for k in killed:
            self.alive[k] = 0.0
            for i, (u, v) in enumerate(self.edges):
                if u == k or v == k:
                    self.edge_active[i] = 0.0
        return self._obs(), {}

    def step(self, action):
        # Reward: connectivity ratio of surviving nodes
        active_nodes = [i for i in range(N_NODES) if self.alive[i] > 0]
        sub = self.g.subgraph(active_nodes)
        if len(active_nodes) > 1:
            n_components = nx.number_connected_components(sub)
            connectivity = len(active_nodes) / (N_NODES * n_components)
        else:
            connectivity = 0.0

        # Penalise if chosen node is already offline
        penalty = 0.1 if self.alive[action] == 0 else 0.0

        reward = connectivity - penalty
        done   = False
        return self._obs(), reward, done, False, {}
