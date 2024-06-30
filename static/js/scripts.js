

var contrastSlider = ""
var brightnessSlider = ""
var formData = new FormData();
var selectedFormat = "square";
var imgWidth = 0;
var imgHeight = 0;
var jcp = null
var rect = null
var processedImage = null
var selectedColor;

var isImageUploaded = false;
var isImageProcessed = false;

var parentContainerHeight = 0
var parentContainerWidth = 0
var processedImageWidth = 0
var processedImageHeight = 0
var originalImageWidth = 0
var originalImageHeight = 0
var imageWidthToHeightRatio = 0
var imageHeightToWidthRatio = 0
var finalFrameShort = 2400
var finalFrameLong = 3300
var finalFrameVerticalRatio = 2400 / 3300
var finalFrameHorizontalRatio = 3300 / 2400
var isImageLargerThanFrame = false



window.addEventListener('DOMContentLoaded', function () {
    var fileInput = document.getElementById('file-upload');
    var preview = document.getElementById('image-preview');
    var squareFrame = document.getElementById('square');
    var portraitFrame = document.getElementById('portrait');
    var landscapeFrame = document.getElementById('landscape');

    // Create sliders for contrast and brightness
    contrastSlider = document.getElementById('contrast-slider');
    brightnessSlider = document.getElementById('brightness-slider');

    // Add event listeners to the sliders
    contrastSlider.addEventListener('input', updateImageContrast);
    brightnessSlider.addEventListener('input', updateImageBrightness);

    preview.addEventListener('dragover', function (event) {
        event.preventDefault(); // Prevent default behavior (Prevent file from being opened)
    });


    fileInput.addEventListener('change', function (event) {
        if (fileInput.files && fileInput.files[0]) {
            var reader = new FileReader();
            var inputFile = fileInput.files[0]

            reader.onload = function (e) {
                //console.log(e.target.result)
                preview.innerHTML = '<img src="' + e.target.result + '" alt="Preview" class="image-preview">';
                //preview.style.backgroundColor = "black";
                //preview.style.opacity = "0.8";
                inputFile = e.target.result

                isImageUploaded = true;
                document.querySelector('.image-preview').style.zIndex = '2';
            }

            reader.readAsDataURL(inputFile);
            if (formData.has('image')) {
                formData.delete('image');
            }
            formData.append('image', inputFile);

        }
    });

    preview.addEventListener('drop', function (event) {
        event.preventDefault(); // Prevent default behavior (Prevent file from being opened)
        console.log('File dropped')
        var preview = document.getElementById('image-preview');

        var reader = new FileReader();
        if (event.dataTransfer.files && event.dataTransfer.files[0]) {
            reader.onload = function (e) {
                //console.log(e.target.result)
                preview.innerHTML = '<img src="' + e.target.result + '" alt="Preview" class="image-preview">';
                isImageUploaded = true;
            }
            reader.readAsDataURL(event.dataTransfer.files[0]);

            if (formData.has('image')) {
                formData.delete('image');
            }
            formData.append('image', event.dataTransfer.files[0]);


        }
    });


    const selectElement = document.getElementById('color-dropdown');
    const previewImg = document.getElementById('preview-img');
    const colorPreview = document.getElementById('color-preview');
    // Function to update the preview image based on the selected option
    function updatePreview() {
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        const imgSrc = selectedOption.getAttribute('data-img');

        if (imgSrc) {
            previewImg.src = imgSrc;
            previewImg.style.display = 'block';
        } else {
            previewImg.src = '';
            previewImg.style.display = 'none';
            colorPreview.style.backgroundColor = 'transparent'; // Ensure the block appears without an image
        }
    }

    // Update the preview image when the selection changes
    selectElement.addEventListener('change', updatePreview);

    // Initialize the preview image based on the initially selected option
    updatePreview();

});

