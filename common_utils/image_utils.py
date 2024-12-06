from PIL import Image


def generate_map(TILES, MAP, OBJECT_LIST):

    # Create a new image with a white background
    width = 200
    height = 200
    image = Image.new("RGB", (width, height), "white")

    # Get the pixel access object
    pixels = image.load()

    # Generate a simple gradient
    for x in range(0, MAP.size_x):
        for y in range(0, MAP.size_y):

            index = TILES[(x, y)].occupied_by

            if index:
                obj = OBJECT_LIST[index]
            else:
                obj = None

            if not obj:
                r = 0
                g = 0
                b = 0
            else:
                if obj.type_name == "Grass":

                    r = 0
                    g = 255
                    b = 0
                else:
                    r = 255
                    g = 255
                    b = 255

            pixels[x, y] = (r, g, b)

    # Save the image
    image.save("static/other/map_image.png")
