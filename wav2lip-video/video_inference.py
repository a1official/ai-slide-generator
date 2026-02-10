"""
Video-to-Video Lip Sync using Wav2Lip
Main inference script for processing videos with audio
"""
import os
import sys
import argparse
import numpy as np
import cv2
import torch
from tqdm import tqdm

# Add parent directory to path to import Wav2Lip modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wav2lip_dir = os.path.join(parent_dir, 'Wav2Lip')
sys.path.insert(0, wav2lip_dir)

import audio
import face_detection
from models import Wav2Lip

# Import local modules
import config
from utils import (
    load_video_frames, 
    extract_audio_from_video, 
    merge_audio_video,
    validate_video_file,
    validate_audio_file,
    get_video_info,
    create_video_writer,
    get_smoothened_boxes,
    cleanup_temp_files
)


class Wav2LipVideoProcessor:
    """Main class for processing videos with Wav2Lip"""
    
    def __init__(self, checkpoint_path: str, device: str = None):
        """
        Initialize the Wav2Lip video processor
        
        Args:
            checkpoint_path: Path to Wav2Lip model checkpoint
            device: Device to use ('cuda' or 'cpu')
        """
        self.checkpoint_path = checkpoint_path
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        
        print(f'Using {self.device} for inference.')
    
    def load_model(self):
        """Load the Wav2Lip model"""
        if self.model is not None:
            return
        
        print(f"Loading checkpoint from: {self.checkpoint_path}")
        
        if self.device == 'cuda':
            checkpoint = torch.load(self.checkpoint_path, weights_only=False)
        else:
            checkpoint = torch.load(
                self.checkpoint_path,
                map_location=lambda storage, loc: storage,
                weights_only=False
            )
        
        self.model = Wav2Lip()
        s = checkpoint["state_dict"]
        new_s = {}
        for k, v in s.items():
            new_s[k.replace('module.', '')] = v
        self.model.load_state_dict(new_s)
        
        self.model = self.model.to(self.device)
        self.model.eval()
        print("Model loaded successfully")
    
    def detect_faces(self, frames, batch_size=16, pads=[0, 10, 0, 0], 
                    nosmooth=False, box=None, static=False, detect_every_n=1):
        """
        Detect faces in video frames with optimization options
        
        Args:
            frames: List of video frames
            batch_size: Batch size for face detection
            pads: Padding [top, bottom, left, right]
            nosmooth: Disable smoothing
            box: Manual bounding box [y1, y2, x1, x2]
            static: If True, detect face only in first frame and reuse (FAST!)
            detect_every_n: Detect face every N frames (1 = every frame, 10 = every 10th frame)
            
        Returns:
            List of [face_crop, coordinates] for each frame
        """
        if box and box[0] != -1:
            print('Using specified bounding box instead of face detection...')
            y1, y2, x1, x2 = box
            return [[f[y1:y2, x1:x2], (y1, y2, x1, x2)] for f in frames]
        
        # OPTIMIZATION: Static mode - detect once, reuse for all frames
        if static:
            print('🚀 OPTIMIZATION: Static mode enabled - detecting face in first frame only...')
            frames_to_detect = [frames[0]]
        # OPTIMIZATION: Detect every N frames
        elif detect_every_n > 1:
            print(f'🚀 OPTIMIZATION: Detecting faces every {detect_every_n} frames...')
            frames_to_detect = [frames[i] for i in range(0, len(frames), detect_every_n)]
        else:
            frames_to_detect = frames
        
        detector = face_detection.FaceAlignment(
            face_detection.LandmarksType._2D,
            flip_input=False,
            device=self.device
        )
        
        # Detect faces in batches
        while True:
            predictions = []
            try:
                for i in tqdm(range(0, len(frames_to_detect), batch_size), desc="Detecting faces"):
                    batch = np.array(frames_to_detect[i:i + batch_size])
                    predictions.extend(detector.get_detections_for_batch(batch))
            except RuntimeError:
                if batch_size == 1:
                    raise RuntimeError(
                        'Image too big to run face detection on GPU. '
                        'Please use the --resize_factor argument'
                    )
                batch_size //= 2
                print(f'Recovering from OOM error; New batch size: {batch_size}')
                continue
            break
        
        # Process detections
        detected_boxes = []
        pady1, pady2, padx1, padx2 = pads
        
        for rect, image in zip(predictions, frames_to_detect):
            if rect is None:
                os.makedirs(config.TEMP_DIR, exist_ok=True)
                cv2.imwrite(os.path.join(config.TEMP_DIR, 'faulty_frame.jpg'), image)
                raise ValueError(
                    'Face not detected! Ensure the video contains a face in all frames.'
                )
            
            y1 = max(0, rect[1] - pady1)
            y2 = min(image.shape[0], rect[3] + pady2)
            x1 = max(0, rect[0] - padx1)
            x2 = min(image.shape[1], rect[2] + padx2)
            
            detected_boxes.append([x1, y1, x2, y2])
        
        # OPTIMIZATION: Expand boxes to all frames
        if static:
            # Use first frame's detection for all frames
            boxes = np.array([detected_boxes[0]] * len(frames))
            print(f'✓ Reusing face detection from first frame for all {len(frames)} frames')
        elif detect_every_n > 1:
            # Interpolate boxes for frames in between detections
            boxes = []
            for i in range(len(frames)):
                detection_idx = min(i // detect_every_n, len(detected_boxes) - 1)
                boxes.append(detected_boxes[detection_idx])
            boxes = np.array(boxes)
            print(f'✓ Interpolated {len(detected_boxes)} detections to {len(frames)} frames')
        else:
            boxes = np.array(detected_boxes)
        
        if not nosmooth and not static:  # No need to smooth if static
            boxes = get_smoothened_boxes(boxes, T=5)
        
        results = [
            [image[y1:y2, x1:x2], (y1, y2, x1, x2)]
            for image, (x1, y1, x2, y2) in zip(frames, boxes)
        ]
        
        del detector
        return results
    
    def prepare_datagen(self, frames, mel_chunks, face_det_results, 
                       batch_size=128, img_size=96, static=False):
        """
        Generator for preparing batches of data
        
        Args:
            frames: List of video frames
            mel_chunks: List of mel spectrogram chunks
            face_det_results: Face detection results
            batch_size: Batch size for processing
            img_size: Size to resize face crops
            static: Use only first frame
            
        Yields:
            Batches of (img_batch, mel_batch, frame_batch, coords_batch)
        """
        img_batch, mel_batch, frame_batch, coords_batch = [], [], [], []
        
        for i, m in enumerate(mel_chunks):
            idx = 0 if static else i % len(frames)
            frame_to_save = frames[idx].copy()
            face, coords = face_det_results[idx].copy()
            
            face = cv2.resize(face, (img_size, img_size))
            
            img_batch.append(face)
            mel_batch.append(m)
            frame_batch.append(frame_to_save)
            coords_batch.append(coords)
            
            if len(img_batch) >= batch_size:
                img_batch, mel_batch = np.asarray(img_batch), np.asarray(mel_batch)
                
                img_masked = img_batch.copy()
                img_masked[:, img_size//2:] = 0
                
                img_batch = np.concatenate((img_masked, img_batch), axis=3) / 255.
                mel_batch = np.reshape(
                    mel_batch, 
                    [len(mel_batch), mel_batch.shape[1], mel_batch.shape[2], 1]
                )
                
                yield img_batch, mel_batch, frame_batch, coords_batch
                img_batch, mel_batch, frame_batch, coords_batch = [], [], [], []
        
        if len(img_batch) > 0:
            img_batch, mel_batch = np.asarray(img_batch), np.asarray(mel_batch)
            
            img_masked = img_batch.copy()
            img_masked[:, img_size//2:] = 0
            
            img_batch = np.concatenate((img_masked, img_batch), axis=3) / 255.
            mel_batch = np.reshape(
                mel_batch,
                [len(mel_batch), mel_batch.shape[1], mel_batch.shape[2], 1]
            )
            
            yield img_batch, mel_batch, frame_batch, coords_batch
    
    def process_video(self, face_video_path: str, audio_source_path: str,
                     output_path: str, **kwargs):
        """
        Process a video with audio to generate lip-synced output
        
        Args:
            face_video_path: Path to video containing faces
            audio_source_path: Path to audio file or video with audio
            output_path: Path to save output video
            **kwargs: Additional parameters (see config.DEFAULT_PARAMS)
        """
        # Merge default params with provided kwargs
        params = config.DEFAULT_PARAMS.copy()
        params.update(kwargs)
        
        # Validate inputs
        if not validate_video_file(face_video_path):
            raise ValueError(f"Invalid face video: {face_video_path}")
        
        # Get video info
        video_info = get_video_info(face_video_path)
        print(f"\nVideo Info:")
        print(f"  Resolution: {video_info['width']}x{video_info['height']}")
        print(f"  FPS: {video_info['fps']}")
        print(f"  Frames: {video_info['frame_count']}")
        print(f"  Duration: {video_info['duration']:.2f}s\n")
        
        # Load video frames
        frames, fps = load_video_frames(
            face_video_path,
            resize_factor=params['resize_factor'],
            rotate=params['rotate'],
            crop=params['crop']
        )
        
        if params['fps']:
            fps = params['fps']
        
        # Extract/load audio
        audio_path = audio_source_path
        if not audio_source_path.endswith('.wav'):
            print('Extracting audio from source...')
            os.makedirs(config.TEMP_DIR, exist_ok=True)
            audio_path = os.path.join(config.TEMP_DIR, 'temp_audio.wav')
            if not extract_audio_from_video(audio_source_path, audio_path):
                raise ValueError("Failed to extract audio")
        
        if not validate_audio_file(audio_path):
            raise ValueError(f"Invalid audio file: {audio_path}")
        
        # Load and process audio
        print("Processing audio...")
        wav = audio.load_wav(audio_path, params['sample_rate'])
        mel = audio.melspectrogram(wav)
        print(f"Mel spectrogram shape: {mel.shape}")
        
        if np.isnan(mel.reshape(-1)).sum() > 0:
            raise ValueError(
                'Mel contains nan! Using a TTS voice? '
                'Add a small epsilon noise to the wav file and try again'
            )
        
        # Create mel chunks
        mel_chunks = []
        mel_idx_multiplier = 80. / fps
        i = 0
        while True:
            start_idx = int(i * mel_idx_multiplier)
            if start_idx + params['mel_step_size'] > len(mel[0]):
                mel_chunks.append(mel[:, len(mel[0]) - params['mel_step_size']:])
                break
            mel_chunks.append(mel[:, start_idx : start_idx + params['mel_step_size']])
            i += 1
        
        print(f"Number of mel chunks: {len(mel_chunks)}")
        
        # Trim frames to match audio length
        frames = frames[:len(mel_chunks)]
        print(f"Processing {len(frames)} frames")
        
        # Detect faces
        print("\nDetecting faces...")
        face_det_results = self.detect_faces(
            frames,
            batch_size=params['face_det_batch_size'],
            pads=params['pads'],
            nosmooth=params['nosmooth'],
            box=params['box'],
            static=params.get('static', False),
            detect_every_n=params.get('detect_every_n', 1)
        )
        
        # Load model
        self.load_model()
        
        # Prepare output
        frame_h, frame_w = frames[0].shape[:-1]
        temp_video_path = os.path.join(config.TEMP_DIR, 'result.avi')
        out = create_video_writer(
            temp_video_path, 
            fps, 
            (frame_w, frame_h),
            params['output_codec']
        )
        
        # Process frames
        print("\nGenerating lip-synced video...")
        batch_size = params['wav2lip_batch_size']
        gen = self.prepare_datagen(
            frames.copy(),
            mel_chunks,
            face_det_results,
            batch_size=batch_size,
            img_size=params['img_size']
        )
        
        for img_batch, mel_batch, frame_batch, coords_batch in tqdm(
            gen, 
            total=int(np.ceil(float(len(mel_chunks)) / batch_size)),
            desc="Processing"
        ):
            img_batch = torch.FloatTensor(
                np.transpose(img_batch, (0, 3, 1, 2))
            ).to(self.device)
            mel_batch = torch.FloatTensor(
                np.transpose(mel_batch, (0, 3, 1, 2))
            ).to(self.device)
            
            with torch.no_grad():
                pred = self.model(mel_batch, img_batch)
            
            pred = pred.cpu().numpy().transpose(0, 2, 3, 1) * 255.
            
            for p, f, c in zip(pred, frame_batch, coords_batch):
                y1, y2, x1, x2 = c
                p = cv2.resize(p.astype(np.uint8), (x2 - x1, y2 - y1))
                
                # QUALITY IMPROVEMENT: Blend face with original frame to reduce artifacts
                # Create a mask for smooth blending
                mask = np.ones((y2 - y1, x2 - x1, 3), dtype=np.float32)
                
                # Apply Gaussian blur to mask edges for seamless blending
                feather_amount = min(15, (y2 - y1) // 10)  # Adaptive feathering
                if feather_amount > 0:
                    # Feather the edges
                    mask[:feather_amount, :] *= np.linspace(0, 1, feather_amount)[:, np.newaxis, np.newaxis]
                    mask[-feather_amount:, :] *= np.linspace(1, 0, feather_amount)[:, np.newaxis, np.newaxis]
                    mask[:, :feather_amount] *= np.linspace(0, 1, feather_amount)[np.newaxis, :, np.newaxis]
                    mask[:, -feather_amount:] *= np.linspace(1, 0, feather_amount)[np.newaxis, :, np.newaxis]
                
                # Blend the face
                original_face = f[y1:y2, x1:x2].astype(np.float32)
                blended = (p.astype(np.float32) * mask + original_face * (1 - mask)).astype(np.uint8)
                
                f[y1:y2, x1:x2] = blended
                out.write(f)
        
        out.release()
        
        # Merge audio and video
        print("\nMerging audio and video...")
        if not merge_audio_video(
            temp_video_path, 
            audio_path, 
            output_path,
            params['output_quality']
        ):
            raise ValueError("Failed to merge audio and video")
        
        print(f"\n✓ Successfully created lip-synced video: {output_path}")
        
        # Cleanup
        cleanup_temp_files(config.TEMP_DIR, keep_patterns=['faulty_frame'])


def main():
    parser = argparse.ArgumentParser(
        description='Video-to-Video Lip Sync using Wav2Lip'
    )
    
    # Required arguments
    parser.add_argument('--checkpoint', type=str, required=True,
                       help='Path to Wav2Lip checkpoint')
    parser.add_argument('--face_video', type=str, required=True,
                       help='Path to video containing faces')
    parser.add_argument('--audio', type=str, required=True,
                       help='Path to audio file or video with audio')
    parser.add_argument('--output', type=str, required=True,
                       help='Path to save output video')
    
    # Optional arguments
    parser.add_argument('--quality', type=str, default='medium',
                       choices=['low', 'medium', 'high'],
                       help='Quality preset')
    parser.add_argument('--resize_factor', type=int, default=1,
                       help='Reduce resolution by this factor')
    parser.add_argument('--face_det_batch_size', type=int, default=16,
                       help='Batch size for face detection')
    parser.add_argument('--wav2lip_batch_size', type=int, default=128,
                       help='Batch size for Wav2Lip model')
    parser.add_argument('--rotate', action='store_true',
                       help='Rotate video 90 degrees clockwise')
    parser.add_argument('--nosmooth', action='store_true',
                       help='Disable face detection smoothing')
    
    # OPTIMIZATION arguments
    parser.add_argument('--static', action='store_true',
                       help='🚀 FAST: Detect face once and reuse for all frames (100x-1000x faster!)')
    parser.add_argument('--detect_every_n', type=int, default=1,
                       help='🚀 FAST: Detect face every N frames (e.g., 10 = detect every 10th frame)')
    
    args = parser.parse_args()
    
    # Apply quality preset
    params = config.QUALITY_PRESETS[args.quality].copy()
    
    # Override with command line arguments
    if args.resize_factor != 1:
        params['resize_factor'] = args.resize_factor
    if args.face_det_batch_size != 16:
        params['face_det_batch_size'] = args.face_det_batch_size
    if args.wav2lip_batch_size != 128:
        params['wav2lip_batch_size'] = args.wav2lip_batch_size
    if args.rotate:
        params['rotate'] = True
    if args.nosmooth:
        params['nosmooth'] = True
    if args.static:
        params['static'] = True
    if args.detect_every_n != 1:
        params['detect_every_n'] = args.detect_every_n
    
    # Create processor and run
    processor = Wav2LipVideoProcessor(args.checkpoint)
    processor.process_video(
        args.face_video,
        args.audio,
        args.output,
        **params
    )


if __name__ == '__main__':
    main()
