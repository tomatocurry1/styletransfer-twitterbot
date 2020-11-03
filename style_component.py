import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from PIL import Image
import matplotlib.pyplot as plt

import torchvision.transforms as transforms
import torchvision.models as models
from torchvision.utils import save_image 
import time
from math import log, ceil, sqrt

import copy

from style_transfer_basis import get_style_model_and_losses, image_loader, unloader, run_style_transfer, device, cnn_normalization_mean, cnn_normalization_std

class StyleComponent:




    def __init__(self):
        self.styleImages = ["starry-night.jpg"]
        self.size = (320, 320)
        self.scalefactor = 320*320         





    def transfer(self, contentImage, styleImage):
        size = self.calculateSize(Image.open(contentImage))


        print(size)
        contentImage = image_loader(contentImage, size)
        styleImage = image_loader(styleImage, size)
        
        cnn = models.vgg19(pretrained=True).features.to(device).eval()

        input_img = contentImage.clone()
        styled_output = run_style_transfer(cnn, cnn_normalization_mean, cnn_normalization_std,
                            contentImage, styleImage,input_img)

        

        
        save_image(styled_output, "output.jpg")

    def calculateSize(self, contentImage):
        width = contentImage.width
        height = contentImage.height



        scale = sqrt(self.scalefactor/(width*height))




        return int(scale*height), int(scale*width )



if __name__ == '__main__':
    contentImage = "chicken.png"
    styleImage = "starry-night.jpg"
    from time import time
    start = time()
    StyleComponent().transfer(contentImage, styleImage)
    print(time()-start)
