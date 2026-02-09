"""
Flask Web Application for Wav2Lip Video Processing
Simple interface for uploading video and audio, processing, and viewing results
"""
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from video_inference import Wav2LipVideoProcessor
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wav2lip-video-processing-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Upload and output directories
UPLOAD_FOLDER = os.path.join(config.BASE_DIR, 'uploads')
OUTPUT_FOLDER = config.OUTPUTS_DIR
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'mp4', 'm4a', 'aac'}

# Global processor instance
processor = None


def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_processor():
    """Get or create processor instance"""
    global processor
    if processor is None:
        checkpoint_path = config.WAV2LIP_CHECKPOINT
        if not os.path.exists(checkpoint_path):
            # Try alternative paths
            alt_paths = [
                os.path.join(config.BASE_DIR, '..', 'checkpoints', 'wav2lip_gan.pth'),
                os.path.join(config.BASE_DIR, '..', 'ai-slide-generator', 'Wav2Lip', 'checkpoints', 'wav2lip_gan.pth'),
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    checkpoint_path = alt_path
                    break
        
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(
                f"Wav2Lip checkpoint not found. Please place wav2lip_gan.pth in {config.MODELS_DIR}"
            )
        
        processor = Wav2LipVideoProcessor(checkpoint_path)
    return processor


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        # Check if files are present
        if 'video' not in request.files or 'audio' not in request.files:
            return jsonify({'error': 'Both video and audio files are required'}), 400
        
        video_file = request.files['video']
        audio_file = request.files['audio']
        
        # Check if files are selected
        if video_file.filename == '' or audio_file.filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        # Validate file types
        if not allowed_file(video_file.filename, ALLOWED_VIDEO_EXTENSIONS):
            return jsonify({'error': 'Invalid video file type. Allowed: mp4, avi, mov, mkv, webm'}), 400
        
        if not allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
            return jsonify({'error': 'Invalid audio file type. Allowed: wav, mp3, mp4, m4a, aac'}), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        session_folder = os.path.join(UPLOAD_FOLDER, session_id)
        os.makedirs(session_folder, exist_ok=True)
        
        # Save uploaded files
        video_filename = secure_filename(video_file.filename)
        audio_filename = secure_filename(audio_file.filename)
        
        video_path = os.path.join(session_folder, f'video_{video_filename}')
        audio_path = os.path.join(session_folder, f'audio_{audio_filename}')
        
        video_file.save(video_path)
        audio_file.save(audio_path)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'video_path': video_path,
            'audio_path': audio_path,
            'message': 'Files uploaded successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process', methods=['POST'])
def process_video():
    """Process video with Wav2Lip"""
    try:
        data = request.json
        session_id = data.get('session_id')
        quality = data.get('quality', 'medium')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        session_folder = os.path.join(UPLOAD_FOLDER, session_id)
        if not os.path.exists(session_folder):
            return jsonify({'error': 'Session not found'}), 404
        
        # Find uploaded files
        files = os.listdir(session_folder)
        video_file = next((f for f in files if f.startswith('video_')), None)
        audio_file = next((f for f in files if f.startswith('audio_')), None)
        
        if not video_file or not audio_file:
            return jsonify({'error': 'Uploaded files not found'}), 404
        
        video_path = os.path.join(session_folder, video_file)
        audio_path = os.path.join(session_folder, audio_file)
        
        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'lipsynced_{timestamp}.mp4'
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Get quality parameters
        params = config.QUALITY_PRESETS.get(quality, config.QUALITY_PRESETS['medium'])
        
        # Process video
        proc = get_processor()
        proc.process_video(
            face_video_path=video_path,
            audio_source_path=audio_path,
            output_path=output_path,
            **params
        )
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'output_url': url_for('download_video', filename=output_filename),
            'message': 'Video processed successfully'
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download_video(filename):
    """Download processed video"""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/view/<filename>')
def view_video(filename):
    """View processed video"""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, mimetype='video/mp4')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/outputs')
def list_outputs():
    """List all processed videos"""
    try:
        if not os.path.exists(OUTPUT_FOLDER):
            return jsonify({'outputs': []})
        
        files = []
        for filename in os.listdir(OUTPUT_FOLDER):
            if filename.endswith('.mp4'):
                file_path = os.path.join(OUTPUT_FOLDER, filename)
                stat = os.stat(file_path)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    'download_url': url_for('download_video', filename=filename),
                    'view_url': url_for('view_video', filename=filename)
                })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'outputs': files})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        checkpoint_exists = os.path.exists(config.WAV2LIP_CHECKPOINT)
        return jsonify({
            'status': 'healthy',
            'checkpoint_loaded': checkpoint_exists,
            'checkpoint_path': config.WAV2LIP_CHECKPOINT
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Wav2Lip Video Processing Web Interface")
    print("="*60)
    print(f"\nStarting server...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print(f"Checkpoint: {config.WAV2LIP_CHECKPOINT}")
    print("\nOpen your browser and navigate to: http://localhost:5001")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
