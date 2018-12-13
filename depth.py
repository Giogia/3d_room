import torch
import torch.nn.parallel
from PIL import Image
import numpy as np

import network
from model import Model, E_senet
import depth_utils

import matplotlib.image


def define_model():

    original_model = network.senet154(pretrained='imagenet')
    encoder = E_senet(original_model)
    model = Model(encoder, num_features=2048, block_channel = [256, 512, 1024, 2048])

    return model
   

def depth(img):
    model = define_model()
    model = torch.nn.DataParallel(model)#.cuda()
    model.load_state_dict(torch.load('pretrained_model/model_senet', map_location={'cuda:0': 'cpu'}))
    model.eval()

    loader = depth_utils.load(img)

    for i, tensor in enumerate(loader):
        tensor = torch.autograd.Variable(tensor)  # , volatile=True).cuda()
        depth = model(tensor)

        depth = depth.view(depth.size(2),depth.size(3)).data.cpu().numpy()
        depth = (depth * 255 / np.max(depth)).astype('uint8')
        depth = Image.fromarray(depth).resize((img.size[0],img.size[1]), Image.BILINEAR)

    return depth


# test the class
if __name__ == '__main__':

    img = Image.open('assets/wall1.jpg')
    depth = depth(img)
    depth.save('assets/floor_d.jpg')


