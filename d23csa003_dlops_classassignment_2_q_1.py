# -*- coding: utf-8 -*-
"""D23CSA003_DLOps_ClassAssignment_2_Q_1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XuVdrWOI73f0-CPzuT-wMrfYVdT7lW5F
"""

!pip install tensorboardX

import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import numpy as np

torch.manual_seed(10) #Changed in version2
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

batch_size = 32  #Changed
learning_rate = 0.0001  #Changed
num_epochs = 20  #Changed

import torchvision.transforms as transforms
from torchvision.datasets import USPS
from torch.utils.data import DataLoader, TensorDataset

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=(0.5,), std=(0.5,))
])

train_dataset = USPS(root='./data', train=True, transform=transform, download=True)
test_dataset = USPS(root='./data', train=False, transform=transform, download=True)

train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False)

class MLP(nn.Module):
    def __init__(self):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(16*16, 256)
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=5, stride=1, padding=2)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=5, stride=1, padding=2)
        self.fc1 = nn.Linear(32*4*4, 256)
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

from sklearn.metrics import confusion_matrix, precision_score, recall_score
from torch.utils.tensorboard import SummaryWriter

def train(model, train_loader, criterion, optimizer, epoch, writer):
    model.train()
    running_loss = 0.0
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    avg_loss = running_loss / len(train_loader)
    print(f'Training Loss Epoch {epoch + 1}: {avg_loss:.4f}')
    writer.add_scalar('Training Loss', avg_loss, epoch)
    return avg_loss

def test(model, test_loader, writer, epoch):
    model.eval()
    correct = 0
    total = 0
    predicted_labels = []
    true_labels = []
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            _, predicted = torch.max(output.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
            predicted_labels.extend(predicted.cpu().numpy())
            true_labels.extend(target.cpu().numpy())
    accuracy = 100 * correct / total
    precision = precision_score(true_labels, predicted_labels, average='macro')
    recall = recall_score(true_labels, predicted_labels, average='macro')
    cm = confusion_matrix(true_labels, predicted_labels)
    print(f'Testing Precision: {precision:.2f}, Recall: {recall:.2f}')  #Setting pricison to 2 in version2
    writer.add_scalar('Accuracy', accuracy, epoch)
    writer.add_scalar('Precision', precision, epoch)
    writer.add_scalar('Recall', recall, epoch)
    writer.add_figure('Confusion Matrix', plot_confusion_matrix(cm), epoch)
    plot_confusion_matrix(cm)
    return accuracy, precision, recall

def plot_confusion_matrix(cm):
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    plt.xticks(np.arange(10))
    plt.yticks(np.arange(10))
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, format(cm[i, j], 'd'), horizontalalignment="center", color="white" if cm[i, j] > cm.max() / 2 else "black")
    plt.tight_layout()
    return plt.gcf()

mlp_model = MLP().to(device)
cnn_model = CNN().to(device)

criterion = nn.CrossEntropyLoss()
mlp_optimizer = optim.Adam(mlp_model.parameters(), lr=learning_rate)
cnn_optimizer = optim.Adam(cnn_model.parameters(), lr=learning_rate)

mlp_writer = SummaryWriter('./logs/mlp')
cnn_writer = SummaryWriter('./logs/cnn')

for epoch in range(num_epochs):
    mlp_loss = train(mlp_model, train_loader, criterion, mlp_optimizer, epoch, mlp_writer)

mlp_accuracy, mlp_precision, mlp_recall = test(mlp_model, test_loader, mlp_writer, num_epochs)
mlp_writer.close()

print("MLP Model:")
print(f"Accuracy: {mlp_accuracy:.2f}%")
print(f"Precision: {mlp_precision:.4f}")
print(f"Recall: {mlp_recall:.4f}")

for epoch in range(num_epochs):
    cnn_loss = train(cnn_model, train_loader, criterion, cnn_optimizer, epoch, cnn_writer)

cnn_accuracy, cnn_precision, cnn_recall = test(cnn_model, test_loader, cnn_writer, num_epochs)
cnn_writer.close()

print("\nCNN Model:")
print(f"Accuracy: {cnn_accuracy:.2f}%")
print(f"Precision: {cnn_precision:.4f}")
print(f"Recall: {cnn_recall:.4f}")

# Commented out IPython magic to ensure Python compatibility.
!kill 8487
# %reload_ext tensorboard

log_dir = "/content/logs"

# %tensorboard --logdir $log_dir

# !rm -r data logs

