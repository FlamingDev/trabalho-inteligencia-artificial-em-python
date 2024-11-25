from model import Planet

model = Planet(3,5,5,4,3)

model.show_grid()

for _ in range(1):
    model.step()
    print()

model.show_grid()