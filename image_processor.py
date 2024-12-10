import os
import logging
from pathlib import Path
from typing import List, Tuple
from PIL import Image
from reportlab.lib import pagesizes
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import hydra
from omegaconf import DictConfig
from hydra.core.hydra_config import HydraConfig
from hydra.utils import get_original_cwd

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.valid_dimensions = cfg.image_specs.valid_dimensions
        self.valid_dpis = cfg.image_specs.valid_dpis
        self.supported_extensions = cfg.folders.supported_extensions
        self.original_cwd = get_original_cwd()
        
        # MTG card dimensions in mm
        self.CARD_WIDTH = 63.5 * mm  # 6.35 cm = 63.5 mm
        self.CARD_HEIGHT = 88.9 * mm # 8.89 cm = 88.9 mm
        
    def _get_absolute_path(self, path: str) -> Path:
        p = Path(path)
        return p if p.is_absolute() else Path(self.original_cwd) / p

    def validate_image(self, image_path: Path) -> Tuple[bool, Image.Image, str]:
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                
                valid_dim = False
                for valid_w, valid_h in self.valid_dimensions:
                    if width == valid_w and height == valid_h:
                        valid_dim = True
                        break
                
                if not valid_dim:
                    return False, None, f"Invalid dimensions {width}x{height}"
                
                try:
                    dpi = img.info.get('dpi', (None, None))[0]
                    if dpi not in self.valid_dpis:
                        return False, None, f"Invalid DPI {dpi}"
                except Exception as e:
                    # Just proceed if DPI can't be read
                    pass
                
                return True, img, "Valid"
                
        except Exception as e:
            return False, None, f"Error processing image: {str(e)}"

    def collect_valid_images(self) -> List[Path]:
        valid_images = []
        total_images = 0
        invalid_images = []
        
        for folder_path in self.cfg.folders.input_paths:
            folder = self._get_absolute_path(folder_path)
            if not folder.exists():
                logger.error(f"Folder not found: {folder}")
                continue
            
            for file in folder.iterdir():
                if file.suffix.lower() in self.supported_extensions:
                    total_images += 1
                    is_valid, _, reason = self.validate_image(file)
                    if is_valid:
                        valid_images.append(file)
                    else:
                        invalid_images.append((file, reason))
        
        logger.info(f"Total images processed: {total_images}")
        logger.info(f"Valid images found: {len(valid_images)}")
        if invalid_images:
            logger.info("Invalid images:")
            for img, reason in invalid_images:
                logger.info(f" - {img.name}: {reason}")
        
        return valid_images

    def create_pdf(self, valid_images: List[Path]):
        if not valid_images:
            logger.warning("No valid images found. PDF will not be created.")
            return
            
        output_path = Path(HydraConfig.get().run.dir) / "output.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        c = canvas.Canvas(str(output_path), pagesize=pagesizes.A4)
        page_width, page_height = pagesizes.A4
        
        margin = self.cfg.pdf_output.margin * mm  # Convert mm to points
        spacing = self.cfg.pdf_output.spacing * mm  # Convert mm to points
        images_per_row = self.cfg.pdf_output.images_per_row
        rows_per_page = 3
        
        current_image = 0
        total_images = len(valid_images)
        
        while current_image < total_images:
            # Start new page
            y = page_height - margin - self.CARD_HEIGHT  # Start from top of page
            
            # Process three rows
            for row in range(rows_per_page):
                x = margin
                
                # Process images in current row
                for col in range(images_per_row):
                    if current_image < total_images:
                        c.drawImage(
                            str(valid_images[current_image]),
                            x,
                            y,
                            width=self.CARD_WIDTH,
                            height=self.CARD_HEIGHT,
                            preserveAspectRatio=True
                        )
                        x += self.CARD_WIDTH + spacing  # Move right by card width plus spacing
                        current_image += 1
                
                # Move to next row if there are more images
                if current_image < total_images and row < rows_per_page - 1:
                    y -= (self.CARD_HEIGHT + spacing)  # Move down by card height plus spacing
            
            # Add new page if there are more images
            if current_image < total_images:
                c.showPage()
        
        c.save()
        logger.info(f"PDF created successfully at {output_path}")

@hydra.main(config_path="config", config_name="config")
def main(cfg: DictConfig):
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    processor = ImageProcessor(cfg)
    valid_images = processor.collect_valid_images()
    
    if valid_images:
        processor.create_pdf(valid_images)
    else:
        logger.error("No valid images found. Process terminated.")

if __name__ == "__main__":
    main()
