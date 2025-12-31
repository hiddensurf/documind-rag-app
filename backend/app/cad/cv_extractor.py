"""
CAD Feature Extractor using Computer Vision
Extracts text, shapes, dimensions, and structure from CAD images
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional
import logging
import json
import re

logger = logging.getLogger(__name__)

class CADFeatureExtractor:
    """Extract features from CAD drawings using OpenCV"""
    
    def __init__(self):
        self.min_line_length = 20
        self.min_circle_radius = 5
    
    def extract_features(self, image_path: str) -> Dict:
        """
        Main extraction method - extracts all features from CAD image
        
        Returns:
            Dict with extracted features including text, shapes, complexity metrics
        """
        try:
            logger.info(f"🔍 Extracting CV features from: {image_path}")
            
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Run all extraction methods
            features = {
                "image_path": image_path,
                "image_size": {"width": img.shape[1], "height": img.shape[0]},
                "text": self._extract_text(img),
                "shapes": self._detect_shapes(gray),
                "lines": self._detect_lines(gray),
                "complexity": self._calculate_complexity(gray),
                "color_analysis": self._analyze_colors(img),
                "dimensions": self._extract_dimensions(img),
            }
            
            # Calculate summary stats
            features["summary"] = self._generate_summary(features)
            
            logger.info(f"✅ Extracted features: {len(features['text']['all_text'])} text items, "
                       f"{features['shapes']['circles']} circles, "
                       f"{features['lines']['total_lines']} lines")
            
            return features
            
        except Exception as e:
            logger.error(f"❌ CV extraction failed: {e}")
            return self._empty_features(image_path, str(e))
    
    def _extract_text(self, img) -> Dict:
        """Extract text using OCR"""
        try:
            # Convert to PIL Image for pytesseract
            pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            
            # Extract text with bounding boxes
            data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
            
            # Filter out low confidence text
            texts = []
            for i, conf in enumerate(data['conf']):
                if conf > 30 and data['text'][i].strip():
                    texts.append({
                        "text": data['text'][i].strip(),
                        "confidence": conf,
                        "position": {
                            "x": data['left'][i],
                            "y": data['top'][i],
                            "width": data['width'][i],
                            "height": data['height'][i]
                        }
                    })
            
            # Extract all text as single string
            all_text = " ".join([t['text'] for t in texts])
            
            # Try to find dimension patterns (e.g., "150mm", "30°", "R15")
            dimensions = self._find_dimension_patterns(all_text)
            
            # Find technical annotations
            technical_terms = self._find_technical_terms(all_text)
            
            return {
                "all_text": all_text,
                "text_items": texts,
                "text_count": len(texts),
                "dimensions_found": dimensions,
                "technical_terms": technical_terms
            }
        except Exception as e:
            logger.warning(f"Text extraction failed: {e}")
            return {
                "all_text": "",
                "text_items": [],
                "text_count": 0,
                "dimensions_found": [],
                "technical_terms": []
            }
    
    def _detect_shapes(self, gray) -> Dict:
        """Detect circles, rectangles, and other shapes"""
        try:
            shapes = {
                "circles": 0,
                "rectangles": 0,
                "polygons": 0,
                "circle_list": [],
                "rectangle_list": []
            }
            
            # Detect circles using Hough Circle Transform
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=20,
                param1=50,
                param2=30,
                minRadius=self.min_circle_radius,
                maxRadius=200
            )
            
            if circles is not None:
                circles = np.uint16(np.around(circles))
                shapes["circles"] = len(circles[0])
                shapes["circle_list"] = [
                    {"x": int(c[0]), "y": int(c[1]), "radius": int(c[2])}
                    for c in circles[0]
                ]
            
            # Detect rectangles/contours
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) == 4:  # Rectangle
                    shapes["rectangles"] += 1
                    x, y, w, h = cv2.boundingRect(approx)
                    if w > 10 and h > 10:  # Filter small noise
                        shapes["rectangle_list"].append({"x": x, "y": y, "width": w, "height": h})
                elif len(approx) > 4:  # Polygon
                    shapes["polygons"] += 1
            
            return shapes
        except Exception as e:
            logger.warning(f"Shape detection failed: {e}")
            return {"circles": 0, "rectangles": 0, "polygons": 0, "circle_list": [], "rectangle_list": []}
    
    def _detect_lines(self, gray) -> Dict:
        """Detect lines using Hough Transform"""
        try:
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi/180,
                threshold=50,
                minLineLength=self.min_line_length,
                maxLineGap=10
            )
            
            if lines is None:
                return {"total_lines": 0, "horizontal": 0, "vertical": 0, "diagonal": 0}
            
            horizontal = 0
            vertical = 0
            diagonal = 0
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                
                if angle < 10 or angle > 170:
                    horizontal += 1
                elif 80 < angle < 100:
                    vertical += 1
                else:
                    diagonal += 1
            
            return {
                "total_lines": len(lines),
                "horizontal": horizontal,
                "vertical": vertical,
                "diagonal": diagonal
            }
        except Exception as e:
            logger.warning(f"Line detection failed: {e}")
            return {"total_lines": 0, "horizontal": 0, "vertical": 0, "diagonal": 0}
    
    def _calculate_complexity(self, gray) -> Dict:
        """Calculate drawing complexity metrics"""
        try:
            # Edge density
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Gradient magnitude (detail level)
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient = np.sqrt(sobelx**2 + sobely**2)
            avg_gradient = np.mean(gradient)
            
            # Complexity score (0-10)
            complexity_score = min(10, edge_density * 100 + avg_gradient / 10)
            
            return {
                "edge_density": float(edge_density),
                "avg_gradient": float(avg_gradient),
                "complexity_score": round(complexity_score, 2),
                "complexity_level": self._classify_complexity(complexity_score)
            }
        except Exception as e:
            logger.warning(f"Complexity calculation failed: {e}")
            return {"complexity_score": 0, "complexity_level": "unknown"}
    
    def _analyze_colors(self, img) -> Dict:
        """Analyze color usage in drawing"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Detect predominant colors
            unique_colors = len(np.unique(img.reshape(-1, img.shape[2]), axis=0))
            
            # Check if mostly black/white (typical CAD)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            is_grayscale = np.allclose(img[:,:,0], img[:,:,1]) and np.allclose(img[:,:,1], img[:,:,2])
            
            return {
                "unique_colors": unique_colors,
                "is_grayscale": is_grayscale,
                "color_count": "monochrome" if is_grayscale else "color"
            }
        except Exception as e:
            logger.warning(f"Color analysis failed: {e}")
            return {"unique_colors": 0, "is_grayscale": True}
    
    def _extract_dimensions(self, img) -> Dict:
        """Try to extract dimension markers and arrows"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect dimension arrows (simplified)
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=30, maxLineGap=10)
            
            dimension_markers = 0
            if lines is not None:
                # Simple heuristic: look for parallel lines (dimension lines)
                dimension_markers = len(lines) // 10  # Rough estimate
            
            return {
                "dimension_markers_estimated": dimension_markers,
                "has_dimensions": dimension_markers > 0
            }
        except Exception as e:
            logger.warning(f"Dimension extraction failed: {e}")
            return {"dimension_markers_estimated": 0, "has_dimensions": False}
    
    def _find_dimension_patterns(self, text: str) -> List[str]:
        """Find dimension patterns in text (e.g., '150mm', '30°', 'R15')"""
        patterns = [
            r'\d+\.?\d*\s*mm',      # millimeters
            r'\d+\.?\d*\s*cm',      # centimeters
            r'\d+\.?\d*\s*m\b',     # meters
            r'\d+\.?\d*\s*°',       # degrees
            r'R\d+\.?\d*',          # radius
            r'Ø\d+\.?\d*',          # diameter
            r'\d+\.?\d*\s*x\s*\d+\.?\d*',  # dimensions like "150 x 75"
        ]
        
        dimensions = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dimensions.extend(matches)
        
        return list(set(dimensions))  # Remove duplicates
    
    def _find_technical_terms(self, text: str) -> List[str]:
        """Find technical terms and standards"""
        technical_keywords = [
            'ISO', 'DIN', 'ANSI', 'ASTM', 'SCALE', 'SECTION',
            'VIEW', 'DETAIL', 'ASSEMBLY', 'PART', 'REV',
            'MATERIAL', 'FINISH', 'TOLERANCE', 'THREAD'
        ]
        
        found_terms = []
        for keyword in technical_keywords:
            if keyword.lower() in text.lower():
                found_terms.append(keyword)
        
        return found_terms
    
    def _classify_complexity(self, score: float) -> str:
        """Classify complexity level"""
        if score < 2:
            return "very_simple"
        elif score < 4:
            return "simple"
        elif score < 6:
            return "moderate"
        elif score < 8:
            return "complex"
        else:
            return "very_complex"
    
    def _generate_summary(self, features: Dict) -> Dict:
        """Generate human-readable summary"""
        return {
            "total_text_items": features['text']['text_count'],
            "total_shapes": features['shapes']['circles'] + features['shapes']['rectangles'],
            "total_lines": features['lines']['total_lines'],
            "complexity": features['complexity']['complexity_level'],
            "has_dimensions": len(features['text']['dimensions_found']) > 0,
            "has_technical_terms": len(features['text']['technical_terms']) > 0
        }
    
    def _empty_features(self, image_path: str, error: str) -> Dict:
        """Return empty features dict on error"""
        return {
            "image_path": image_path,
            "error": error,
            "text": {"all_text": "", "text_items": [], "text_count": 0},
            "shapes": {"circles": 0, "rectangles": 0},
            "lines": {"total_lines": 0},
            "complexity": {"complexity_score": 0},
            "summary": {}
        }
    
    def format_for_llm(self, features: Dict) -> str:
        """Format extracted features as text prompt for LLM"""
        summary = features.get('summary', {})
        text_data = features.get('text', {})
        shapes = features.get('shapes', {})
        lines = features.get('lines', {})
        complexity = features.get('complexity', {})
        
        prompt = f"""CAD DRAWING ANALYSIS (Computer Vision Extraction)

