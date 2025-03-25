import os
import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

# ==================== ScUnicorn Model ====================
class BasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0)

    def forward(self, x):
        return self.conv(x)


class ResidualBlock(nn.Module):
    def __init__(self, num_channels):
        super().__init__()
        self.conv1 = nn.Conv2d(num_channels, num_channels, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(num_channels, num_channels, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        out = F.relu(self.conv1(x), inplace=True)
        out = F.relu(self.conv2(out) + x, inplace=True)
        return out


class CascadingBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.r1 = ResidualBlock(channels)
        self.r2 = ResidualBlock(channels)
        self.r3 = ResidualBlock(channels)
        self.c1 = BasicBlock(channels * 2, channels)
        self.c2 = BasicBlock(channels * 3, channels)
        self.c3 = BasicBlock(channels * 4, channels)

    def forward(self, x):
        c0 = o0 = x
        b1 = self.r1(o0)
        c1 = torch.cat([c0, b1], dim=1)
        o1 = self.c1(c1)

        b2 = self.r2(o1)
        c2 = torch.cat([c1, b2], dim=1)
        o2 = self.c2(c2)

        b3 = self.r3(o2)
        c3 = torch.cat([c2, b3], dim=1)
        o3 = self.c3(c3)

        return o3


class ScUnicorn(nn.Module):  # Renamed model
    def __init__(self, num_channels=64):
        super().__init__()
        self.entry = nn.Conv2d(1, num_channels, kernel_size=3, stride=1, padding=1)

        self.cb1 = CascadingBlock(num_channels)
        self.cb2 = CascadingBlock(num_channels)
        self.cb3 = CascadingBlock(num_channels)
        self.cb4 = CascadingBlock(num_channels)
        self.cb5 = CascadingBlock(num_channels)

        self.cv1 = nn.Conv2d(num_channels * 2, num_channels, kernel_size=1, stride=1, padding=0)
        self.cv2 = nn.Conv2d(num_channels * 3, num_channels, kernel_size=1, stride=1, padding=0)
        self.cv3 = nn.Conv2d(num_channels * 4, num_channels, kernel_size=1, stride=1, padding=0)
        self.cv4 = nn.Conv2d(num_channels * 5, num_channels, kernel_size=1, stride=1, padding=0)
        self.cv5 = nn.Conv2d(num_channels * 6, num_channels, kernel_size=1, stride=1, padding=0)

        self.exit = nn.Conv2d(num_channels, 1, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        x = self.entry(x)
        c0 = o0 = x
        b1 = self.cb1(o0)
        c1 = torch.cat([c0, b1], dim=1)
        o1 = self.cv1(c1)

        b2 = self.cb2(o1)
        c2 = torch.cat([c1, b2], dim=1)
        o2 = self.cv2(c2)

        b3 = self.cb3(o2)
        c3 = torch.cat([c2, b3], dim=1)
        o3 = self.cv3(c3)

        b4 = self.cb4(o3)
        c4 = torch.cat([c3, b4], dim=1)
        o4 = self.cv4(c4)

        b5 = self.cb5(o4)
        c5 = torch.cat([c4, b5], dim=1)
        o5 = self.cv5(c5)

        out = self.exit(o5)
        return out


# ==================== Data Processing Functions ====================
def reconstruct_matrix(matlist, indices):
    """ Reconstructs the ScUnicorn matrix chromosome-wise. """
    if indices.shape[1] < 4:
        raise ValueError(f"Invalid indices shape: {indices.shape}, expected (N, 4)")

    unique_chromosomes = np.unique(indices[:, 0])
    matrices = {}

    for chrom in unique_chromosomes:
        chr_indices = indices[indices[:, 0] == chrom]
        chr_mats = matlist[indices[:, 0] == chrom]

        max_x = (chr_indices[:, -2] + 40).max()
        max_y = (chr_indices[:, -1] + 40).max()

        if max_x <= 0 or max_y <= 0:
            raise ValueError(f"Invalid matrix size for chromosome {chrom}: ({max_x}, {max_y}). Check indices.")

        chr_matrix = np.zeros((max_x, max_y))

        for i in range(len(chr_indices)):
            x, y = chr_indices[i, -2], chr_indices[i, -1]
            chr_matrix[x:x+40, y:y+40] = chr_mats[i].squeeze()

        matrices[str(int(chrom))] = chr_matrix

    return matrices


def load_data(input_file):
    data = np.load(input_file, allow_pickle=True)
    inputs = torch.tensor(data['data'], dtype=torch.float)
    indices = torch.tensor(data['inds'], dtype=torch.long)

    dataset = TensorDataset(inputs, indices)
    loader = DataLoader(dataset, batch_size=64, shuffle=False)

    return loader, indices


# ==================== Inference Function ====================
def run_inference(input_file, checkpoint_file, output_dir, multi_chrom, device):
    print(f"Using device: {device}")

    model = ScUnicorn(num_channels=64).to(device)
    checkpoint = torch.load(checkpoint_file, map_location=device)
    model.load_state_dict(checkpoint)  # ✅ Loads ScUnicorn checkpoint correctly
    model.eval()
    print(f"Loaded model from {checkpoint_file}")

    loader, indices = load_data(input_file)
    print(f"Loaded input ScUnicorn data from {input_file}, running inference...")

    result_data, result_inds = [], []

    with torch.no_grad():
        for batch in tqdm(loader, desc="Predicting"):
            lr, inds = batch
            lr = lr.to(device)
            out = model(lr)

            result_data.append(out.cpu().numpy())
            result_inds.append(inds.numpy())

    result_data = np.concatenate(result_data, axis=0)
    result_inds = np.concatenate(result_inds, axis=0)

    matrices = reconstruct_matrix(result_data, result_inds)

    os.makedirs(output_dir, exist_ok=True)
    for chrom, matrix in matrices.items():
        output_file = os.path.join(output_dir, f"chr11_scunicorn.npz")
        np.savez_compressed(output_file, scunicorn=matrix)
        print(f"Saved {output_file}")

    print("Inference complete. All ScUnicorn matrices saved.")


# ==================== Argument Parsing ====================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ScUnicorn inference")
    parser.add_argument("--input", type=str, required=True, help="Path to input Hi-C data (.npz file)")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to trained ScUnicorn checkpoint (.pth file)")
    parser.add_argument("--output", type=str, required=True, help="Directory to save per-chromosome output")
    parser.add_argument("--multi-chrom", action="store_true", help="Enable multi-chromosome processing")
    parser.add_argument("--cuda", type=int, default=-1, help="CUDA device ID (-1 for CPU, 0 for first GPU, etc.)")

    args = parser.parse_args()
    device = torch.device(f"cuda:{args.cuda}" if (torch.cuda.is_available() and args.cuda >= 0) else "cpu")

    run_inference(args.input, args.checkpoint, args.output, args.multi_chrom, device)