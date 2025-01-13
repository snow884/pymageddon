from io import BytesIO

from PIL import Image
from singleton import realm


def generate_map():

    # Create a new image with a white background
    width = 200
    height = 200
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
