import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
from datetime import datetime

def process_pdfs(uploaded_files):
    writer = PdfWriter()
    total_original_pages = 0
    
    # --- YOUR CUSTOM CROP COORDINATES ---
    qr_coords = (185, 458, 410, 820)      
    invoice_coords = (30, 70, 565, 455)   

    # Loop through every file uploaded
    for uploaded_file in uploaded_files:
        # Read the current uploaded file into memory
        pdf_bytes = uploaded_file.read()
        
        # Create two separate streams for this specific file
        qr_stream = io.BytesIO(pdf_bytes)
        inv_stream = io.BytesIO(pdf_bytes)
        
        reader_qr = PdfReader(qr_stream)
        reader_inv = PdfReader(inv_stream)
        
        num_pages = len(reader_qr.pages)
        total_original_pages += num_pages
        
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
            
    # Save the final combined result to a new in-memory bytes buffer
    output_pdf = io.BytesIO()
    writer.write(output_pdf)
    output_pdf.seek(0) # Reset pointer to the beginning
    
    return output_pdf, total_original_pages

# --- Web App Interface ---
st.set_page_config(page_title="Flipkart Label Cropper", page_icon="✂️")
st.title("Flipkart Label Cropper ✂️")
st.write("Upload one or multiple Flipkart PDFs to crop and merge them into alternating shipping labels and invoices.")

# File uploader widget - ACCEPTS MULTIPLE FILES
uploaded_files = st.file_uploader("Upload Flipkart Labels (PDF)", type="pdf", accept_multiple_files=True)

# Check if the list of uploaded files is not empty
if uploaded_files:
    if st.button("Process Labels"):
        with st.spinner("Cropping and merging..."):
            try:
                # Process all files
                processed_pdf, total_pages = process_pdfs(uploaded_files)
                
                st.success(f"Success! Processed {total_pages} original pages across {len(uploaded_files)} file(s) into {total_pages * 2} cropped, alternating pages.")
                
                # Generate dynamic filename with current date and time (DDMMYYYYHHMM)
                timestamp = datetime.now().strftime("%d%m%Y%H%M")
                dynamic_filename = f"flipkart_labels_ready_{timestamp}.pdf"
                
                # Download button
                st.download_button(
                    label="⬇️ Download Combined Cropped PDF",
                    data=processed_pdf,
                    file_name=dynamic_filename,
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888888; font-size: 16px; font-weight: bold;'>Developed by Harshit 😎</p>", 
    unsafe_allow_html=True
)
