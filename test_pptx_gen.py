from backend.slide_generation.pptx_generator import PowerPointGenerator
from pathlib import Path
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        # Path to your JSON file
        file_path = Path('output/slides/intro_ai_20250509_221657.json')
        logger.info(f"Using JSON file: {file_path}")
        
        # Output path for the PowerPoint
        output_path = Path('output/slides/intro_ai_test.pptx')
        logger.info(f"Output will be saved to: {output_path}")
        
        # Load the JSON data
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded JSON data: {len(data['slides'])} slides")
        logger.debug(f"JSON content: {json.dumps(data, indent=2)}")
        
        # Create PowerPoint generator and generate presentation
        generator = PowerPointGenerator()
        logger.info("PowerPoint generator created")
        
        result_path = generator.generate_presentation(data['slides'], output_path)
        logger.info(f"PowerPoint generated successfully at: {result_path}")
        
        print(f'Generated {output_path}')
    except Exception as e:
        logger.exception(f"Error generating PowerPoint: {e}")
        raise

if __name__ == "__main__":
    main()
