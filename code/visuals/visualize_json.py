import json 

# to visualize bounding boxes
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import os 

img = "../../data/pngs/BOAS_1948_dict-p/9.png"

for i in range(1, 10):
    filename = f"temp-{i}"
    output_folder = "../../scratch/"
    json_path = f"../../scratch/{filename}.json"
    metadata = json.load(open(json_path))      
    im = Image.open(img)

    fig, ax = plt.subplots(figsize=(10,10))  # Create figure and axes
    ax.imshow(im) # Display the image
    for key in metadata.keys(): # Create Polygon patches
        entry = metadata[key] # Looking through all the bounding boxes detected in this image
        if type(entry) is dict and "bounding_box" in entry.keys(): # Looking for the coordinates 
            box_coords = entry["bounding_box"]
            poly = Polygon(box_coords, fill=False, edgecolor='red')
            ax.add_patch(poly) # Add the patch to the Axes
    box_path = "".join([output_folder, "bounding_boxes/"])

    if not os.path.exists(box_path):
        os.makedirs(box_path)
    filepath = "".join([box_path, filename, ".png"])
    plt.savefig(filepath)
    plt.close()

