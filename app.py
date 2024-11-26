from model import *

model = Planet(0,0,1,8, 8, 30, seed = 12)

for _ in range(50):
    model.show_grid()
    model.step()
    print()
s = 0
for agent in model.agents:
    if isinstance(agent, SimpleAgent):
        print(f"agent {agent.unique_id} has collected {agent.collected_resources} resources")
        s += agent.collected_resources
print("soma = ", s)
