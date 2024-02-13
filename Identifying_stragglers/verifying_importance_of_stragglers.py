import copy

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import tqdm

from neural_networks import SimpleNN
from utils import (load_data, interpolate_colors, straggler_ratio_vs_generalisation, train_stop_at_inversion,
                   transform_datasets_to_dataloaders)

# Load the dataset. We copy the batch size from the "Inversion dynamics of class manifolds in deep learning ..." paper
train_dataset, test_dataset, full_dataset = load_data()
train_loader, test_loader, full_loader = transform_datasets_to_dataloaders(
    [train_dataset, test_dataset, full_dataset], 70000)
stragglers = [None for _ in range(10)]
# Instantiate the model, loss function, optimizer and learning rate scheduler
model = SimpleNN(28*28, 2, 40, 1)
model1 = copy.deepcopy(model)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.1)
# Run the training process
num_epochs = 500
models = train_stop_at_inversion(model, full_loader, optimizer, criterion, num_epochs)
# Calculate the number of steps in your gradient
train_ratios = list(np.arange(0.9, 0, -0.1))
n_ratios = len(train_ratios)
# Define your edge colors and select a colormap for the gradients
start_color = (0, 0, 0)
end_color = (192, 192, 192)  # This represents a silver color
colors = interpolate_colors(start_color, end_color, n_ratios)
for idx, train_ratio in tqdm.tqdm(enumerate(train_ratios), desc='Going through different train:test ratios'):
    straggler_data = torch.tensor([], dtype=torch.float32)
    straggler_target = torch.tensor([], dtype=torch.long)
    non_straggler_data = torch.tensor([], dtype=torch.float32)
    non_straggler_target = torch.tensor([], dtype=torch.long)
    for data, target in full_loader:
        for i in range(10):
            if models[i] is not None:
                stragglers[i] = ((torch.argmax(model(data), dim=1) != target) & (target == i))
                current_non_stragglers = (torch.argmax(model(data), dim=1) == target) & (target == i)
                # Concatenate the straggler data and targets
                straggler_data = torch.cat((straggler_data, data[stragglers[i]]), dim=0)
                straggler_target = torch.cat((straggler_target, target[stragglers[i]]), dim=0)
                # Concatenate the non-straggler data and targets
                non_straggler_data = torch.cat((non_straggler_data, data[current_non_stragglers]), dim=0)
                non_straggler_target = torch.cat((non_straggler_target, target[current_non_stragglers]), dim=0)
    print(f'A total of {len(straggler_data)} stragglers and {len(non_straggler_data)} non-stragglers were found.')
    straggler_ratios, avg_accuracies, std_accuracies = straggler_ratio_vs_generalisation(
        straggler_data, straggler_target, non_straggler_data, non_straggler_target, train_ratio)
    print(f'For train_ratio = {train_ratio} we get average accuracies of {avg_accuracies}.')

    plt.errorbar(straggler_ratios, avg_accuracies, yerr=std_accuracies, marker='o', capsize=5, color=colors[idx])
plt.xlabel('Ratio of Stragglers in Train Set')
plt.ylabel('Accuracy on Test Set (%)')
plt.title('Test Set Accuracy vs. Straggler Ratio')
plt.grid(True)
plt.savefig('Figures/generalisation_vs_straggler_ratio.png')
plt.savefig('Figures/generalisation_vs_straggler_ratio.pdf')
plt.show()
