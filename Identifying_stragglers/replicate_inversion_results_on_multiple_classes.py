import matplotlib.pyplot as plt
import torch.nn as nn
import torch.optim as optim

from neural_networks import SimpleNN
from utils import load_data, plot_radii, test, train_model, transform_datasets_to_dataloaders

# Load the dataset. We copy the batch size from the "Inversion dynamics of class manifolds in deep learning ..." paper
train_dataset, test_dataset, _ = load_data()
train_loader, test_loader = transform_datasets_to_dataloaders([train_dataset, test_dataset], 8192)
all_epoch_radii, all_error_radii = [], []
for _ in range(1):
    # Instantiate the model, loss function, optimizer and learning rate scheduler
    model = SimpleNN(28*28, 2, 20, 1)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.1)
    # Run the training process
    num_epochs = 500
    epoch_radii, error_radii = train_model(model, train_loader, optimizer, criterion, num_epochs)
    print(f'The model achieved the accuracy of {round(test(model, train_loader), 4)}% on the train set, and '
          f'{round(test(model, test_loader), 4)}% on the test set')
    all_epoch_radii.append(epoch_radii)
    all_error_radii.append(error_radii)
# Plot the results
plot_radii('Epoch', all_epoch_radii)
plot_radii('Error', all_error_radii)
plt.show()
