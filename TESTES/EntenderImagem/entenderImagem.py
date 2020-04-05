from matplotlib import image
from matplotlib import pyplot
from PIL import Image

data = image.imread("anime1.jpg")

print(data)
print(pyplot.imshow(data))