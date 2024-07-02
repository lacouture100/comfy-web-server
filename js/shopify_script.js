document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    initSliders();
    initColorPreview();
});

var formData = new FormData();

const config = {
    selectedFormat: "square",
    selectedColor: null,
    isImageUploaded: false,
    isImageProcessed: false,
    dimensions: {
        imgWidth: 0,
        imgHeight: 0,
    },
    frameSizes: {
        finalFrameVerticalRatio: 2400 / 3300,
        finalFrameHorizontalRatio: 3300 / 2400
    },
    cropX: 0,
    cropY: 0,
    cropWidth: 0,
    cropHeight: 0
};

const elements = {
    fileInput: document.getElementById('file-upload'),
    preview: document.getElementById('image-preview'),
    frames: {
        square: document.getElementById('square'),
        portrait: document.getElementById('portrait'),
        landscape: document.getElementById('landscape')
    },
    sliders: {
        contrast: document.getElementById('contrast-slider'),
        brightness: document.getElementById('brightness-slider')
    },
    colorDropdown: document.getElementById('color-dropdown'),
    colorPreviewImg: document.getElementById('color-preview-img'),
    colorPreview: document.getElementById('color-preview'),
    loadingSpinner: document.getElementById('loading'),
    imageContainer: document.getElementById('processed-image-container'),
    upscaleImageUrl: document.getElementById('upscale-image-url'),
    productMedia: document.getElementById('product__media'),
    cropFrame: null

};

const initEventListeners = () => {
    elements.fileInput.addEventListener('change', (event) => handleFileInput(event, elements.fileInput));
    elements.preview.addEventListener('dragover', (event) => event.preventDefault());
    elements.preview.addEventListener('drop', (event) => handleFileDrop(event));
    elements.frames.square.addEventListener('click', () => handleFormatSelection('square'));
    elements.frames.portrait.addEventListener('click', () => handleFormatSelection('portrait'));
    elements.frames.landscape.addEventListener('click', () => handleFormatSelection('landscape'));
};

const initSliders = () => {
    elements.sliders.contrast.addEventListener('input', () => updateImageStyle('contrast', elements.sliders.contrast.value));
    elements.sliders.brightness.addEventListener('input', () => updateImageStyle('brightness', elements.sliders.brightness.value));
};

const initColorPreview = () => {
    elements.colorDropdown.addEventListener('change', updateColorPreview);
    updateColorPreview();
};

const updateImageStyle = (property, value) => {
    const processedImage = document.getElementById('processed-image');
    const currentFilter = processedImage.style.filter;
    const regex = new RegExp(`${property}\\(([^)]+)\\)`, 'i');
    const newFilter = currentFilter.match(regex) ? currentFilter.replace(regex, `${property}(${value}%)`) : `${currentFilter} ${property}(${value}%)`;
    processedImage.style.filter = newFilter.trim();
};

const handleFileInput = (event, fileInput) => {
    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => {
            elements.preview.innerHTML = `<img src="${e.target.result}" alt="Preview" class="image-preview">`;
            config.isImageUploaded = true;
            document.querySelector('.image-preview').style.zIndex = '2';
        };
        reader.readAsDataURL(fileInput.files[0]);
        updateFormData('image', fileInput.files[0]);
    }
};

const handleFileDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
        elements.preview.innerHTML = `<img src="${e.target.result}" alt="Preview" class="image-preview">`;
        config.isImageUploaded = true;
    };
    reader.readAsDataURL(file);
    updateFormData('image', file);
};

const handleFormatSelection = (format) => {
    config.selectedFormat = format;
    if (config.isImageProcessed) {
        showCropFrame();
    }
};

const updateColorPreview = () => {
    const selectedOption = elements.colorDropdown.options[elements.colorDropdown.selectedIndex];
    const imgSrc = selectedOption.getAttribute('data-img');
    elements.colorPreviewImg.src = imgSrc;
    elements.colorPreviewImg.style.display = 'block';
};

