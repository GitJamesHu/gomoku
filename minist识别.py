import os
import torch
import torchvision
from altair import data_transformers
from openai.types.beta.threads.runs.code_interpreter_output_image import Image
from torchvision import datasets, transforms, models
import imageio
import numpy as np
from torch.utils.data import Dataset, DataLoader

# 先把字典做好

# 然后做两个list
data_info_PATH = '/Users/hujianwen/Desktop/AI/DataLoader definition/flower_data/train.txt'
# train_name = list(data_info.keys())
# train_label = list(data_info.values())

root_dir = '/Users/hujianwen/Desktop/AI/DataLoader definition/flower_data/'
train_dir = root_dir + 'train_filelist'
valid_dir = root_dir + 'val_filelist'

# image_Path = [os.path.join(train_dir, x) for x in train_name]

def FlowerDataset(Dataset):
    def __init__(self, root_dir, ann_file, transform = None):
        self.root_dir = root_dir
        self.ann_file = ann_file
        self.data_info = self.load_annotations()
        self.img = [os.path.join(root_dir, x) for x in list(self.data_info.keys())]
        self.label = list(self.data_info.values())
        self.transform = transform

    def __len__(self):
        return len(self.data_info)

    def __get_item__(self, idx):
        image = Image.open(self.img[idx])
        label = self.label[idx]
        if self.transform:
            image = self.transform(image)
        label = torch.from_numpy(np.array(label))
        return image, label
    def load_annotations(self):
        data_info = {}
        with open(self.ann_file) as f:
            data_list = [x.strip().split() for x in f.readlines()]
            for filename, label in data_list:
                data_info[filename] = label
        return data_info

data_transformers = {
    'train':
        transforms.Compose([
            transforms.Resize(96),
            transforms.RandomRotation(45),
            transforms.CenterCrop(64),
            transforms.RandomHorizontalFlip(0.5),
            transforms.RandomVerticalFlip(0.5),
            transforms.ColorJitter(brightness=0.3, saturation=0.2, hue=0.1,contrast=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ]
        ),
    'valid':
        transforms.Compose([
            transforms.Resize(64),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ]
        )
}

train_dataset = FlowerDataset(root_dir='/Users/hujianwen/Desktop/AI/DataLoader definition/flower_data/train_filelist', ann_file='/Users/hujianwen/Desktop/AI/DataLoader definition/flower_data/train.txt', transform = data_transformers['train'])
print(train_dataset.label)