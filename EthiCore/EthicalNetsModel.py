# EthiCore/EthicalNetsModel.py
# تعريف بنية النماذج الأخلاقية الثلاثة (UtiliNet, DeontoNet, VirtuNet).

import torch
import torch.nn as nn
import torch.nn.functional as F
import os

class SimpleNet(nn.Module):
    def __init__(self, input_dim):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 1) 
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        return torch.sigmoid(self.fc2(x))

class EthicalNetsModel:
    """صنف حاوي لإدارة وتوليد تنبؤات الشبكات الأخلاقية الثلاث."""
    def __init__(self, input_dim: int, model_weights_path: str = "models/"):
        self.UtiliNet = SimpleNet(input_dim)
        self.DeontoNet = SimpleNet(input_dim)
        self.VirtuNet = SimpleNet(input_dim)
        
        # في التطبيق الحقيقي: قم بتحميل الأوزان المدربة مسبقًا
        # try:
        #     self.UtiliNet.load_state_dict(torch.load(os.path.join(model_weights_path, "utilinet.pt")))
        # except:
        #     print("تحذير: فشل تحميل أوزان UtiliNet. استخدام الأوزان العشوائية.")

    def predict(self, scenario_vector: list) -> dict:
        """توليد التنبؤات لكل شبكة."""
        scenario_tensor = torch.tensor(scenario_vector, dtype=torch.float32).unsqueeze(0)
        
        with torch.no_grad():
            utili_score = self.UtiliNet(scenario_tensor).item()
            deonto_score = self.DeontoNet(scenario_tensor).item()
            virtu_score = self.VirtuNet(scenario_tensor).item()
        
        return {
            "UtiliNet": utili_score,
            "DeontoNet": deonto_score,
            "VirtuNet": virtu_score
        }
