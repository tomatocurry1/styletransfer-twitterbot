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

from style_transfer_basis import get_style_model_and_losses, image_loader, unloader, run_style_transfer, device, cnn_normalization_mean, cnn_normalization_std, cnn

class StyleComponent:

    styleImages = {'starry night': "starry-night.jpg", 'tsunami': "hokusai_tsunami.jpg", 'udnie': "udnie.jpg"}


    def __init__(self):
        
        self.scalefactor = 320*320         



    def transfer(self, contentImage, styleImage):
        size = self.calculateSize(Image.open(contentImage))


        
        contentImage = image_loader(contentImage, size)
        styleImage = image_loader(styleImage, size)
        
        

        input_img = contentImage.clone()
        styled_output = run_style_transfer(cnn, cnn_normalization_mean, cnn_normalization_std,
                            contentImage, styleImage, input_img)

        

        
        save_image(styled_output, "output.jpg")

    def calculateSize(self, contentImage):
        width = contentImage.width
        height = contentImage.height



        scale = sqrt(self.scalefactor/(width*height))




        return int(scale*height), int(scale*width )



if __name__ == '__main__':
    contentImage = "surfer.jpg"
    styleImage = "starry-night.jpg"
    from time import time
    start = time()
    StyleComponent().transfer(contentImage, StyleComponent.styleImages['tsunami'])
    print(time()-start)