// Process the image on the server
function processImage() {

    // Check if an image has been uploaded
    if (!isImageUploaded) {
        alert("Please upload an image first!");
        return;
    }
    let imageContainer = document.getElementById('image-container');

    // Check if the image container is empty, if not delete content forr new image to appear
    if (imageContainer.innerHTML != '') {
        imageContainer.innerHTML = '';
    }
    // Show the loading spinner
    document.getElementById('loading').hidden = false;

    // Get the selected background color
    selectedColor = document.getElementById("color-dropdown").value || "none";

    // Append the selected background color to the form data sent to server for processing
    formData.append("background_color", selectedColor);

    // Send the image to the server for processing
    fetch('http://ue2.thingmade.com/process', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })   // Assuming the response contains the image URL
        .then(data => {
            // Extract the image URL from the response
            //const imageUrl = `{{ url_for('static', filename='') }}${data.image_url}`;
            const imageUrl = `static/${data.image_url}`;
            console.log('Image URL:', imageUrl);



            // Check if the img element exists; if not, create it
            let img = document.getElementById('processed-image');
            if (!img) {
                img = document.createElement('img');
                img.id = 'processed-image';
                img.alt = 'Processed Image';  // Optional alt text
                img.style.filter = 'contrast(100%) brightness(1.0)';  // Apply contrast and brightness filters


                // Get the image dimensions
                img.addEventListener('load', function () {
                    originalImageWidth = img.naturalWidth;
                    originalImageHeight = img.naturalHeight;

                    imageWidthToHeightRatio = originalImageWidth / originalImageHeight;
                    imageHeightToWidthRatio = originalImageHeight / originalImageWidth;
                    img.style.width = '100%';
                    img.style.maxHeight = '100%';  

                    imageContainer.appendChild(img);
                    isImageProcessed = true;
                    //Load the image crop module after the image is loaded

                });

            }

            // Set the source of the img element to the new image URL
            img.src = imageUrl;
            document.getElementById('loading').hidden = true;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}


// Function to update the image contrast
function updateImageContrast() {
    var contrastValue = contrastSlider.value;
    console.log('Contrast value:', contrastValue);

    var processedImage = document.getElementById('processed-image');
    processedImage.style.filter = `contrast(${contrastValue}%)`;
}

// Function to update the image brightness
function updateImageBrightness() {
    var brightnessValue = brightnessSlider.value;
    console.log('Brightness value:', brightnessValue);

    var processedImage = document.getElementById('processed-image');
    processedImage.style.filter = `brightness(${brightnessValue}%)`;
}




// Upscale the image
function upscaleImage() {

    if (!isImageUploaded) {
        alert("Please upload an image first!");
        return;
    }

    if (!isImageProcessed ) {
        alert("Please upload an image, then click on transform!");
        return;
    }
    console.log("---------------- Upscale image function called -----------------");

    document.getElementById('loading').hidden = false;
    var contrast = document.getElementById('contrast-slider').value;
    var brightness = document.getElementById('brightness-slider').value;


    finalImageSettings.originalImageHeight = originalImageHeight;
    finalImageSettings.originalImageWidth = originalImageWidth;
    finalImageSettings.parentContainerHeight = parentContainerHeight;
    finalImageSettings.parentContainerWidth = parentContainerWidth;
    finalImageSettings.imageCropX1 = jcp.active.pos.x;
    finalImageSettings.imageCropY1 = jcp.active.pos.y;
    finalImageSettings.imageCropY2 = jcp.active.pos.h;
    finalImageSettings.imageCropX2 = jcp.active.pos.w;
    finalImageSettings.format = selectedFormat;
    finalImageSettings.brightness = brightness;
    finalImageSettings.contrast = contrast;

    var processedImage = document.getElementById('processed-image');
    var imageSrc = processedImage.src;

    // Create a new FormData object to send the image and other data to the server
    var formData = new FormData();

    fetch(imageSrc)
        .then(response => response.blob())
        .then(blob => {

            //create the image file
            const file = new File([blob], "image.jpg", { type: "image/jpeg" });
            formData.append('image', file);
            
            formData.append("contrast", contrast);
            formData.append("brightness", brightness);
            formData.append("format", selectedFormat);
            formData.append("original_image_height", originalImageHeight);
            formData.append("original_image_width", originalImageWidth);
            formData.append("parent_container_height", parentContainerHeight);
            formData.append("parent_container_width", parentContainerWidth);
            formData.append("image_crop_x1", jcp.active.pos.x);
            formData.append("image_crop_x2", jcp.active.pos.w);
            formData.append("image_crop_y1", jcp.active.pos.y);
            formData.append("image_crop_y2", jcp.active.pos.h);
            formData.append("processed_image_height", processedImageHeight);
            formData.append("processed_image_width", processedImageWidth);

            for (var pair of formData.entries()) {
                console.log(pair[0] + ', ' + pair[1]);
            }


            console.log("Final image settings:", finalImageSettings);

            return fetch('http://10.65.168.99:5000/upscale', {
                method: 'POST',
                body: formData
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .catch(error => console.error('Error:', error))
        .then(data => {
            console.log(data)
            const imageUrl = `static/${data.image_url}`;
            console.log("Upscaled image URL : " + imageUrl)

            finalImageSettings.downloadUrl = imageUrl;
            //Create the download link
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = imageUrl;
            a.download = 'edited-image.png';
            document.body.appendChild(a);
            a.click();

        })
        
        .then(document.getElementById('loading').hidden = true);

}


function back() {
    window.location.reload();
}
