from model import *

model = Planet(3,5,5,25,2)

for _ in range(300):
    model.show_grid()
    model.step()
    print()

for agent in model.agents:
    if isinstance(agent, SimpleAgent):
        print(f"agent {agent.unique_id} has collected {agent.collected_resources} resources")