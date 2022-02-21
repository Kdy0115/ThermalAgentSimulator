from mesa.space import Grid,MultiGrid
from mesa.agent import Agent
import numpy as np
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union
import itertools

FloatCoordinate_3d = Tuple[int, int, int]
GridContent_3d = Union[Optional[Agent], Set[Agent]]
# used in ContinuousSpace
FloatCoordinate_3d = Union[Tuple[float, float, float], np.ndarray]


def accept_tuple_argument_3d(wrapped_function):
    """ Decorator to allow grid methods that take a list of (x, y) coord tuples
    to also handle a single position, by automatically wrapping tuple in
    single-item list rather than forcing user to do it.

    """

    def wrapper(*args: Any):
        if isinstance(args[1], tuple) and len(args[1]) == 3:
            return wrapped_function(args[0], [args[1]])
        else:
            return wrapped_function(*args)

    return wrapper

class ContinuousSpace3d:
    """ Continuous space where each agent can have an arbitrary position.

    Assumes that all agents are point objects, and have a pos property storing
    their position as an (x, y) tuple. This class uses a numpy array internally
    to store agent objects, to speed up neighborhood lookups.

    """

    _grid = None

    def __init__(
        self,
        x_max: float,
        y_max: float,
        z_max: float,
        torus: bool,
        x_min: float = 0,
        y_min: float = 0,
        z_min: float = 0,
    ) -> None:
        """ Create a new continuous space.

        Args:
            x_max, y_max: Maximum x and y coordinates for the space.
            torus: Boolean for whether the edges loop around.
            x_min, y_min: (default 0) If provided, set the minimum x and y
                          coordinates for the space. Below them, values loop to
                          the other edge (if torus=True) or raise an exception.

        """
        self.x_min = x_min
        self.x_max = x_max
        self.width = x_max - x_min
        self.y_min = y_min
        self.y_max = y_max
        self.height = y_max - y_min
        self.z_min = z_min
        self.z_max = z_max
        self.depth = z_max - z_min
        self.center = np.array(((x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2))
        self.size = np.array((self.width, self.height, self.depth))
        self.torus = torus

        self._agent_points = None
        self._index_to_agent = {}  # type: Dict[int, Agent]
        self._agent_to_index = {}  # type: Dict[Agent, int]

    def place_agent(self, agent: Agent, pos: FloatCoordinate_3d) -> None:
        """ Place a new agent in the space.

        Args:
            agent: Agent object to place.
            pos: Coordinate tuple for where to place the agent.

        """
        pos = self.torus_adj(pos)
        if self._agent_points is None:
            self._agent_points = np.array([pos])
        else:
            self._agent_points = np.append(self._agent_points, np.array([pos]), axis=0)
        self._index_to_agent[self._agent_points.shape[0] - 1] = agent
        self._agent_to_index[agent] = self._agent_points.shape[0] - 1
        agent.pos = pos


    def move_agent(self, agent: Agent, pos: FloatCoordinate_3d) -> None:
        """ Move an agent from its current position to a new position.

        Args:
            agent: The agent object to move.
            pos: Coordinate tuple to move the agent to.

        """
        pos = self.torus_adj(pos)
        idx = self._agent_to_index[agent]
        self._agent_points[idx, 0] = pos[0]
        self._agent_points[idx, 1] = pos[1]
        self._agent_points[idx, 2] = pos[2]
        agent.pos = pos


    def remove_agent(self, agent: Agent) -> None:
        """ Remove an agent from the simulation.

        Args:
            agent: The agent object to remove
            """
        if agent not in self._agent_to_index:
            raise Exception("Agent does not exist in the space")
        idx = self._agent_to_index[agent]
        del self._agent_to_index[agent]
        max_idx = max(self._index_to_agent.keys())
        # Delete the agent's position and decrement the index/agent mapping
        self._agent_points = np.delete(self._agent_points, idx, axis=0)
        for a, index in self._agent_to_index.items():
            if index > idx:
                self._agent_to_index[a] = index - 1
                self._index_to_agent[index - 1] = a
        # The largest index is now redundant
        del self._index_to_agent[max_idx]
        agent.pos = None


    def get_neighbors(
        self, pos: FloatCoordinate_3d, radius: float, include_center: bool = True
    ) -> List[GridContent_3d]:
        """ Get all objects within a certain radius.

        Args:
            pos: (x,y,z) coordinate tuple to center the search at.
            radius: Get all the objects within this distance of the center.
            include_center: If True, include an object at the *exact* provided
                            coordinates. i.e. if you are searching for the
                            neighbors of a given agent, True will include that
                            agent in the results.

        """
        deltas = np.abs(self._agent_points - np.array(pos))
        if self.torus:
            deltas = np.minimum(deltas, self.size - deltas)
        dists = deltas[:, 0] ** 2 + deltas[:, 1] ** 2 + deltas[:, 2] ** 2

        # 立方体で敷き詰められていると仮定して√2をかける
        radius *= np.sqrt(2)

        (idxs,) = np.where(dists <= radius ** 2)
        neighbors = [
            self._index_to_agent[x] for x in idxs if include_center or dists[x] > 0
        ]
        return neighbors


    def get_heading(
        self, pos_1: FloatCoordinate_3d, pos_2: FloatCoordinate_3d
    ) -> FloatCoordinate_3d:
        """ Get the heading angle between two points, accounting for toroidal space.

        Args:
            pos_1, pos_2: Coordinate tuples for both points.
        """
        one = np.array(pos_1)
        two = np.array(pos_2)
        if self.torus:
            one = (one - self.center) % self.size
            two = (two - self.center) % self.size
        heading = two - one
        if isinstance(pos_1, tuple):
            heading = tuple(heading)
        return heading


    def get_distance(self, pos_1: FloatCoordinate_3d, pos_2: FloatCoordinate_3d) -> float:
        """ Get the distance between two point, accounting for toroidal space.

        Args:
            pos_1, pos_2: Coordinate tuples for both points.

        """
        x1, y1, z1 = pos_1
        x2, y2, z2 = pos_2

        dx = np.abs(x1 - x2)
        dy = np.abs(y1 - y2)
        dz = np.abs(z1 - z2)
        if self.torus:
            dx = min(dx, self.width - dx)
            dy = min(dy, self.height - dy)
            dz = min(dz, self.depth - dz)
        return np.sqrt(dx * dx + dy * dy + dz * dz)


    def torus_adj(self, pos: FloatCoordinate_3d) -> FloatCoordinate_3d:
        """ Adjust coordinates to handle torus looping.

        If the coordinate is out-of-bounds and the space is toroidal, return
        the corresponding point within the space. If the space is not toroidal,
        raise an exception.

        Args:
            pos: Coordinate tuple to convert.

        """
        if not self.out_of_bounds(pos):
            return pos
        elif not self.torus:
            raise Exception("Point out of bounds, and space non-toroidal.")
            #return (-1, -1, -1)
        else:
            x = self.x_min + ((pos[0] - self.x_min) % self.width)
            y = self.y_min + ((pos[1] - self.y_min) % self.height)
            z = self.z_min + ((pos[2] - self.z_min) % self.depth)
            if isinstance(pos, tuple):
                return (x, y, z)
            else:
                return np.array((x, y, z))


    def out_of_bounds(self, pos: FloatCoordinate_3d) -> bool:
        """ Check if a point is out of bounds. """

        x, y, z = pos
        return x < self.x_min or x > self.x_max or y < self.y_min or y > self.y_max or z < self.z_min or z > self.z_max

    def get_cell_list_contents( self, cell_list: Iterable[FloatCoordinate_3d]) -> List[GridContent_3d]:
        """
        Args:
            cell_list: Array-like of (x, y) tuples, or single tuple.

        Returns:
            A list of the contents of the cells identified in cell_list

        """
        agents_list = []
        for agent in self._agent_to_index:
            x_point, y_point, z_point = cell_list[0]
            if agent.__class__.__name__ != "HeatCharge" and agent.__class__.__name__ != "AirConditioner":
                if agent.pos == cell_list[0]:
                    agents_list.append(agent)
        
        return agents_list