# Certificate Forgery Detection System

A comprehensive system to verify academic certificates using OCR, Blockchain, and AI.

## Project Overview
This project validates academic records by:
1.  Extracting text from certificate images using OCR.
2.   verifying data integrity via Blockchain.
3.  Detecting potential forgery attempts using a trained AI model.

## Model File
**The trained model is not included in this repository due to GitHub file size limits.**

### Option 1: Download Pre-trained Model
*   The model file (`certificate_forgery_model.h5`) should be placed in `ai/model/`.
*   [Download Link Placeholder]

### Option 2: Train the Model Locally
You can generate the model by running the training script:

```bash
cd ai
python train_model.py
```

## Setup & usage
See `requirements.txt` for dependencies.
Use `start_project.bat` to launch the full system.
## Model File

The trained certificate forgery detection model is not included in this repository due to GitHub file size limitations.

### Download Model
Download the model from: <Google Drive / HuggingFace link>

Place it inside:
ai/model/certificate_forgery_model.h5

### Train Locally
```bash
python train.py
