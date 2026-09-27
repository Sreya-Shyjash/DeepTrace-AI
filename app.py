from flask import Flask, render_template, request, jsonify, send_file
import os, hashlib, io, base64, numpy as np
from PIL import Image, ImageChops, ImageEnhance
from PIL.ExifTags import TAGS
from fpdf import FPDF

app = Flask(__name__, 
            template_folder='frontend/templates', 
            static_folder='frontend/static')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- RESTORED PDF GENERATOR CLASS ---
class ForensicReport(FPDF):
    def header(self):
        self.set_font('Courier', 'B', 16)
        self.set_text_color(20, 20, 20)
        self.cell(0, 10, 'DEEPTRACE AI - FORENSIC ANALYSIS REPORT', ln=True, align='C')
        self.set_draw_color(0, 242, 255) 
        self.line(10, 22, 200, 22)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Courier', 'I', 8)
        self.cell(0, 10, f'DeepTrace Forensic OS v2.0 - Confidential - Page {self.page_no()}', 0, 0, 'C')

# --- FORENSIC ENGINE FUNCTIONS ---

def calculate_hashes(file_bytes):
    # Generates both real fingerprints
    md5 = hashlib.md5(file_bytes).hexdigest()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    return md5, sha256

def extract_metadata(image):
    exif_data = {}
    try:
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if isinstance(value, bytes): value = value.decode(errors='ignore')
                exif_data[decoded] = str(value)
        else: exif_data = {"Status": "No EXIF Metadata found."}
    except: exif_data = {"Status": "Extraction Failure."}
    return exif_data

def perform_ela_analysis(image_path, quality=90):
    original = Image.open(image_path).convert('RGB')
    temp_ela_path = os.path.join(UPLOAD_FOLDER, 'temp_ela.jpg')
    original.save(temp_ela_path, 'JPEG', quality=int(quality))
    resaved = Image.open(temp_ela_path)
    ela_image = ImageChops.difference(original, resaved)
    
    pixel_data = np.array(ela_image)
    mean_val = np.mean(pixel_data)
    std_val = np.std(pixel_data)
    
    # Forensic Logic
    if std_val < 0.8: score = 85.0 # AI Signature
    else: score = (mean_val * 4.5) + (std_val * 1.5)
    
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema]) or 1
    ela_view = ImageEnhance.Brightness(ela_image).enhance(350.0 / max_diff)
    
    buffered = io.BytesIO()
    ela_view.save(buffered, format="JPEG")
    if os.path.exists(temp_ela_path): os.remove(temp_ela_path)
    return base64.b64encode(buffered.getvalue()).decode(), round(min(score, 99.4), 1)

# --- ROUTES ---

@app.route('/')
def index(): return render_template('index.html')

@app.route('/dashboard')
def dashboard(): return render_template('dashboard.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['file']
    quality = request.form.get('quality', 90)
    file_bytes = file.read()
    temp_path = os.path.join(UPLOAD_FOLDER, "evidence.jpg")
    with open(temp_path, 'wb') as f: f.write(file_bytes)

    img = Image.open(io.BytesIO(file_bytes))
    md5, sha = calculate_hashes(file_bytes)
    metadata = extract_metadata(img)
    ela_b64, score = perform_ela_analysis(temp_path, quality)
    
    if any(k in metadata for k in ['Make', 'Model']): score = max(score - 20, 10.5)

    return jsonify({
        "hashes": {"md5": md5, "sha256": sha},
        "metadata": metadata,
        "ela": ela_b64,
        "score": score,
        "verdict": "MANIPULATED / AI" if score > 55 else "AUTHENTIC",
        "tineye": f"https://tineye.com/search/{md5}"
    })

@app.route('/download_report', methods=['POST'])
def download_report():
    data = request.json
    score_clean = str(data.get('score', '0')).replace('%', '')
    
    pdf = ForensicReport()
    pdf.add_page()
    pdf.set_font("Courier", size=12)
    
    # Section 1: Case Details
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"TIMESTAMP: {data.get('timestamp')}", ln=True)
    pdf.cell(0, 10, f"CASE ID: DT-2026-CYBER", ln=True)
    pdf.ln(5)
    
    # Section 2: Hashes
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Courier", 'B', 12)
    pdf.cell(0, 10, "1. CRYPTOGRAPHIC SIGNATURES", ln=True)
    pdf.set_font("Courier", size=10)
    pdf.cell(0, 8, f"MD5 Hash:    {data.get('md5')}", ln=True)
    pdf.cell(0, 8, f"SHA-256:     {data.get('sha256')}", ln=True)
    pdf.ln(5)
    
    # Section 3: Verdict
    pdf.set_font("Courier", 'B', 12)
    pdf.cell(0, 10, "2. ANALYSIS VERDICT", ln=True)
    pdf.set_font("Courier", size=11)
    pdf.cell(0, 8, f"SUSPICION SCORE: {score_clean}%", ln=True)
    pdf.cell(0, 8, f"SYSTEM RESULT:   {data.get('verdict')}", ln=True)
    pdf.ln(10)
    
    # Section 4: Summary
    pdf.set_font("Courier", 'B', 12)
    pdf.cell(0, 10, "3. FORENSIC SUMMARY", ln=True)
    pdf.set_font("Courier", size=11)
    integrity = "Reliable" if float(score_clean) < 55 else "Compromised"
    summary = (f"The digital evidence was analyzed using Error Level Analysis (ELA) and "
               f"Metadata cross-referencing. A score of {score_clean}% indicates that the "
               f"file integrity is {integrity}. Digital signatures verify file identity.")
    pdf.multi_cell(0, 10, summary)
    
    return send_file(io.BytesIO(pdf.output()), as_attachment=True, download_name="DeepTrace_Report.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True, port=8501)