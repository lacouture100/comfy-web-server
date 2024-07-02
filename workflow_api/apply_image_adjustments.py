from PIL import ImageEnhance, Image


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
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(contrast)

def adjust_brightness(image, brightness) -> Image:
    """
    Adjust the brightness of an image.
    
    Args:
        image: The image to adjust the brightness of.
        brightness: The brightness value to apply to the image.
        
    Returns:
        Image: The adjusted image.
    """
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(brightness)



