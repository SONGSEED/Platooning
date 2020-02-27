import matplotlib.pyplot as plt
import numpy as np
import glob
from sklearn.model_selection import train_test_split
#img_array = np.load("training_data/1575298710.npz")

def load_data(path = './training_data/1575986935.npz', random_state = 41):

    x_train = np.empty((0, 120, 320, 1))
    y_train = np.empty((0, 4))
    training_data = glob.glob(path)

    for single_npz in training_data:
        with np.load(single_npz) as data:
            x = data['train']
            y = data['train_labels']
        x = np.reshape(x, (-1, 120, 320, 1))

        x_train = np.vstack((x_train, x))
        y_train = np.vstack((y_train, y))

    # 트레이닝셋을 잘못 만들어서 잘라줘함
    y_train = y_train[:, :-1]

    print('load data!!!')

    # train test split, 7:3
    return train_test_split(x_train, y_train, test_size=0.3 ,random_state= random_state)

def show_data(x, y):
    print("show data!!!")

    plt_row = 5
    plt_col = 5
    plt.rcParams["figure.figsize"] = (10, 10)

    f, axarr = plt.subplots(plt_row, plt_col)

    for i in range(plt_row * plt_col):

        sub_plt = axarr[int(i / plt_row), int(i % plt_col)]
        sub_plt.axis('off')
        sub_plt.imshow(x[i].reshape(120, 320))

        label = np.argmax(y[i])

        if label == 0:
            direction = 'left'
        elif label == 1:
            direction = 'right'
        elif label == 2:
            direction = 'forward'
        elif label == 3:
            direction = 'backward'

        sub_plt_title = str(label) + " : " + direction
        sub_plt.set_title(sub_plt_title)

    plt.show()



x_train, x_test, y_train, y_test = load_data(random_state = 41)
show_data(x_train, y_train)
