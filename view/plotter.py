from collections import deque
from random import randint
import time
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

class DataPlot:
    def __init__(self, max_entries=20):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axis_y2 = deque(maxlen=max_entries)

        self.max_entries = max_entries

        self.buf1 = deque(maxlen=5)
        self.buf2 = deque(maxlen=5)

    def add(self, x, y, y2):
        self.axis_x.append(x)
        self.axis_y.append(y)
        self.axis_y2.append(y2)

    def get_x(self):
        return self.axis_x.popleft()

    def get_y1(self):
        return self.axis_y.popleft()

    def get_y2(self):
        return self.axis_y2.popleft()


class RealtimePlot:
    def __init__(self, axes):
        self.axes = axes

        self.lineplot, = axes.plot([], [])
        self.lineplot2, = axes.plot([], [])

    def plot(self, dataPlot):
        self.lineplot.set_data(dataPlot.axis_x, dataPlot.axis_y)
        self.lineplot2.set_data(dataPlot.axis_x, dataPlot.axis_y2)

        self.axes.set_xlim(min(dataPlot.axis_x), max(dataPlot.axis_x))
        ymin = min([min(dataPlot.axis_y), min(dataPlot.axis_y2)]) - 10
        ymax = max([max(dataPlot.axis_y), max(dataPlot.axis_y2)]) + 10
        self.axes.set_ylim(ymin, ymax)
        self.axes.relim()


def main():
    fig = plt.figure(figsize=(10, 5), facecolor='#ececec')
    fig.text(0.5, 0.01, 'Time [ms]', ha='center')
    fig.text(0.01, 0.5, 'Output', va='center', rotation='vertical')
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    data = DataPlot()
    dataPlotting1 = RealtimePlot(ax1)
    dataPlotting2 = RealtimePlot(ax2)
    dataPlotting3 = RealtimePlot(ax3)
    dataPlotting4 = RealtimePlot(ax4)

    try:
        t0 = time.time()
        while True:
            t = time.time() - t0
            data.add(t, 30 + 1 / randint(1, 5), 35 + randint(1, 5))
            dataPlotting1.plot(data)
            dataPlotting2.plot(data)
            dataPlotting3.plot(data)
            dataPlotting4.plot(data)
            plt.pause(0.0001)
    except KeyboardInterrupt:
        print('Keyboard exception received. Exiting.')
        plt.close()
        exit()


if __name__ == "__main__":
    main()
