import random
import pandas as pd
import mesa
#from mesa.time import RandomActivation
from numpy.matlib import empty

from SimpleAgent import SimpleAgent
from ObjectiveBasedAgent import ObjectiveBasedAgent
from StateBasedAgent import StateBasedAgent
from Resource import Resource
from Obstacle import Obstacle


class Planet(mesa.Model):
    def __init__(self, n_SA,
                 n_SBA, n_OBA, height, width, n_resources , n_obstacles=0, base_pos = (0,0), seed=None):
        super().__init__(seed=seed)
        self.n_SA = n_SA;
        self.n_SBA = n_SBA
        self.n_OBA = n_OBA
        self.obstacles = []
        self.grid = mesa.space.MultiGrid(int(width), int(height), torus=False)
        self.base_pos = base_pos

        for _ in range(n_resources):
            x, y = self.random.randrange(width), self.random.randrange(height)
            while (x, y) == base_pos or (x, y) in self.obstacles:
                x, y = self.random.randrange(width), self.random.randrange(height)
            size = self.random.choice([Resource.SMALL, Resource.MEDIUM, Resource.HEAVY])
            self.grid.place_agent(Resource(size, self), (x, y))

        for _ in range(n_obstacles):
            x, y = self.random.randrange(width), self.random.randrange(height)
            while (x, y) == base_pos or (x, y) in self.obstacles:
                x, y = self.random.randrange(width), self.random.randrange(height)
            self.grid.place_agent(Obstacle(self), (x, y))
            self.obstacles.append((x, y))


        for _ in range(n_SA):
            a = SimpleAgent(self)
            self.grid.place_agent(a, base_pos)

        for _ in range(n_SBA):
            a = StateBasedAgent(self)
            self.grid.place_agent(a, base_pos)

        for _ in range(n_OBA):
            a = ObjectiveBasedAgent(self)
            self.grid.place_agent(a, base_pos)


    def step(self):
    # Verifica todos os agentes
        for agent in self.agents:
            if isinstance(agent, SimpleAgent):
                agent.step()  # Movimenta o agente ou coleta o recurso

        # Certifique-se de que os objetos estáticos (obstáculos, recursos) permaneçam intactos
        for (x, y) in self.obstacles:
            if not any(isinstance(obj, Obstacle) for obj in self.grid.get_cell_list_contents((x, y))):
                self.grid.place_agent(Obstacle(self), (x, y))

    

    def to_dataframe(self):
        self.data = []
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_contents = self.grid.get_cell_list_contents((x, y))
                for obj in cell_contents:
                    if isinstance(obj, Resource) or isinstance(obj, Obstacle) or isinstance(obj, SimpleAgent):
                        self.data.append({
                            "x": int(x),
                            "y": int(y),
                            "type": obj.type,  
                            "color": obj.color,  
                            "shape": obj.shape
                        })
        return pd.DataFrame(self.data)


