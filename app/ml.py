import random

import torch
from torchvision import models
from torchvision import transforms
from PIL import Image
import torch.nn as nn

from app.config import config


def load_model():
    global model, device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = models.resnet50(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 2)
    model.load_state_dict(torch.load(config.ml_path, map_location=torch.device('cpu')))
    model = model.to(device)
    model.eval()


classes = ['Faulty', 'Healthy']

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def predict(images_uuid):
    images = [transform(Image.open(f'{config.images_dir}/{str(img)}.jpg').convert("RGB")) for img in images_uuid]
    images = torch.stack(images)
    images = images.to(device)
    with torch.no_grad():
        outputs = model(images)
    _, predicted = torch.max(outputs, 1)
    items = [classes[pred.item()] for pred in predicted]
    return zip(images_uuid, items)

