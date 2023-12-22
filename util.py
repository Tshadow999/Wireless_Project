import math
import re
import matplotlib as mp
from objects import Params

mp.use('Agg')
from matplotlib import pyplot
import numpy as np

mp.rcParams["font.family"] = "Verdana"

def snr(distance, bandwidth, power, frequency):
    antenna_gain = 0
    noise = calculate_noise(bandwidth, noise_figure=7)
    pl = free_space_pathloss(distance, frequency)
    return power - pl + antenna_gain - noise  # in dB


def shannon_capacity(snr, bandwidth):
    snr = to_pwr(snr)
    return bandwidth * math.log2(1 + snr)


def thermal_noise(bandwidth):
    thermal_noise = Params.BOLTZMANN * Params.TEMPERATURE * bandwidth
    return 10 * math.log10(thermal_noise)


def calculate_noise(bandwidth, noise_figure):
    return thermal_noise(bandwidth) + noise_figure


def free_space_pathloss(distance, frequency):
     return 20*math.log10(distance)+10*math.log10(frequency) - 147.55 # in dB


def distance_2d(x1, y1, x2, y2):
    dist_x = abs(x1 - x2)
    dist_y = abs(y1 - y2)
    return math.sqrt(dist_x ** 2 + dist_y ** 2)


def distance_3d(h1, h2, x1=None, y1=None, x2=None, y2=None, d2d=None):
    d_2d = d2d
    if d_2d is None:
        d_2d = distance_2d(x1, y1, x2, y2)
    dist_h = abs(h1 - h2)
    return math.sqrt(d_2d ** 2 + dist_h ** 2)


def to_pwr(db):
    return 10 ** (db / 10)


def to_db(pwr):
    return 10 * math.log10(pwr)


def dbw_to_dbm(pwr):
    return pwr + 30


def str_to_float(string):
    s = re.sub(r'[^\d.]+', '', string)
    return float(s)


def average(data):
    if len(data) > 0:
        return sum(data) / len(data)
    else:
        return None


def find_geo(coord_1, coord_2):
    dy = coord_2[1] - coord_1[1]
    dx = coord_2[0] - coord_1[0]
    radians = math.atan2(dy, dx)
    return np.degrees(radians)


def get_color(i):
    colors_ = ['blueviolet', 'dodgerblue', 'mediumseagreen', 'deeppink', 'coral', 'royalblue', 'midnightblue',
               'yellowgreen', 'darkgreen', 'mediumblue', 'DarkOrange', 'green', 'red', 'MediumVioletRed',
               'darkcyan', 'orangered', 'purple', 'cornflowerblue', 'saddlebrown', 'indianred', 'fuchsia', 'DarkViolet',
               'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue',
               'slategray', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'black', 'grey',
               'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellow']
    return colors_[i % len(colors_)]


def get_bar_color(i):
    colors_ = ['blueviolet', 'mediumseagreen', 'deeppink', 'coral', 'royalblue', "MediumVioletRed", 'midnightblue',
               'yellowgreen', 'darkgreen', 'mediumblue', 'DarkViolet', 'DarkOrange', 'green', 'red',
               'darkcyan', 'orangered', 'purple', 'cornflowerblue', 'saddlebrown', 'indianred', 'fuchsia',
               'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue',
               'slategray', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'black', 'grey',
               'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellow']
    return colors_[i % len(colors_)]


def get_boxplot_color(i):
    colors_ = [(0.5411764705882353, 0.16862745098039217, 0.8862745098039215, 0.5), (0.11764705882352941, 0.5647058823529412, 1.0, 0.5),
               (0.23529411764705882, 0.7019607843137254, 0.44313725490196076, 0.5), (1.0, 0.0784313725490196, 0.5764705882352941, 0.5), 'coral', 'royalblue', 'midnightblue',
               'yellowgreen', 'darkgreen', 'mediumblue', 'DarkOrange', 'green', 'red', 'MediumVioletRed',
               'darkcyan', 'orangered', 'purple', 'cornflowerblue', 'saddlebrown', 'indianred', 'fuchsia', 'DarkViolet',
               'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue',
               'slategray', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'black', 'grey',
               'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellow']
    return colors_[i % len(colors_)]


def plot_bars(b, A, inpname, x_label_rotation=0, xlab="", ylab="", xlabels="",
              labels="", error=None, fontscale=2, dim=[7, 5], scale=2, legendpos="out", lloc=2,
              out_style=[".pdf"], x_grid=True, y_grid=True, yranges=None, OPACITY=0.9, BAR_EDGE_COLORS=False,
              PATTERNS=False):
    fontsize = 20
    fig = pyplot.figure(figsize=(dim[0], dim[1]))
    ax = pyplot.subplot(111)

    ax.set_axisbelow(True)
    ax.xaxis.grid(x_grid)
    ax.yaxis.grid(y_grid)

    if BAR_EDGE_COLORS:
        BAR_EDGE_COLORS = [get_color(i) for i in range(len(xlabels))]
    else:
        BAR_EDGE_COLORS = ['black'] * len(xlabels)

    h = pyplot.bar(b, A, align='center', width=0.30, color=[get_color(i) for i in range(len(xlabels))],
                   edgecolor=BAR_EDGE_COLORS, linewidth=1.0, alpha=OPACITY, label=labels)

    pyplot.ylabel(ylab)

    xticks_pos = [0.45 * patch.get_width() + patch.get_xy()[0] for patch in h]
    pyplot.xticks(xticks_pos, xlabels, ha='center', rotation=x_label_rotation)
    if yranges:
        pyplot.ylim(yranges[0], yranges[1])
    else:
        pyplot.ylim(min(A) * 0.6, max(A) * 1.05)

    pyplot.tick_params(axis='both', which='major', labelsize=fontsize)
    pyplot.xlabel(xlab, fontsize=fontsize)
    pyplot.ylabel(ylab, fontsize=fontsize)

    for os in out_style:
        pyplot.savefig(inpname + os, bbox_inches='tight')
    pyplot.close(pyplot.gcf())
