from PIL import Image

def remove_checkerboard(image_path, output_path):
    img = Image.open(image_path).convert("RGBA")
    data = img.getdata()
    
    new_data = []
    # Let's consider standard checkerboard colors.
    # We can also just check if the pixel is close to white or light gray.
    for item in data:
        # item is (r, g, b, a)
        r, g, b, a = item
        # If the pixel is very bright gray/white (e.g., > 200 in all channels)
        # And R, G, B are very close to each other (neutral)
        if r > 200 and g > 200 and b > 200 and abs(r-g) < 10 and abs(g-b) < 10:
            new_data.append((255, 255, 255, 0)) # transparent
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(output_path, "PNG")

if __name__ == "__main__":
    remove_checkerboard("frontend/favicon.png", "frontend/favicon.png")
