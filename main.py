from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import streamlit as st
import requests


# Load model and processor
processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
m = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')


# Function to load image from computer
def load_image_from_file(file):
    image = Image.open(file)
    return image


# Function to load image from URL
def load_image_from_url(url):
    image = Image.open(requests.get(url, stream=True).raw)
    return image


# Function to classify image
def classify_image(image, model, processor):
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_idx = logits.argmax(-1).item()
    return model.config.id2label[predicted_class_idx]


def main():
    st.set_page_config(layout="wide")
    st.title("Simple image classification app")
    st.subheader("vit-base-patch16-224")

    col1, col2 = st.columns([2, 3])
    image = None

    # Left column: Buttons, upload fields, and Predict Class button
    with col1:
        uploaded_file = st.file_uploader("Choose an image:",
                                         type=["jpg", "jpeg", "png"])
        url = st.text_input("...or enter image URL:")
        if uploaded_file:
            image = load_image_from_file(uploaded_file)
        elif url:
            try:
                image = load_image_from_url(url)
            except requests.exceptions.RequestException as e:
                st.warning(f"Error loading image from URL: {e}")
                return
        else:
            st.warning("Please upload an image or provide an image URL.")
            return

        if st.button("Classify image") and image:
            predicted_class = classify_image(image, m, processor)
            st.success(f"Image class: {predicted_class}")

    # Right column: Display the uploaded image
    with col2:
        if image:
            aspect_ratio = image.width / image.height
            use_column_width = aspect_ratio > 1.4

            if uploaded_file:
                st.image(image, caption="Uploaded image",
                         use_column_width=use_column_width)
            elif url:
                try:
                    st.image(image, caption="Image from URL",
                             use_column_width=use_column_width)
                except Exception as e:
                    st.warning(f"Error loading image from URL: {e}")


if __name__ == "__main__":
    main()
