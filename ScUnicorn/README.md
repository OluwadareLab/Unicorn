## 1. Important Notice

Due to GitHub’s file size limitations, the `train.npz`, `valid.npz`, and `test.npz` files could not be uploaded to the repository.  
You can **download them from Zenodo** using the following link:

[Download ScUnicorn Dataset](https://zenodo.org/uploads/15079331?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImRkYzI5MmQwLTdmYWQtNGIwNi04YWIzLWU4ZmViYzMxNmNlOSIsImRhdGEiOnt9LCJyYW5kb20iOiJlMmI0NmNhYjliNWY5ZjA2N2I5ZThkN2EwMDgzODk3ZCJ9.Ql-dXIRmoFgjZXe4Psw3G-mv_uAmM8bqLrfKhNC92PdoLPgCKEIKaRob73gZrYcNV7hW9Bc3XF_pk6ml8fL22A)

You can also download the dataset using `wget`:

```bash
wget https://zenodo.org/uploads/15079331?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImRkYzI5MmQwLTdmYWQtNGIwNi04YWIzLWU4ZmViYzMxNmNlOSIsImRhdGEiOnt9LCJyYW5kb20iOiJlMmI0NmNhYjliNWY5ZjA2N2I5ZThkN2EwMDgzODk3ZCJ9.Ql-dXIRmoFgjZXe4Psw3G-mv_uAmM8bqLrfKhNC92PdoLPgCKEIKaRob73gZrYcNV7hW9Bc3XF_pk6ml8fL22A
```

### 1.0 Navigate to the ScUnicorn Directory

Before proceeding, ensure you are inside the **ScUnicorn** folder:

```bash
cd ScUnicorn
```

### 1.1 Downloading the Dataset
Once downloaded, place the files in the `data/` directory as follows:

```
ScUnicorn/
│
├── data/
│   ├── train.npz    # Training dataset
│   ├── valid.npz    # Validation dataset
│   ├── test.npz     # Testing dataset
│
```

After placing the files correctly, you will get the folder structure as seen below. You can then proceed with the training instructions below.

## 2. Folder Structure
```
ScUnicorn/
│
├── configs/                          # Configuration files
│   ├── default_config.yaml           # Default model and training settings
│
├── models/                           # Model components
│   ├── degradation_kernel.py         # Degradation kernel functions
│   ├── restoration_loop.py           # Iterative restoration module
│   ├── scunicorn.py                  # Main model integration
│
├── output/                           # Output of generate_hr.py will be stored here
│
├── scripts/                          # Execution scripts
│   ├── generate_hr.py                # High-resolution generation script
│   ├── training/                     # Model training scripts
│   │   ├── train.py                  # Training script for ScUnicorn
│   │   ├── infer.py                  # Inference script for trained model
│
├── checkpoint/                       # Model checkpoints
│   ├── scunicorn_model.pytorch       # Saved ScUnicorn model checkpoint
│
├── utils/                            # Utility functions
│   ├── data_loader.py                # Data loading utilities
│   ├── metrics.py                    # Performance evaluation metrics
│   ├── visualization.py              # Visualization tools
│   ├── logger.py                     # Logging functions
│
├── data/                             # Dataset storage
│   ├── train.npz                     # Training dataset
│   ├── valid.npz                     # Validation dataset
│   ├── test.npz                      # Testing dataset
│   ├── mouse_test_data/              # Sample test data
│   │   ├── chr3_100kb.txt
│   │   ├── chr11_100kb.txt
│   │   ├── chr3_500kb.txt
│   │   ├── chr11_500kb.txt
│
├── requirements.txt                   # Python dependencies
├── README.md                          # Project documentation
```

## 3. Training Instructions

To train the ScUnicorn model, navigate to the `scripts/training` directory:
```bash
cd scripts/training
```
run:

```bash
python3 train.py --train_data ../../data/train.npz --valid_data ../../data/valid.npz --epochs 50 --batch_size 64 --lr 0.0003
```

This command will:
- Load training data from `data/train.npz`
- Load validation data from `data/valid.npz`
- Train the model for 50 epochs with a batch size of 64
- Save the trained model in `checkpoint/scunicorn.pth`

## 4. Inference Instructions

To run inference using the trained ScUnicorn model, navigate to the `scripts/training` directory:
```bash
cd scripts/training
```
run:

```bash
python3 infer.py --input ../../data/test.npz --checkpoint ../../checkpoint/scunicorn_model.pytorch --output ../../output/
```

This command will:
- Load the trained model from `checkpoint/scunicorn_model.pytorch`
- Run inference on test data from `data/test.npz`
- Save the output predictions in the `output/` directory

## 5. Generating HR Maps

To generate high-resolution (HR) Hi-C maps using the trained ScUnicorn model, navigate to the `scripts/` directory:
```bash
cd scripts
```
run:

```bash
python3 generate_hr.py --model_path ../checkpoint/scunicorn_model.pytorch --data_path ../data/mouse_test_data/chr3_100kb.txt --output_image_path ../output/output.png --output_hic_path ../output/output.txt
```

This command will:
- Load the trained model from `checkpoint/scunicorn_model.pytorch`
- Use the input Hi-C file `data/mouse_test_data/chr3_100kb.txt`
- Generate an HR Hi-C map and save it as an image in `output/output.png`
- Save the HR Hi-C matrix in `output/output.txt`

## 6. Next Steps

The `output/output.txt` file generated from the **Generating HR Maps** step can be used in the next stage of **3D Unicorn** for **3D reconstruction**.
