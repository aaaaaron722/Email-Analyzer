# Email-Analyzer
![img](icons/icon512.png)
### Description

Email Analyzer is a Python-based tool that leverages AI models to automatically analyze and generate email content. The tool uses the facebook/bart-large-cnn model to summarize and process large email bodies, making it easier to quickly understand key points or automatically generate replies.

### Features
- Load and utilize the facebook/bart-large-cnn AI model for natural language processing.
- Automatically generate email summaries.
- Supports GPU (if available) to accelerate processing.
- Easily customizable for different AI models or processing tasks.

### Prerequisites
- Python 3.7 or higher
- CUDA-compatible GPU (optional but recommended for faster performance)
- Internet connection for downloading the pre-trained model (first-time setup)


### Installation
1. Clone the repository:

```bash
git clone https://github.com/yourusername/email-analyzer.git
cd email-analyzer
```


2. Install the required dependencies:

```bash
pip install -r requirements.txt
```


### Folder Structure
    .
    ├── model_cache/          # Directory for storing cached models
    ├── email_analyzer.py     # Main class for email analysis
    ├── requirements.txt      # Required Python dependencies
    └── README.md             # Project documentation

### Dependencies
The project relies on the following Python libraries:

- transformers – For loading and using the pre-trained BART model.
- torch – For running AI models on both CPU and GPU.
- pathlib – For handling directory creation and model caching.
- logging – For recording logs during model loading and email generation.

### Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue if you find any bugs or want to add features.

### Limitation
Cuz the model was trained by google, And the input data usually in English. So there is a problem that is this application may not read the email content in Mandarin. 
Also the suggested reply still have some problem. I am trying to figure out.