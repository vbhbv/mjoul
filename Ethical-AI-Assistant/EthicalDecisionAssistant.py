# EthicalDecisionAssistant.py
# الملف الرئيسي لتشغيل المساعد الأخلاقي المحايد محلياً وتجربة وظائف المكتبة.

import numpy as np
from EthiCore import EthicalNetsModel, InferenceEngine, ContextualClassifier

# --- الإعدادات العامة ---
# يجب أن يتطابق حجم المتجه (Embedding) مع حجم الإدخال في EthicalNetsModel
INPUT_DIM = 256 

# --- تهيئة المكونات ---
try:
    # تهيئة نماذج الذكاء الاصطناعي (يفترض تحميل الأوزان)
    ethical_model = EthicalNetsModel(input_dim=INPUT_DIM)
    
    # تهيئة محرك الاستدلال (يحمل ملفات config/ تلقائياً)
    inference_engine = InferenceEngine(config_path="config")
    
    # تهيئة مصنف السياق (يفترض تحميل نماذجه من مجلد 'models/' أو الافتراض)
    context_classifier = ContextualClassifier(model_path="models/classifier_model.pkl")
    
    print("[INIT SUCCESS]: تم تهيئة جميع المكونات الأساسية.")

except Exception as e:
    print(f"[INIT ERROR]: فشل في تهيئة أحد المكونات. يرجى التحقق من المسارات والملفات: {e}")
    exit()

# --- وظيفة المحاكاة ---
def get_scenario_data(text: str) -> list[float]:
    """
    وظيفة محاكاة: تحول النص إلى متجه. 
    في التطبيق الحقيقي، تستخدم نموذج لغة طبيعية (NLP) مثل BERT.
    """
    # نرجع متجه وهمي (Mock Vector) لغرض التجربة
    # (يمكنك تغيير هذه الأرقام لمحاكاة سيناريوهات مختلفة)
    np.random.seed(hash(text) % (2**32 - 1)) # لتوليد نتائج شبه ثابتة لنفس النص
    vector = np.random.rand(INPUT_DIM).tolist()
    
    # محاكاة تأثير النص على المتجه لبعض السيناريوهات المعروفة
    if "سرية" in text or "بيانات" in text:
        # لمحاكاة سيناريو الخصوصية حيث تكون درجة الواجب عالية
        vector[0:10] = [0.9] * 10
    elif "خسارة" in text or "جمهور" in text:
        # لمحاكاة سيناريو يتطلب منفعة جماعية
        vector[10:20] = [0.1] * 10
        
    return vector

def run_analysis(scenario_text: str):
    """إجراء التحليل الكامل على سيناريو معين وإظهار المخرجات."""
    print("\n" + "=" * 80)
    print(f"** بدء تحليل السيناريو: {scenario_text[:70]}...")
    
    # 1. إعداد البيانات
    scenario_vector = get_scenario_data(scenario_text)
    
    # 2. تصنيف السياق
    context = context_classifier.classify(scenario_text)
    print(f"\n[1] السياق المصنف (Context): {context}")
    
    # 3. توليد النتائج الأولية
    scores = ethical_model.predict(scenario_vector)
    print(f"[2] الدرجات الأولية للشبكات: UtiliNet: {scores['UtiliNet']:.4f}, DeontoNet: {scores['DeontoNet']:.4f}, VirtuNet: {scores['VirtuNet']:.4f}")
    
    # 4. توليد الأسئلة الاستجوابية (يشمل تطبيق الأوزان السياقية)
    questions = inference_engine.generate_questions(scores, context)
    
    print("\n[3] الأسئلة الاستجوابية المقترحة (القرار الحيادي):\n")
    for i, q in enumerate(questions):
        print(f"    - السؤال {i+1}: {q}")
    print("=" * 80)

# --- أمثلة تشغيلية ---
if __name__ == "__main__":
    
    # السيناريو 1: تعارض بين الواجب (القاعدة) والمنفعة (النتيجة)
    scenario_1 = (
        "اكتشفت الشركة خطأ محاسبيًا صغيرًا يمكن إخفاؤه بسهولة. "
        "الكشف عنه الآن سيتسبب في انخفاض حاد في أسعار الأسهم "
        "ويضر بآلاف الموظفين، بينما الإخفاء يضمن الاستقرار المالي."
    )
    run_analysis(scenario_1)

    # السيناريو 2: سيناريو يركز على الخصوصية (يجب أن يعزز DeontoNet)
    scenario_2 = (
        "هل يجب استخدام بيانات المستخدمين غير المشفرة لتحسين خوارزمية "
        "إعلانية جديدة، بالرغم من أن سياسة الخصوصية تحظر استخدام هذه البيانات؟"
    )
    run_analysis(scenario_2)
