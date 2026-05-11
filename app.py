import streamlit as st
from pypdf import PdfReader, PdfWriter
import io

def process_pdf(uploaded_file):
    # Read the uploaded file into memory
    pdf_bytes = uploaded_file.read()
    
    # Create two separate file-like objects in memory from the bytes
    qr_stream = io.BytesIO(pdf_bytes)
    inv_stream = io.BytesIO(pdf_bytes)
    
    reader_qr = PdfReader(qr_stream)
    reader_inv = PdfReader(inv_stream)
    writer = PdfWriter()
    
    # --- TIGHT CROP COORDINATES ---
    qr_coords = (185, 458, 410, 820)      
    invoice_coords = (30, 70, 565, 455)   

    num_pages = len(reader_qr.pages)
    
    for i in range(num_pages):
        # 1. QR Label (Top Half)
        page_qr = reader_qr.pages[i]
        page_qr.cropbox.lower_left = (qr_coords[0], qr_coords[1])
        page_qr.cropbox.upper_right = (qr_coords[2], qr_coords[3])
        writer.add_page(page_qr)
        
        # 2. Invoice (Bottom Half)
        page_inv = reader_inv.pages[i]
        page_inv.cropbox.lower_left = (invoice_coords[0], invoice_coords[1])
        page_inv.cropbox.upper_right = (invoice_coords[2], invoice_coords[3])
        writer.add_page(page_inv)
        
    # Save the result to a new in-memory bytes buffer
    output_pdf = io.BytesIO()
    writer.write(output_pdf)
    output_pdf.seek(0) # Reset pointer to the beginning
    
    return output_pdf, num_pages

# --- Web App Interface ---
st.set_page_config(page_title="Flipkart Label Cropper", page_icon="✂️")
st.title("Flipkart Label Cropper ✂️")
st.write("Upload your Flipkart PDF to crop and split it into alternating shipping labels and invoices.")

# File uploader widget
uploaded_file = st.file_uploader("Upload Flipkart Labels (PDF)", type="pdf")

if uploaded_file is not None:
    if st.button("Process Labels"):
        with st.spinner("Cropping and merging..."):
            try:
                # Process the file
                processed_pdf, pages = process_pdf(uploaded_file)
                
                st.success(f"Success! Processed {pages} original pages into {pages * 2} cropped, alternating pages.")
                
                # Download button
                st.download_button(
                    label="⬇️ Download Cropped PDF",
                    data=processed_pdf,
                    file_name="flipkart_labels_ready.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
