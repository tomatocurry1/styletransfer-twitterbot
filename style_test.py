import os 
from time import time
from style_component import StyleComponent

def checkOutputImage():

	if os.path.exists("output.jpg"):
		os.remove("output.jpg")

	contentImage = "surfer.jpg"
    
	start = time()
	StyleComponent().transfer(contentImage, StyleComponent.styleImages['tsunami'])
	print(time()-start)

	return os.path.exists("output.jpg")





if __name__ == '__main__':
	assert checkOutputImage()