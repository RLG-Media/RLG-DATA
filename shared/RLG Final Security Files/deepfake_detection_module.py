import os
import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from facenet_pytorch import MTCNN, InceptionResnetV1
from deepface import DeepFace
from transformers import pipeline
from moviepy.editor import VideoFileClip
from skimage.metrics import structural_similarity as ssim

# Load AI Models
mtcnn = MTCNN(keep_all=True, device='cuda' if torch.cuda.is_available() else 'cpu')
face_model = InceptionResnetV1(pretrained='vggface2').eval()
deepfake_detector = pipeline("image-classification", model="facebook/deepfake-detection")

class DeepfakeDetection:
    def __init__(self, threshold=0.8):
        self.threshold = threshold  # Confidence threshold for fake detection

    def extract_frames(self, video_path, frame_rate=1):
        """
        Extracts frames from a video at a specified frame rate.
        """
        clip = VideoFileClip(video_path)
        duration = int(clip.duration)
        frames = []
        
        for i in range(0, duration, frame_rate):
            frame = clip.get_frame(i)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frames.append(frame)

        return frames

    def detect_faces(self, image):
        """
        Detects faces in an image.
        """
        faces, _ = mtcnn.detect(image)
        return faces

    def deepfake_classification(self, image):
        """
        Uses a deep learning model to classify real vs. fake images.
        """
        result = deepfake_detector(image)
        confidence = result[0]['score']
        is_fake = result[0]['label'] == "FAKE"
        return is_fake, confidence

    def compare_faces(self, img1, img2):
        """
        Uses facial recognition to compare two faces and detect inconsistencies.
        """
        try:
            result = DeepFace.verify(img1, img2, model_name="VGG-Face", enforce_detection=False)
            return result["distance"]
        except Exception as e:
            return str(e)

    def detect_video_deepfake(self, video_path):
        """
        Processes a video to detect deepfakes by analyzing multiple frames.
        """
        print(f"Analyzing video: {video_path}")
        frames = self.extract_frames(video_path)
        fake_scores = []

        for frame in frames:
            faces = self.detect_faces(frame)
            if faces is not None:
                for (x, y, w, h) in faces:
                    face = frame[int(y):int(y+h), int(x):int(x+w)]
                    is_fake, confidence = self.deepfake_classification(face)
                    fake_scores.append(confidence)

        avg_fake_score = np.mean(fake_scores) if fake_scores else 0
        return avg_fake_score > self.threshold, avg_fake_score

    def detect_image_deepfake(self, image_path):
        """
        Detects deepfake images by analyzing facial inconsistencies.
        """
        print(f"Analyzing image: {image_path}")
        image = cv2.imread(image_path)
        is_fake, confidence = self.deepfake_classification(image)
        return is_fake, confidence

if __name__ == "__main__":
    dfd = DeepfakeDetection()

    # Test with an image
    test_image = "test_image.jpg"
    fake, confidence = dfd.detect_image_deepfake(test_image)
    print(f"Deepfake Detection - Image: {test_image}, Fake: {fake}, Confidence: {confidence:.2f}")

    # Test with a video
    test_video = "test_video.mp4"
    video_fake, video_confidence = dfd.detect_video_deepfake(test_video)
    print(f"Deepfake Detection - Video: {test_video}, Fake: {video_fake}, Confidence: {video_confidence:.2f}")
