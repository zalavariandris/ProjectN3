def merge_images(file_paths):
    import os
    from PIL import Image
    print("merge files")
    # merge images
    total_width = 12000
    total_height = 8000
    rows = 6
    cols = 4
    canvas = Image.new('RGB', (total_width, total_height))
    for i, filename in enumerate(file_paths):
        print(i)
        img = Image.open(filename)
        x_offset = i%rows*2000
        y_offset = i//rows*2000
        canvas.paste(img, (x_offset, y_offset))
    return canvas

    # for filename in file_paths:
    #     os.remove(filename)

if __name__ == "__main__":
    img = merge_images([
        "capture_0-0.png", "capture_2000-0.png", "capture_4000-0.png", "capture_6000-0.png", "capture_8000-0.png", "capture_10000-0.png", 
        "capture_0-2000.png", "capture_2000-2000.png", "capture_4000-2000.png", "capture_6000-2000.png", "capture_8000-2000.png", "capture_10000-2000.png", 
        "capture_0-4000.png", "capture_2000-4000.png", "capture_4000-4000.png", "capture_6000-4000.png", "capture_8000-4000.png", "capture_10000-4000.png", 
        "capture_0-6000.png", "capture_2000-6000.png", "capture_4000-6000.png", "capture_6000-6000.png", "capture_8000-6000.png", "capture_10000-6000.png"
        ])

    canvas.save(img, "TIFF")