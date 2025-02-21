from io import BytesIO

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common_utils.utils import get_types_dict
from PIL import Image
from singleton import realm

HIST_COUNTS = {}
HIST_REFRESH_TIMES = 0


def generate_map():

    # Create a new image with a white background
    width = realm.MAP.size_x
    height = realm.MAP.size_y
    image = Image.new("RGB", (width, height), "white")

    # Get the pixel access object
    pixels = image.load()

    # Generate a simple gradient
    for x in range(0, realm.MAP.size_x):
        for y in range(0, realm.MAP.size_y):

            index = realm.TILES[(x, y)].occupied_by

            if index:
                obj = realm.OBJECT_LIST[index]
            else:
                obj = None

            if not obj:
                r = 195
                g = 168
                b = 86
            else:
                r = obj.rgb_map[0]
                g = obj.rgb_map[1]
                b = obj.rgb_map[2]

            pixels[x, y] = (r, g, b)

    # Save the image

    f = BytesIO()

    # image.save("static/other/map_image.png")
    image.save(f, format="PNG")

    realm.REDIS_CONNECTION.set(f"map_image", f.getvalue())


def get_plot_by_spicies(interval=100, hist=100):

    plt.clf()

    global HIST_COUNTS

    types_dict = get_types_dict()

    if not HIST_COUNTS:
        HIST_COUNTS = {obj_name: {} for obj_name, _ in types_dict.items()}

    for i, o in realm.OBJECT_LIST.items():

        HIST_COUNTS[o.type_name][int(realm.EPOCH_COUNTER / interval)] = (
            HIST_COUNTS[o.type_name].get(int(realm.EPOCH_COUNTER / interval), 0) + 1
        )

    for obj_name, _ in types_dict.items():
        if HIST_COUNTS[obj_name].get(int(realm.EPOCH_COUNTER / interval) - hist):
            del HIST_COUNTS[obj_name][int(realm.EPOCH_COUNTER / interval) - hist]

    x = []
    y_list = {}

    for epoch in range(
        max(0, int(realm.EPOCH_COUNTER / interval) - hist + 1),
        int(realm.EPOCH_COUNTER / interval) + 1,
    ):
        x.append(epoch * interval)

        for o, _ in types_dict.items():
            cnt = HIST_COUNTS[o].get(epoch, 0)

            if not y_list.get(o):
                y_list[o] = []

            y_list[o].append(cnt)

    for o, y in y_list.items():
        plt.semilogy(x, y, color=[color / 255 for color in types_dict[o].rgb_map])

    ax = plt.gca()
    # ax.set_facecolor(face_col)
    ax.spines["bottom"].set_color("white")
    ax.spines["top"].set_color("white")
    ax.spines["left"].set_color("white")
    ax.spines["right"].set_color("white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.grid(alpha=0.1)
    ax.title.set_color("white")
    ax.tick_params(axis="x", colors="white")
    ax.tick_params(axis="y", colors="white")

    # Add labels and title
    plt.xlabel("Time in refreshes")
    plt.ylabel("Count of different animal/plant types")

    f = BytesIO()
    # Save the plot to a file
    plt.savefig(f, transparent=True)  # Saves as PNG by default
    # plt.savefig("sine_wave.pdf")  # To save as PDF
    # plt.savefig("sine_wave.jpg", dpi=300) # To save as JPG with 300 DPI

    # Display the plot (optional, if you also want to see it)
    # plt.show()

    realm.REDIS_CONNECTION.set(f"counts_historical_plot", f.getvalue())


def get_refresh_time_plot(interval=100, hist=1000):

    plt.clf()

    global HIST_REFRESH_TIMES

    types_dict = get_types_dict()

    if not HIST_REFRESH_TIMES:
        HIST_REFRESH_TIMES = {}

    HIST_COUNTS[int(realm.EPOCH_COUNTER / interval)] = realm.LAST_REFRESH_TIME

    if HIST_COUNTS.get(int(realm.EPOCH_COUNTER / interval) - hist):
        del HIST_COUNTS[int(realm.EPOCH_COUNTER / interval) - hist]

    x = []
    y = []

    for epoch in range(
        max(0, int(realm.EPOCH_COUNTER / interval) - hist + 1),
        int(realm.EPOCH_COUNTER / interval) + 1,
    ):
        x.append(epoch * interval)
        y.append(HIST_COUNTS.get(epoch, 0))

    plt.plot(x, y, color="white")

    ax = plt.gca()
    # ax.set_facecolor(face_col)
    ax.spines["bottom"].set_color("white")
    ax.spines["top"].set_color("white")
    ax.spines["left"].set_color("white")
    ax.spines["right"].set_color("white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.grid(alpha=0.1)
    ax.title.set_color("white")
    ax.tick_params(axis="x", colors="white")
    ax.tick_params(axis="y", colors="white")

    # Add labels and title
    plt.xlabel("Time in refreshes")
    plt.ylabel("World refresh time / ms")

    f = BytesIO()
    # Save the plot to a file
    plt.savefig(f, transparent=True)  # Saves as PNG by default
    # plt.savefig("sine_wave.pdf")  # To save as PDF
    # plt.savefig("sine_wave.jpg", dpi=300) # To save as JPG with 300 DPI

    # Display the plot (optional, if you also want to see it)
    # plt.show()

    realm.REDIS_CONNECTION.set(f"refresh_time_plot", f.getvalue())
