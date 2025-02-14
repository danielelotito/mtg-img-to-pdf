# Image to PDF Processor

A Python application that processes multiple image folders and creates a formatted PDF document with validated images arranged in rows. Useful to print custom proxies for popular card-games with cards of size 2.5 x 3.5 inches, or 6.35 x 8.89cm.

The application checks image dimensions and DPI specifications before including them in the output PDF.

## Features

- Scans multiple input folders for images (JPG and PNG)
- Validates image dimensions and DPI according to specifications
- Creates A4-sized PDF with configurable image layout
- Comprehensive logging of processing steps and warnings
- Hydra-based configuration management
- Maintains image aspect ratios in PDF output
- Support for Magic: The Gathering card dimensions (63.5mm × 88.9mm)

## Requirements

- Python 3.10 or higher
- Dependencies listed in `requirements.txt`:
  - hydra-core >= 1.3.2
  - Pillow >= 10.0.0
  - reportlab >= 4.0.4
  - omegaconf >= 2.3.0
  - PyYAML >= 6.0.1

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd image-processor
```

2. Create and activate a conda environment:

```bash
conda create -n image_processor python=3.10
conda activate image_processor
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

## Configuration

The application uses Hydra for configuration management. Main configuration options are in `config/config.yaml`:

### Image Specifications

```yaml
image_specs:
  check_valid_dimensions: true 
  check_dpi: true 
  valid_dimensions:
    - [744, 1045]  # width x height
    - [744, 1039]
    - [1500, 2100]
  valid_dpis: [72, 96]
```

### PDF Output Settings

```yaml
pdf_output:
  page_size: A4
  images_per_row: 3
  margin: 20  # mm
  spacing: -0.15  # mm between images
```

### Input/Output Paths

```yaml
folders:
  input_paths:
    - ./img/finished
  supported_extensions: [".jpg", ".jpeg", ".png"]
```

## Usage

1. Update the configuration file with your input folders:

   - Open `config/config.yaml`
   - Modify the `input_paths` list with your image folder paths
2. Run the application:

```bash
python image_processor.py
```

The processed PDF will be created in the `outputs/YYYY-MM-DD/HH-MM-SS` directory with timestamped folders.

## Project Structure

```
image-processor/
├── config/
│   └── config.yaml
├── image_processor.py
├── requirements.txt
├── README.md
└── outputs/
    └── YYYY-MM-DD/
        ├── HH-MM-SS/
        │   ├── output.pdf
        │   └── process.log
```

## Output

- The application creates a timestamped output directory for each run
- Each run directory contains:
  - `output.pdf`: The generated PDF with processed images
  - `process.log`: Detailed processing log including warnings and errors

## Logging

The application logs various events:

- INFO: General processing information and success messages
- WARNING: Issues with image dimensions or DPI
- ERROR: Processing failures or critical issues

Example log output:

```
INFO: Total images processed: 25
INFO: Valid images found: 20
INFO: Invalid images:
 - image.jpg: Invalid dimensions 800x600
 - photo.png: Invalid DPI 150
INFO: PDF created successfully at /path/to/output.pdf
```

## Image Validation

The application validates images based on:

1. Dimensions: Must match one of the configured valid dimensions
2. DPI: Must match one of the configured valid DPI values
3. File format: Must be JPG or PNG

Invalid images are logged with warnings and excluded from the PDF.

## Card Layout

- Images are arranged in a grid layout on A4 pages
- Each page contains up to 9 images (3 rows × 3 columns)
- Card dimensions are fixed at 63.5mm × 88.9mm (standard MTG card size)
- Configurable margins and spacing between cards
- Aspect ratio is preserved during PDF generation

## Customization

You can modify various aspects of the processing:

- Change valid dimensions in `config.yaml`
- Adjust PDF layout parameters
- Add support for additional image formats
- Modify logging levels and output format
- Configure card spacing and margins

## Error Handling

The application includes robust error handling:

- Invalid image files are skipped with appropriate warnings
- Missing input folders are reported
- PDF creation errors are caught and logged
- Invalid configurations are detected and reported
- DPI validation errors are gracefully handled

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
