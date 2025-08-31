"""
Table and Image Processing Module
Handles extraction and processing of tables and images from documents
"""

import io
import base64
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import fitz  # PyMuPDF
from langchain.schema import Document as LangChainDocument


class TableProcessor:
    """Extract and process tables from various document types"""
    
    def __init__(self):
        self.table_detection_confidence = 0.7
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF using multiple methods"""
        tables = []
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Method 1: Find tables using text blocks
            text_blocks = page.get_text("dict")
            page_tables = self._detect_tables_from_blocks(text_blocks, page_num)
            tables.extend(page_tables)
            
            # Method 2: Find tables using image analysis
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            image_tables = self._detect_tables_from_image(img_data, page_num)
            tables.extend(image_tables)
        
        doc.close()
        return self._merge_duplicate_tables(tables)
    
    def _detect_tables_from_blocks(self, text_blocks: Dict, page_num: int) -> List[Dict[str, Any]]:
        """Detect tables from text blocks in PDF"""
        tables = []
        blocks = text_blocks.get("blocks", [])
        
        for block_idx, block in enumerate(blocks):
            if "lines" not in block:
                continue
                
            # Look for table-like structures
            lines = block["lines"]
            if len(lines) < 2:  # Need at least 2 lines for a table
                continue
            
            # Check if lines have consistent column structure
            line_spans = []
            for line in lines:
                spans = line.get("spans", [])
                span_positions = [(span["bbox"][0], span["text"]) for span in spans]
                line_spans.append(span_positions)
            
            if self._is_table_structure(line_spans):
                table_data = self._extract_table_data(line_spans)
                if table_data:
                    tables.append({
                        "page": page_num,
                        "block_id": block_idx,
                        "type": "text_based",
                        "data": table_data,
                        "bbox": block["bbox"],
                        "confidence": 0.8
                    })
        
        return tables
    
    def _detect_tables_from_image(self, img_data: bytes, page_num: int) -> List[Dict[str, Any]]:
        """Detect tables from page images using OpenCV"""
        try:
            # Convert image data to OpenCV format
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combine lines to find table structure
            table_mask = cv2.add(horizontal_lines, vertical_lines)
            
            # Find contours (potential table regions)
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            tables = []
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area > 5000:  # Filter small regions
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Extract table region
                    table_region = img[y:y+h, x:x+w]
                    
                    # Perform OCR on table region
                    table_text = pytesseract.image_to_string(table_region)
                    
                    if self._validate_table_text(table_text):
                        tables.append({
                            "page": page_num,
                            "table_id": i,
                            "type": "image_based",
                            "bbox": [x, y, x+w, y+h],
                            "text": table_text,
                            "confidence": 0.6
                        })
            
            return tables
            
        except Exception as e:
            print(f"Error in image-based table detection: {e}")
            return []
    
    def _is_table_structure(self, line_spans: List[List[Tuple[float, str]]]) -> bool:
        """Check if text lines form a table structure"""
        if len(line_spans) < 2:
            return False
        
        # Check for consistent column alignment
        column_positions = set()
        for spans in line_spans:
            for pos, text in spans:
                column_positions.add(round(pos, -1))  # Round to nearest 10
        
        # Need at least 2 columns
        if len(column_positions) < 2:
            return False
        
        # Check if most lines have multiple columns
        multi_column_lines = sum(1 for spans in line_spans if len(spans) > 1)
        return multi_column_lines / len(line_spans) > 0.5
    
    def _extract_table_data(self, line_spans: List[List[Tuple[float, str]]]) -> Optional[pd.DataFrame]:
        """Extract structured data from table lines"""
        try:
            # Group spans by column positions
            column_positions = []
            all_positions = set()
            
            for spans in line_spans:
                for pos, text in spans:
                    all_positions.add(round(pos, -1))
            
            sorted_positions = sorted(all_positions)
            
            # Create table rows
            table_rows = []
            for spans in line_spans:
                row = [""] * len(sorted_positions)
                for pos, text in spans:
                    rounded_pos = round(pos, -1)
                    if rounded_pos in sorted_positions:
                        col_idx = sorted_positions.index(rounded_pos)
                        row[col_idx] = text.strip()
                table_rows.append(row)
            
            if table_rows:
                df = pd.DataFrame(table_rows)
                # Remove empty columns
                df = df.loc[:, (df != "").any(axis=0)]
                return df if not df.empty else None
            
            return None
            
        except Exception as e:
            print(f"Error extracting table data: {e}")
            return None
    
    def _validate_table_text(self, text: str) -> bool:
        """Validate if OCR text represents a table"""
        lines = text.strip().split('\n')
        if len(lines) < 2:
            return False
        
        # Check for tabular patterns
        has_numbers = any(any(char.isdigit() for char in line) for line in lines)
        has_multiple_words = sum(len(line.split()) > 1 for line in lines) > 1
        
        return has_numbers and has_multiple_words
    
    def _merge_duplicate_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge duplicate tables detected by different methods"""
        merged = []
        used_indices = set()
        
        for i, table1 in enumerate(tables):
            if i in used_indices:
                continue
                
            # Check for overlapping tables
            merged_table = table1.copy()
            used_indices.add(i)
            
            for j, table2 in enumerate(tables[i+1:], i+1):
                if j in used_indices:
                    continue
                    
                if self._tables_overlap(table1, table2):
                    # Merge the tables (keep the one with higher confidence)
                    if table2.get("confidence", 0) > merged_table.get("confidence", 0):
                        merged_table = table2
                    used_indices.add(j)
            
            merged.append(merged_table)
        
        return merged
    
    def _tables_overlap(self, table1: Dict, table2: Dict) -> bool:
        """Check if two tables overlap significantly"""
        if table1.get("page") != table2.get("page"):
            return False
        
        bbox1 = table1.get("bbox", [0, 0, 0, 0])
        bbox2 = table2.get("bbox", [0, 0, 0, 0])
        
        # Calculate overlap
        x_overlap = max(0, min(bbox1[2], bbox2[2]) - max(bbox1[0], bbox2[0]))
        y_overlap = max(0, min(bbox1[3], bbox2[3]) - max(bbox1[1], bbox2[1]))
        
        overlap_area = x_overlap * y_overlap
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        
        return overlap_area > 0.5 * min(area1, area2)


