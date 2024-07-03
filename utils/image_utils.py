from PIL import ImageEnhance, Image, ImageStat
import logging


def crop_image(image, x, y, width, height) -> Image:
    """
    Crop an image based on the specified coordinates and dimensions.
    
    Args:
        image: The image to be cropped.
        x: The x-coordinate of the top-left corner of the crop rectangle.
        y: The y-coordinate of the top-left corner of the crop rectangle.
        width: The width of the crop rectangle.
        height: The height of the crop rectangle.
        
    Returns:
        Image: The cropped image.
    """
    logging.info("Cropping image...")
    width= int(width)
    height = int(height)
    x = int(x)
    y = int(y)
    logging.info(f"Cropping image with bounds: x={x}, y={y}, width={width}, height={height}")
    if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > image.width or y + height > image.height:
        raise ValueError("Invalid cropping dimensions")
    return image.crop((x, y, x + width, y + height))

def adjust_contrast(image, contrast) -> Image:
    """
    Adjust the contrast of an image.
    
    Args:
        image: The image to adjust the contrast of.
        contrast: The contrast value to apply to the image.
        
    Returns:
        Image: The adjusted image.
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid image for contrast adjustment")
    
    logging.info("Adjusting contrast...")
    logging.info(f"Contrast value: {contrast}")

    try:
        enhancer = ImageEnhance.Contrast(image)
        adjusted_image = enhancer.enhance(contrast)
        return adjusted_image
    except Exception as e:
        logging.error(f"Error adjusting contrast: {e}")
        raise RuntimeError("Failed to adjust contrast") from e


def adjust_brightness(image, brightness) -> Image:
    """
    Adjust the brightness of an image.
    
    Args:
        image: The image to adjust the brightness of.
        brightness: The brightness value to apply to the image.
        
    Returns:
        Image: The adjusted image.
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid image for brightness adjustment")
    
    logging.info("Adjusting brightness...")
    logging.info(f"Brightness value: {brightness}")

    try:
        enhancer = ImageEnhance.Brightness(image)
        adjusted_image = enhancer.enhance(brightness)
        return adjusted_image
    except Exception as e:
        logging.error(f"Error adjusting brightness: {e}")
        raise RuntimeError("Failed to adjust brightness") from e