const updateFormData = (key, value) => {

    if (formData.has(key)) {
        formData.delete(key);
    }
    console.log(formData);
    formData.append(key, value);
};

const processImage = () => {
    if (!config.isImageUploaded) {
        alert("Please upload an image first!");
        return;
    }
    clearImageContainer();
    elements.loadingSpinner.hidden = false;
    config.selectedColor = elements.colorDropdown.value || "none";
    updateFormData("background_color", config.selectedColor);

    fetch('https://ue2.thingmade.com/process', {
        method: 'POST',
        body: formData
    })
    .then(handleResponse)
    .then(handleProcessedImage)
    .catch(handleError);
    
};

const handleResponse = (response) => {
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
};

const handleProcessedImage = (data) => {
    const imageUrl = `https://ue2.thingmade.com/static/${data.image_url}`;
    let img = document.getElementById('processed-image') || document.createElement('img');
    img.id = 'processed-image';
    img.alt = 'Processed Image';
    img.style.filter = 'contrast(100%) brightness(1.0)';
    img.src = imageUrl;
    img.addEventListener('load', () => {
        updateImageDimensions(img);
        elements.imageContainer.appendChild(img);
        config.isImageProcessed = true;
        showCropFrame();
    });
    elements.loadingSpinner.hidden = true;
};

const handleError = (error) => {
    console.error('Error:', error);
    elements.loadingSpinner.hidden = true;
};

const clearImageContainer = () => {
    elements.imageContainer.innerHTML = '';
};

const updateImageDimensions = (img) => {
    config.dimensions.originalImageWidth = img.naturalWidth;
    config.dimensions.originalImageHeight = img.naturalHeight;
    config.dimensions.imageWidthToHeightRatio = config.dimensions.originalImageWidth / config.dimensions.originalImageHeight;
    config.dimensions.imageHeightToWidthRatio = config.dimensions.originalImageHeight / config.dimensions.originalImageWidth;
    img.style.width = '100%';
    img.style.maxHeight = '100%';
};

const upscaleImage = () => {
    if (!config.isImageUploaded) {
        alert("Please upload an image first!");
        return;
    }
    if (!config.isImageProcessed) {
        alert("Please upload an image, then click on transform!");
        return;
    }

    elements.loadingSpinner.hidden = false;

    const contrast = elements.sliders.contrast.value;
    const brightness = elements.sliders.brightness.value;
    const processedImage = document.getElementById('processed-image');
    const imageSrc = processedImage.src;

    fetch(imageSrc)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(blob => createImageFile(blob))
        .then(file => createUpscaleFormData(file, contrast, brightness))
        .then(sendUpscaleRequest)
        .then(handleUpscaleResponse)
        .catch(handleError);
};

const createImageFile = (blob) => {
    return new File([blob], "image.jpg", { type: "image/jpeg" });
};

const createUpscaleFormData = (file, contrast, brightness) => {

    const processedImage = document.getElementById('processed-image');
    const naturalWidth = processedImage.naturalWidth;
    const naturalHeight = processedImage.naturalHeight;
    const currentWidth = processedImage.clientWidth;
    const currentHeight = processedImage.clientHeight;

    console.log('Natural Dimensions:', naturalWidth, naturalHeight);
    console.log('Current Dimensions:', currentWidth, currentHeight);

    const cropRect = elements.cropFrame.getBoundingClientRect();
    const imgRect = processedImage.getBoundingClientRect();
    const scaleX = config.dimensions.originalImageWidth / imgRect.width;
    const scaleY = config.dimensions.originalImageHeight / imgRect.height;

    config.cropX = (cropRect.left - imgRect.left) * scaleX;
    config.cropY = (cropRect.top - imgRect.top) * scaleY;
    config.cropWidth = cropRect.width * scaleX;
    config.cropHeight = cropRect.height * scaleY;

    console.log(config.cropX, config.cropY, config.cropWidth, config.cropHeight);
    const upscaleFormData = new FormData();
    upscaleFormData.append('image', file);
    upscaleFormData.append("contrast", contrast);
    upscaleFormData.append("brightness", brightness);
    upscaleFormData.append("format", config.selectedFormat);
    upscaleFormData.append("crop_x", config.cropX);
    upscaleFormData.append("crop_y", config.cropY);
    upscaleFormData.append("crop_width", config.cropWidth);
    upscaleFormData.append("crop_height", config.cropHeight);

    return upscaleFormData;
};

