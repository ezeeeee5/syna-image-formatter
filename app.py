
import streamlit as st
from PIL import Image, ImageDraw
import io
import zipfile
import os

st.title("Syna Image Formatter")
st.markdown("Sube las imágenes de producto que quieras estandarizar. La imagen base ya está configurada.")

# Cargar múltiples imágenes de producto
product_files = st.file_uploader("Imágenes de producto", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

# Cargar imagen base predefinida (del sistema)
BASE_IMAGE_PATH = "base_image.png"
base_img = Image.open(BASE_IMAGE_PATH).convert("RGBA")
margin_ratio = 0.05

def process_image(base_img, product_img):
    canvas_size = base_img.size

    # Eliminar sujeto de la imagen base (rellenar fondo blanco)
    base_clear = base_img.copy()
    draw = ImageDraw.Draw(base_clear)
    bbox = base_clear.getbbox()
    draw.rectangle(bbox, fill="white")

    # Recortar y escalar sujeto proporcionalmente
    product_img = product_img.convert("RGBA")
    subject_bbox = product_img.getbbox()
    cropped = product_img.crop(subject_bbox)

    usable_width = int(canvas_size[0] * (1 - 2 * margin_ratio))
    usable_height = int(canvas_size[1] * (1 - 2 * margin_ratio))
    scale_factor = min(usable_width / cropped.width, usable_height / cropped.height)
    new_size = (int(cropped.width * scale_factor), int(cropped.height * scale_factor))
    resized = cropped.resize(new_size, Image.LANCZOS)

    # Pegar centrado sobre fondo base limpio
    final_img = base_clear.copy()
    offset = ((canvas_size[0] - new_size[0]) // 2, (canvas_size[1] - new_size[1]) // 2)
    final_img.paste(resized, offset, resized)

    # Comprimir a 200–300 KB como PNG
    for compress_level in range(9, -1, -1):
        buffer = io.BytesIO()
        final_img.save(buffer, format="PNG", optimize=True, compress_level=compress_level)
        size_kb = buffer.tell() / 1024
        if size_kb <= 300:
            break

    return buffer.getvalue()

if product_files:
    processed_images = []

    with zipfile.ZipFile("output.zip", "w") as zipf:
        for file in product_files:
            product_img = Image.open(file)
            processed_data = process_image(base_img, product_img)
            filename = f"{file.name.split('.')[0]}_formatted.png"
            zipf.writestr(filename, processed_data)
            processed_images.append(filename)

    st.success("Imágenes procesadas correctamente.")
    with open("output.zip", "rb") as f:
        st.download_button("Descargar ZIP", f, file_name="Syna_Formatted_Images.zip")

    st.markdown("### Imágenes generadas:")
    for name in processed_images:
        st.markdown(f"- {name}")