class ImageProcessor:
    """Extract and process images from documents"""
    
    def __init__(self):
        self.min_image_size = (50, 50)  # Minimum image size to process
        self.ocr_confidence_threshold = 30
    
    def extract_images_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract images from PDF and perform OCR"""
        images = []
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images()
            
            for img_idx, img in enumerate(image_list):
                try:
                    # Extract image
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # Skip if not RGB/GRAY
                        img_data = pix.tobytes("png")
                        
                        # Convert to PIL Image
                        pil_image = Image.open(io.BytesIO(img_data))
                        
                        # Check minimum size
                        if pil_image.size[0] < self.min_image_size[0] or pil_image.size[1] < self.min_image_size[1]:
                            continue
                        
                        # Process image
                        processed_data = self._process_image(pil_image, page_num, img_idx)
                        if processed_data:
                            images.append(processed_data)
                    
                    pix = None  # Free memory
                    
                except Exception as e:
                    print(f"Error processing image {img_idx} on page {page_num}: {e}")
                    continue
        
        doc.close()
        return images
    
    def _process_image(self, image: Image.Image, page_num: int, img_idx: int) -> Optional[Dict[str, Any]]:
        """Process individual image with OCR and analysis"""
        try:
            # Enhance image for OCR
            enhanced_image = self._enhance_image_for_ocr(image)
            
            # Perform OCR
            ocr_data = pytesseract.image_to_data(enhanced_image, output_type=pytesseract.Output.DICT)
            
            # Extract text with confidence
            text_blocks = []
            confidences = []
            
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                conf = int(ocr_data['conf'][i])
                
                if text and conf > self.ocr_confidence_threshold:
                    text_blocks.append(text)
                    confidences.append(conf)
            
            ocr_text = " ".join(text_blocks)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Analyze image type
            image_type = self._classify_image_type(image, ocr_text)
            
            # Convert image to base64 for storage
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                "page": page_num,
                "image_id": img_idx,
                "size": image.size,
                "format": image.format or "PNG",
                "mode": image.mode,
                "ocr_text": ocr_text,
                "ocr_confidence": avg_confidence,
                "image_type": image_type,
                "text_blocks_count": len(text_blocks),
                "image_data": image_base64,  # Store for later use
                "has_text": len(ocr_text) > 0
            }
            
        except Exception as e:
            print(f"Error in image processing: {e}")
            return None
    
    def _enhance_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Enhance image quality for better OCR results"""
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Resize if too small
        if image.size[0] < 300 or image.size[1] < 300:
            scale_factor = max(300 / image.size[0], 300 / image.size[1])
            new_size = (int(image.size[0] * scale_factor), int(image.size[1] * scale_factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    
    def _classify_image_type(self, image: Image.Image, ocr_text: str) -> str:
        """Classify the type of image based on content"""
        # Check if it's primarily text
        if len(ocr_text) > 50:
            return "text_image"
        
        # Check if it contains numbers (might be chart/graph)
        if any(char.isdigit() for char in ocr_text):
            return "chart_or_graph"
        
        # Check image characteristics
        if image.mode == '1':  # Binary image
            return "diagram"
        
        # Analyze color distribution
        if image.mode in ['RGB', 'RGBA']:
            colors = image.getcolors(maxcolors=256)
            if colors and len(colors) < 10:
                return "logo_or_icon"
        
        return "photograph"


class MultimodalDocumentProcessor:
    """Combine text, table, and image processing for comprehensive document analysis"""
    
    def __init__(self):
        self.table_processor = TableProcessor()
        self.image_processor = ImageProcessor()
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process document to extract text, tables, and images"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self._process_pdf(file_path)
        else:
            raise ValueError(f"Multimodal processing not yet supported for {file_ext}")
    
    def _process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Comprehensive PDF processing"""
        # Extract tables
        tables = self.table_processor.extract_tables_from_pdf(pdf_path)
        
        # Extract images
        images = self.image_processor.extract_images_from_pdf(pdf_path)
        
        # Create enriched content
        enriched_content = self._create_enriched_content(tables, images)
        
        return {
            "source": pdf_path,
            "tables": tables,
            "images": images,
            "enriched_content": enriched_content,
            "multimodal_summary": self._create_multimodal_summary(tables, images)
        }
    
    def _create_enriched_content(self, tables: List[Dict], images: List[Dict]) -> List[str]:
        """Create enriched text content combining all modalities"""
        content_blocks = []
        
        # Add table content
        for table in tables:
            table_text = f"[TABLE on page {table['page']}]\n"
            if 'data' in table and table['data'] is not None:
                table_text += table['data'].to_string(index=False)
            elif 'text' in table:
                table_text += table['text']
            content_blocks.append(table_text)
        
        # Add image content
        for image in images:
            if image['has_text']:
                image_text = f"[IMAGE on page {image['page']} - {image['image_type']}]\n"
                image_text += f"OCR Text: {image['ocr_text']}"
                content_blocks.append(image_text)
        
        return content_blocks
    
    def _create_multimodal_summary(self, tables: List[Dict], images: List[Dict]) -> Dict[str, Any]:
        """Create summary of multimodal content"""
        return {
            "total_tables": len(tables),
            "total_images": len(images),
            "images_with_text": sum(1 for img in images if img['has_text']),
            "image_types": list(set(img['image_type'] for img in images)),
            "pages_with_tables": list(set(table['page'] for table in tables)),
            "pages_with_images": list(set(img['page'] for img in images))
        }


# Example usage and testing
if __name__ == "__main__":
    # Test multimodal processing
    processor = MultimodalDocumentProcessor()
    
    # Example: process a PDF (you would use an actual file path)
    # result = processor.process_document("sample.pdf")
    # print(f"Found {result['multimodal_summary']['total_tables']} tables")
    # print(f"Found {result['multimodal_summary']['total_images']} images")
