# API_Handler.py
# واجهة FastAPI للنشر السحابي التلقائي والربط الخارجي.

from fastapi import FastAPI
from pydantic import BaseModel
from EthiCore import EthicalNetsModel, InferenceEngine, ContextualClassifier

# إنشاء مثيلات للمكونات الأساسية
# ملاحظة: يجب تعديل 'input_dim' ليناسب حجم متجه المدخل الفعلي
INPUT_DIM = 256 # افتراض حجم المتجه
ethical_model = EthicalNetsModel(input_dim=INPUT_DIM)
inference_engine = InferenceEngine()
context_classifier = ContextualClassifier()

app = FastAPI(
    title="المساعد الأخلاقي المحايد", 
    description="نظام توليد أسئلة استجوابية للقرارات الأخلاقية المعقدة."
)

class Scenario(BaseModel):
    """بنية البيانات المطلوبة في طلب API."""
    text: str # السيناريو النصي (مثل: 'قرار إطلاق محتوى مثير للجدل...')
    vector: list # تمثيل المتجه (Embedding) للسيناريو (للتسهيل)

@app.post("/analyze_scenario/")
async def analyze_scenario(scenario: Scenario):
    """
    نقطة نهاية (Endpoint) لاستقبال سيناريو وإرجاع تحليل حيادي مُدقق.
    """
    try:
        # 1. تصنيف السياق
        context = context_classifier.classify(scenario.text)
        
        # 2. توليد النتائج من الشبكات الثلاث
        scores = ethical_model.predict(scenario.vector)
        
        # 3. توليد الأسئلة الاستجوابية
        questions = inference_engine.generate_questions(scores, context)
        
        return {
            "status": "success",
            "context_classification": context,
            "ethical_scores": scores,
            "neutral_questions": questions
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "ethical_scores": None
        }

# لتشغيل التطبيق (في البيئة المحلية):
# uvicorn API_Handler:app --reload
