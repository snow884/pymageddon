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
                if obj.type_name in ("Grass", "Seed"):
                    r = 0
                    g = 240
                    b = 0
                elif obj.type_name == "Stone":
                    r = 178
                    g = 182
                    b = 167
                elif obj.is_player:
                    r = 0
                    g = 0
                    b = 255
                else:
                    r = 0
                    g = 0
                    b = 0

            pixels[x, y] = (r, g, b)

    # Save the image
    image.save("static/other/map_image.png")
