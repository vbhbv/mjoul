# API_Handler.py
# واجهة FastAPI للنشر السحابي، تخدم الآن كلاً من API والموقع العام.

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles # لاستضافة ملفات الواجهة الأمامية
from pydantic import BaseModel
from EthiCore import EthicalNetsModel, InferenceEngine, ContextualClassifier
import numpy as np
import os

# --- الإعدادات العامة ---
# يجب أن يتطابق حجم المتجه (Embedding) مع حجم الإدخال في EthicalNetsModel
INPUT_DIM = 256 

# --- تهيئة المكونات (يتم مرة واحدة عند بدء تشغيل الخادم) ---
try:
    ethical_model = EthicalNetsModel(input_dim=INPUT_DIM)
    inference_engine = InferenceEngine(config_path="config")
    context_classifier = ContextualClassifier()
except Exception as e:
    print(f"فشل تهيئة نموذج الذكاء الاصطناعي: {e}")
    # إيقاف الخادم في حالة الفشل الحرج
    raise SystemExit("فشل بدء التشغيل بسبب خطأ في تحميل النماذج أو الإعدادات.")

app = FastAPI(
    title="المساعد الأخلاقي المحايد", 
    description="نظام توليد أسئلة استجوابية للقرارات الأخلاقية المعقدة (Ethical AI Assistant)."
)

# --- خدمة الملفات الثابتة (الواجهة الأمامية) ---
# التأكد من وجود مجلد الواجهة الأمامية
if os.path.isdir("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="frontend")
else:
    print("تحذير: لم يتم العثور على مجلد 'frontend'. لن تظهر واجهة الموقع.")

# --- تعريف بنية البيانات لطلب API ---
class Scenario(BaseModel):
    """بنية البيانات المطلوبة في طلب API (النص والمتجه)."""
    text: str
    vector: list[float] 

# --- نقطة نهاية (Endpoint) تحليل السيناريو ---
@app.post("/analyze_scenario/")
async def analyze_scenario(scenario: Scenario):
    """نقطة نهاية API تستقبل البيانات وتعيد التحليل الأخلاقي."""
    if len(scenario.vector) != INPUT_DIM:
        raise HTTPException(
            status_code=422, 
            detail=f"حجم المتجه غير صحيح. المتوقع: {INPUT_DIM}, الوارد: {len(scenario.vector)}"
        )
        
    try:
        context = context_classifier.classify(scenario.text)
        scores = ethical_model.predict(scenario.vector)
        questions = inference_engine.generate_questions(scores, context)
        
        return {
            "status": "success",
            "context_classification": context,
            "ethical_scores": scores,
            "neutral_questions": questions
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"خطأ داخلي أثناء تحليل السيناريو: {str(e)}"
        )

# --- نقطة نهاية (Endpoint) خدمة الواجهة الأمامية ---
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """يخدم ملف index.html عند الوصول إلى المسار الجذر ('/')."""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return HTMLResponse("<h1>خطأ 404: لم يتم العثور على ملف الواجهة الأمامية (index.html).</h1>", status_code=404)

# ملاحظة: لتشغيل هذا الملف، استخدم الأمر: uvicorn API_Handler:app --reload
