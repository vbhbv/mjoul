# API_Handler.py
# واجهة FastAPI المحدثة لخدمة الموقع العام (index.html من الجذر).

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from EthiCore import EthicalNetsModel, InferenceEngine, ContextualClassifier
import numpy as np
import os

# --- الإعدادات العامة ---
INPUT_DIM = 256 

# --- تهيئة المكونات (يتم مرة واحدة عند بدء تشغيل الخادم) ---
try:
    # تحديد المسار الحالي للملف (للوصول الآمن إلى config/)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(BASE_DIR, "config")
    
    ethical_model = EthicalNetsModel(input_dim=INPUT_DIM)
    inference_engine = InferenceEngine(config_path=CONFIG_PATH)
    context_classifier = ContextualClassifier() # يفترض تحميل النماذج من 'models/'
    
    print("[INIT SUCCESS]: تم تهيئة جميع المكونات الأساسية.")
except Exception as e:
    print(f"[INIT ERROR]: فشل في تهيئة نموذج الذكاء الاصطناعي: {e}")
    raise SystemExit("فشل بدء التشغيل بسبب خطأ في تحميل النماذج أو الإعدادات.")

app = FastAPI(
    title="المساعد الأخلاقي المحايد", 
    description="نظام توليد أسئلة استجوابية للقرارات الأخلاقية المعقدة (Ethical AI Assistant)."
)

# --- خدمة الملفات الثابتة (CSS, JS) ---
FRONTEND_STATIC_DIR = os.path.join(BASE_DIR, "frontend")

if os.path.isdir(FRONTEND_STATIC_DIR):
    # مسار /static/ سيخدم الملفات داخل مجلد 'frontend'
    app.mount("/static", StaticFiles(directory=FRONTEND_STATIC_DIR), name="frontend_static")
else:
    print("تحذير: لم يتم العثور على مجلد 'frontend'. لن يتم تحميل ملفات CSS/JS بشكل صحيح.")

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
        # تسجيل الخطأ الداخلي للمساعدة في التصحيح
        print(f"Internal Error in /analyze_scenario/: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"خطأ داخلي أثناء تحليل السيناريو. يرجى مراجعة سجلات الخادم."
        )

# --- نقطة نهاية (Endpoint) خدمة الواجهة الأمامية ---
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """يخدم ملف index.html عند الوصول إلى المسار الجذر ('/')."""
    
    # المسار الكامل لملف index.html (يفترض أنه في جذر المشروع الآن)
    index_path = os.path.join(BASE_DIR, "index.html")

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        # رسالة خطأ إذا لم يتم العثور على ملف الواجهة
        return HTMLResponse("<h1>خطأ 404: لم يتم العثور على ملف الواجهة الأمامية (index.html). تأكد من وجوده في جذر المشروع.</h1>", status_code=404)
        
