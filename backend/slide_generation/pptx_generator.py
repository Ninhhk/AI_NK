import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class PowerPointGenerator:
    def __init__(self):
        self.prs = Presentation()

    def generate_presentation(self, slides_data: list, output_path: Path) -> str:
        """Generate a PowerPoint presentation from the slides data.
        
        Args:
            slides_data: List of slide dictionaries with title_text and text fields
            output_path: Path where to save the presentation
            
        Returns:
            Path to the generated presentation
        """
        try:
            # Create a new Presentation object for each generation
            self.prs = Presentation()
            
            # Add title slide
            title_slide = slides_data[0]
            if title_slide.get("is_title_slide") == "yes":
                self.add_title_slide(title_slide["title_text"])
            else:
                self.add_title_slide(title_slide["title_text"])

            # Add content slides
            for slide_data in slides_data[1:]:
                self.add_content_slide(slide_data)

            # Ensure the output path exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the presentation with proper encoding
            self.prs.save(str(output_path))
            logger.info(f"Successfully saved presentation to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating PowerPoint presentation: {str(e)}")
            raise

    def add_title_slide(self, title: str):
        """Add a title slide to the presentation."""
        try:
            title_slide_layout = self.prs.slide_layouts[0]
            slide = self.prs.slides.add_slide(title_slide_layout)
            title_shape = slide.shapes.title
            title_shape.text = title
        except Exception as e:
            logger.error(f"Error adding title slide: {str(e)}")
            raise

    def add_content_slide(self, slide_data: dict):
        """Add a content slide to the presentation."""
        try:
            bullet_slide_layout = self.prs.slide_layouts[1]
            slide = self.prs.slides.add_slide(bullet_slide_layout)
            shapes = slide.shapes

            # Title
            title_shape = shapes.title
            title_shape.text = slide_data["title_text"]

            # Body
            if "text" in slide_data and slide_data["text"]:
                body_shape = shapes.placeholders[1]
                tf = body_shape.text_frame
                tf.clear()  # Clear any existing text
                
                # Process text content
                text_content = slide_data["text"].strip()
                if text_content:
                    # Split into lines and process each line once
                    lines = [line.strip() for line in text_content.split("\n") if line.strip()]
                    first_line = True
                    
                    for line in lines:
                        # Remove any existing bullet points at the start of the line
                        line = line.lstrip('•').lstrip('*').lstrip('-').strip()
                        
                        # Calculate indentation level from the original text
                        original_line = line
                        indent_level = 0
                        while original_line.startswith('  '):  # Count pairs of spaces for indentation
                            indent_level += 1
                            original_line = original_line[2:]
                        
                        # Add paragraph with proper encoding
                        if first_line:
                            p = tf.paragraphs[0]  # Use existing first paragraph
                            first_line = False
                        else:
                            p = tf.add_paragraph()
                        
                        p.text = line
                        p.level = min(indent_level, 4)  # Cap at 4 levels of indentation

            # Add images if present
            if "images" in slide_data:
                cur_left = 6
                for img_path in slide_data.get("images", []):
                    if os.path.exists(img_path):
                        top = Inches(2)
                        left = Inches(cur_left)
                        height = Inches(4)
                        slide.shapes.add_picture(img_path, left, top, height=height)
                        cur_left += 1
                        
        except Exception as e:
            logger.error(f"Error adding content slide: {str(e)}")
            raise 