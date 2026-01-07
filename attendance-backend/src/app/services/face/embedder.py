import torch
from facenet_pytorch import InceptionResnetV1
from PIL import Image
from torchvision import transforms


class FaceEmbedder:
    def __init__(self, device: str | None = None, model_name: str = "vggface2"):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = model_name
        self.model = InceptionResnetV1(pretrained=model_name).eval().to(self.device)
        self.transform = transforms.Compose(
            [
                transforms.Resize((160, 160)),
                transforms.ToTensor(),
                transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
            ]
        )

    def embed(self, face: Image.Image):
        tensor = self.transform(face).unsqueeze(0).to(self.device)
        with torch.no_grad():
            embedding = self.model(tensor)
        return embedding[0].cpu().numpy()

