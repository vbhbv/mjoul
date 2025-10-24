# EthiCore/ContextualClassifier.py
# لتصنيف السيناريو الوارد إلى سياق محدد (مثل "الخصوصية"، "الأزمة").

import joblib
import os
# ملاحظة: تم حذف استيراد TfidfVectorizer لأنه غير مستخدم مباشرة في هذه الدالة.

class ContextualClassifier:
    """يحدد السياق الأخلاقي للسيناريو المدخل لتطبيق قواعد الأولوية."""
    def __init__(self, model_path="models/classifier_model.pkl", vectorizer_path="models/vectorizer.pkl", contexts=["privacy_scenario", "crisis_management", "default"]):
        self.contexts = contexts
        self.model = None
        self.vectorizer = None
        
        # يجب أن تفترض أن النماذج قد تم تدريبها وحفظها مسبقاً في مجلد 'models/'
        try:
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                # self.model = joblib.load(model_path) # تم إيقاف التحميل للاختبار السهل
                # self.vectorizer = joblib.load(vectorizer_path) # تم إيقاف التحميل للاختبار السهل
                print("تحذير: نموذج تصنيف السياق غير محمل. سيتم استخدام التصنيف الافتراضي.")
        except Exception:
            pass # سيتم استخدام السياق الافتراضي في حالة الفشل

    def classify(self, scenario_text: str) -> str:
        """يصنف النص المدخل ويعيد السياق المطابق."""
        
        # --- محاكاة التصنيف (لغرض الاختبار) ---
        scenario_text_lower = scenario_text.lower()
        if "خصوصية" in scenario_text_lower or "بيانات" in scenario_text_lower:
            return "privacy_scenario"
        if "أزمة" in scenario_text_lower or "إنقاذ" in scenario_text_lower:
            return "crisis_management"
            
        return "default"
