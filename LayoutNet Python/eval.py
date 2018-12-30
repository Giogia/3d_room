import argparse

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from Lines.model import Encoder, Decoder
from Lines.dataset import PanoDataset
from Lines.utils import StatisticDict


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# Model related arguments
parser.add_argument('--path_prefix', default='ckpt/pre',
                    help='prefix path to load model.')
parser.add_argument('--device', default='cuda:0',
                    help='device to run models.')
# Dataset related arguments
parser.add_argument('--root_dir', default='data/test',
                    help='root directory to construct dataloader.')
parser.add_argument('--input_cat', default=['img', 'line'], nargs='+',
                    help='input channels subdirectories')
parser.add_argument('--input_channels', default=6, type=int,
                    help='numbers of input channels')
parser.add_argument('--num_workers', default=6, type=int,
                    help='numbers of workers for dataloaders')
parser.add_argument('--batch_size', default=4, type=int,
                    help='mini-batch size')
args = parser.parse_args()
device = torch.device(args.device)


# Create dataloader
dataset = PanoDataset(root_dir=args.root_dir,
                      cat_list=[*args.input_cat, 'edge', 'cor'],
                      flip=False, rotate=False,
                      gamma=False)
loader = DataLoader(dataset, args.batch_size,
                    shuffle=False, drop_last=False,
                    num_workers=args.num_workers,
                    pin_memory=args.device.startswith('cuda'))


# Prepare model
encoder = Encoder(args.input_channels).to(device)
edg_decoder = Decoder(skip_num=2, out_planes=3).to(device)
cor_decoder = Decoder(skip_num=3, out_planes=1).to(device)
encoder.load_state_dict(torch.load('%s_encoder.pth' % args.path_prefix))
edg_decoder.load_state_dict(torch.load('%s_edg_decoder.pth' % args.path_prefix))
cor_decoder.load_state_dict(torch.load('%s_cor_decoder.pth' % args.path_prefix))


# Start evaluation
criti = nn.BCEWithLogitsLoss(reduction='none')
test_losses = StatisticDict()
for ith, datas in enumerate(loader):
    print('processed %d batches out of %d' % (ith, len(loader)), end='\r', flush=True)
    with torch.no_grad():
        # Prepare data
        x = torch.cat([datas[i]
                      for i in range(len(args.input_cat))], dim=1).to(device)
        y_edg = datas[-2].to(device)
        y_cor = datas[-1].to(device)
        b_sz = x.size(0)

        # Feedforward
        en_list = encoder(x)
        edg_de_list = edg_decoder(en_list[::-1])
        cor_de_list = cor_decoder(en_list[-1:] + edg_de_list[:-1])
        y_edg_ = edg_de_list[-1]
        y_cor_ = cor_de_list[-1]

        # Compute training objective loss
        loss_edg = criti(y_edg_, y_edg)
        loss_edg[y_edg == 0.] *= 0.2
        loss_edg = loss_edg.mean().item()
        loss_cor = criti(y_cor_, y_cor)
        loss_cor[y_cor == 0.] *= 0.2
        loss_cor = loss_cor.mean().item()

    test_losses.update('edg loss', loss_edg, weight=b_sz)
    test_losses.update('cor loss', loss_cor, weight=b_sz)

print('[RESULT] %s' % (test_losses), flush=True)
