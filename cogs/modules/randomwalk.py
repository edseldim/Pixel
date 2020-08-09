from random import choice, randint
import matplotlib.pyplot as plt

class RandomWalk():

    def __init__(self, rep):

        self.rep = rep
        self.x_axis = [0]
        self.y_axis = [0]

    def generate_figure(self):

        i = 0

        while i < self.rep:

            x = randint(-10,10)
            y = randint(-10,10)
            x_direction = x + self.x_axis[-1]
            y_direction = y + self.y_axis[-1]

            if x_direction == self.x_axis[-1] and y_direction == self.y_axis[-1]:

                continue

            else:

                self.x_axis.append(x_direction)
                self.y_axis.append(y_direction)


            i += 1



rw_1 = RandomWalk(6000)
rw_1.generate_figure()
plt.scatter(rw_1.x_axis, rw_1.y_axis, c= [i for i in range(len(rw_1.x_axis))], cmap = 'PiYG', alpha =0.5,  edgecolor='none', s=15)
plt.xticks([])
plt.yticks([])

# try:

#     f = open('test.png','rb')

# except Exception as e:

#     pass

# else:

#     plt.savefig(f)

# finally:

#     f.close()

with open('test', 'wb') as f:

    f.write()