IMAGE PROPERTIES:
- Size: {features.get('image_size', {}).get('width')}x{features.get('image_size', {}).get('height')} pixels
- Complexity: {complexity.get('complexity_level', 'unknown').upper()}
- Complexity Score: {complexity.get('complexity_score', 0)}/10

DETECTED SHAPES:
- Circles: {shapes.get('circles', 0)}
- Rectangles: {shapes.get('rectangles', 0)}
- Total Lines: {lines.get('total_lines', 0)} (H:{lines.get('horizontal', 0)}, V:{lines.get('vertical', 0)}, D:{lines.get('diagonal', 0)})

EXTRACTED TEXT ({text_data.get('text_count', 0)} items):
{text_data.get('all_text', 'No text detected')[:1000]}

DIMENSIONS FOUND:
{', '.join(text_data.get('dimensions_found', [])) if text_data.get('dimensions_found') else 'No dimensions detected'}

TECHNICAL TERMS:
{', '.join(text_data.get('technical_terms', [])) if text_data.get('technical_terms') else 'No technical terms detected'}

DRAWING CHARACTERISTICS:
- Has dimension markers: {'Yes' if features.get('dimensions', {}).get('has_dimensions') else 'No'}
- Color mode: {features.get('color_analysis', {}).get('color_count', 'unknown')}
"""
        return prompt
