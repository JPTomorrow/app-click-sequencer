import io
import os, sys
import requests
import PIL

import torch
import torchvision.transforms as T
import torchvision.transforms.functional as TF

from dall_e import map_pixels, unmap_pixels, load_model
from IPython.display import display, display_markdown

import torch.nn.functional as F

class ImageMaker:
    def __init__(self):
        self.TargetImageSize = 256
        # This can be changed to a GPU, e.g. 'cuda:0'.
        dev = torch.device('cpu')

        # For faster load times, download these files locally and use the local paths instead.
        self.Encode = load_model("https://cdn.openai.com/dall-e/encoder.pkl", dev)
        self.Decode = load_model("https://cdn.openai.com/dall-e/decoder.pkl", dev)

        self.diplay()

    def download_image(self, url):
        resp = requests.get(url)
        resp.raise_for_status()
        return PIL.Image.open(io.BytesIO(resp.content))

    def preprocess(self, img):
        s = min(img.size)
        
        if s < self.TargetImageSize:
            raise ValueError(f'min dim for image {s} < {self.TargetImageSize}')
            
        r = self.TargetImageSize / s
        s = (round(r * img.size[1]), round(r * img.size[0]))
        img = TF.resize(img, s, interpolation=PIL.Image.LANCZOS)
        img = TF.center_crop(img, output_size=2 * [self.TargetImageSize])
        img = torch.unsqueeze(T.ToTensor()(img), 0)
        return map_pixels(img)

    def diplay6(self):
        enc = self.Encode
        dec = self.Decode

        x = self.preprocess(self.download_image('https://assets.bwbx.io/images/users/iqjWHBFdfxIU/iKIWgaiJUtss/v2/1000x-1.jpg'))
        display_markdown('Original image:')
        display(T.ToPILImage(mode='RGB')(x[0]))

        z_logits = enc(x)
        z = torch.argmax(z_logits, axis=1)
        z = F.one_hot(z, num_classes=enc.vocab_size).permute(0, 3, 1, 2).float()

        x_stats = dec(z).float()
        x_rec = unmap_pixels(torch.sigmoid(x_stats[:, :3]))
        x_rec = T.ToPILImage(mode='RGB')(x_rec[0])

        display_markdown('Reconstructed image:')
        display(x_rec)
        
        





