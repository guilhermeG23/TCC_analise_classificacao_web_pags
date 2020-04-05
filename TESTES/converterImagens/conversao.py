import os
from PIL import Image

files = []
for r, d, f in os.walk("./Anime"):
    for file in f:
        files.append(os.path.join(r, file))

for f in files:
    img = Image.open(f).convert('L')
    img.save(f)
