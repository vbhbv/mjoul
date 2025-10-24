
# EthiCore/ContextualClassifier.py
# لتصنيف السيناريو الوارد إلى سياق محدد (مثل "الخصوصية"، "الأزمة").

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

class ContextualClassifier:
    """يحدد السياق الأخلاقي للسيناريو المدخل لتطبيق قواعد الأولوية."""
    def __init__(self, model_path="classifier_model.pkl", contexts=["privacy_scenario", "crisis_management", "default"]):
        self.contexts = contexts
        try:
            # افتراض تحميل نموذج مُدرب مسبقاً
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load("vectorizer.pkl")
        except FileNotFoundError:
            # في التطوير الحقيقي، يجب تدريب النموذج أولاً
            print("تحذير: نموذج التصنيف غير موجود. استخدام السياق الافتراضي.")
            self.model = None
            self.vectorizer = None
            
    def classify(self, scenario_text: str) -> str:
        """يصنف النص المدخل ويعيد السياق المطابق."""
        if not self.model:
            return "default"
            
        try:
            # تحويل النص إلى متجه باستخدام المحول المدرب
            scenario_vector = self.vectorizer.transform([scenario_text])
            # التنبؤ بالسياق
            prediction_index = self.model.predict(scenario_vector)[0]
            
            # يتم إرجاع اسم السياق (مثل "privacy_scenario")
            return self.contexts[prediction_index]
        except Exception as e:
            # في حالة فشل التصنيف لأي سبب، نعود إلى الوضع الافتراضي
            print(f"فشل التصنيف: {e}. العودة إلى السياق الافتراضي.")
            return "default"

