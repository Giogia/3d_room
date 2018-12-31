import torch
import torch.nn.parallel
from PIL import Image
import numpy as np

import depth_network
from depth_model import Model, E_senet
import depth_utils
import os


def define_model():

    original_model = depth_network.senet154(pretrained='imagenet')
    encoder = E_senet(original_model)
    model = Model(encoder, num_features=2048, block_channel = [256, 512, 1024, 2048])

    return model
   

def depth(img):
    model = define_model()
    model = torch.nn.DataParallel(model).cuda()
    model.load_state_dict(torch.load('pretrained_model/model_senet'))#, map_location={'cuda:0': 'cpu'}))
    model.eval()

    loader = depth_utils.load(img)


    for i, tensor in enumerate(loader):

        with torch.no_grad():

            tensor = torch.autograd.Variable(tensor).cuda()

        depth = model(tensor)

        depth = depth.view(depth.size(2),depth.size(3)).data.cpu().numpy()
        depth = (depth * 255 / np.max(depth)).astype('uint8')
        depth = Image.fromarray(depth).resize((img.size[0],img.size[1]), Image.BILINEAR)

    return depth


path = os.getcwd() + '/../result/res_panofull_ts_box_joint/depth'

if not os.path.isdir(path):

    os.mkdir(path)


for i in range(1,54):

    for j in range(5):

        img = Image.open('../result/res_panofull_ts_box_joint/persp/' + str(i) + '-' + str(j) + '.png')
        depth_map = depth(img)
        depth_map.save('../result/res_panofull_ts_box_joint/depth/' + str(i) + '-' + str(j) + 'd.png')

    print(i)


