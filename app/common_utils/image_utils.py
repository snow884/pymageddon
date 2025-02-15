from io import BytesIO

from PIL import Image
from singleton import realm


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


def get_plot_by_spicies():

    global HIST_COUNTS

    cnt_dict = {}

    for i, o in realm.OBJECT_LIST.items():
        cnt_dict[o.type_name] = cnt_dict.get(o.type_name, 0) + 1

    # Generate some sample data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # Create the plot
    plt.plot(x, y)

    # Add labels and title
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Sine Wave Plot")

    # Save the plot to a file
    plt.savefig("sine_wave.png")  # Saves as PNG by default
    # plt.savefig("sine_wave.pdf")  # To save as PDF
    # plt.savefig("sine_wave.jpg", dpi=300) # To save as JPG with 300 DPI

    # Display the plot (optional, if you also want to see it)
    plt.show()

    realm.REDIS_CONNECTION.set(f"counts_historical_plot", f.getvalue())