const sendUpscaleRequest = (upscaleFormData) => {
    return fetch('https://ue2.thingmade.com/upscale', {
        method: 'POST',
        body: upscaleFormData
    }).then(handleResponse);
};

const handleUpscaleResponse = (data) => {
    const imageUrl = `https://ue2.thingmade.com/static/${data.image_url}`;
    let img = document.createElement('img');
    img.id = 'cropped-processed-image';
    img.alt = 'Cropped Processed Image';
    img.src = imageUrl;
    img.style.width = '30%';
    img.style.height = '30%';
    img.style.margin = "auto";
    img.style.display = "block";
    img.style.top = "0";
    img.style.left = "0";
    img.style.bottom = "0";
    img.style.right = "0";



    elements.productMedia.appendChild(img);
    elements.upscaleImageUrl.value = imageUrl;
    elements.loadingSpinner.hidden = true;
};

const showCropFrame = () => {
    if (elements.cropFrame) {
        elements.cropFrame.remove();
    }

    elements.cropFrame = document.createElement('div');
    elements.cropFrame.id = 'crop-frame';
    elements.cropFrame.style.position = 'absolute';
    elements.cropFrame.style.border = '2px dashed #fff';
    elements.cropFrame.style.background = 'rgba(0, 0, 0, 0.5)';

    const imgContainer = elements.imageContainer;
    const img = document.getElementById('processed-image');
    const imgWidth = img.clientWidth;
    const imgHeight = img.clientHeight; 

    let frameWidth, frameHeight;

    if (config.selectedFormat === 'square') {
        const size = Math.min(imgWidth, imgHeight);
        frameWidth = frameHeight = size;
    } else if (config.selectedFormat === 'landscape') {
        frameWidth = Math.min(imgWidth, imgHeight * config.frameSizes.finalFrameHorizontalRatio);
        frameHeight = frameWidth / config.frameSizes.finalFrameHorizontalRatio;
    } else if (config.selectedFormat === 'portrait') {
        frameHeight = Math.min(imgHeight, imgWidth * config.frameSizes.finalFrameVerticalRatio);
        frameWidth = frameHeight / config.frameSizes.finalFrameVerticalRatio;
    }
    console.log(frameWidth, frameHeight);


    elements.cropFrame.style.width = `${frameWidth}px`;
    elements.cropFrame.style.height = `${frameHeight}px`;
    elements.cropFrame.style.top = `${(imgHeight - frameHeight) / 2}px`;
    elements.cropFrame.style.left = `${(imgWidth - frameWidth) / 2}px`;

    imgContainer.appendChild(elements.cropFrame);

    makeDraggable(elements.cropFrame, imgContainer);
};


const makeDraggable = (element, container) => {
    let offsetX, offsetY;

    element.addEventListener('mousedown', (e) => {
        offsetX = e.clientX - element.getBoundingClientRect().left;
        offsetY = e.clientY - element.getBoundingClientRect().top;
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    });

    const onMouseMove = (e) => {
        const containerRect = container.getBoundingClientRect();
        const elementRect = element.getBoundingClientRect();

        let newLeft = e.clientX - containerRect.left - offsetX;
        let newTop = e.clientY - containerRect.top - offsetY;

        newLeft = Math.max(0, Math.min(newLeft, containerRect.width - elementRect.width));
        newTop = Math.max(0, Math.min(newTop, containerRect.height - elementRect.height));

        element.style.left = `${newLeft}px`;
        element.style.top = `${newTop}px`;
    };

    const onMouseUp = () => {
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
    };
};