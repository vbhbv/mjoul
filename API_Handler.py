# API_Handler.py
# واجهة FastAPI النهائية مع إعدادات CORS لحل مشكلة الاتصال

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware # تم إضافة استيراد CORS
from pydantic import BaseModel
from EthiCore import EthicalNetsModel, InferenceEngine, ContextualClassifier
import numpy as np
import os

# --- الإعدادات العامة ---
INPUT_DIM = 256 

# --- تهيئة المكونات (يجب أن تعمل الآن بعد نجاح البناء) ---
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(BASE_DIR, "config")
    
    ethical_model = EthicalNetsModel(input_dim=INPUT_DIM)
    inference_engine = InferenceEngine(config_path=CONFIG_PATH)
    context_classifier = ContextualClassifier()
    
    print("[INIT SUCCESS]: تم تهيئة جميع المكونات الأساسية.")
except Exception as e:
    print(f"[INIT ERROR]: فشل في تهيئة نموذج الذكاء الاصطناعي: {e}")
    # ترك التطبيق يعمل حتى لو فشل النموذج لتجنب فشل Render
    pass 

app = FastAPI(
    title="المساعد الأخلاقي المحايد", 
    description="نظام توليد أسئلة استجوابية للقرارات الأخلاقية المعقدة (Ethical AI Assistant)."
)

# --- إعدادات CORS: السماح لنطاق GitHub Pages بالوصول ---
origins = [
    "http://127.0.0.1:8000",       # للتشغيل المحلي
    "https://mjoul.onrender.com",  # رابط خادم Render
    "https://vbhbv.github.io",     # رابط GitHub Pages (أساسي لحل مشكلة الاتصال)
    "https://vbhbv.github.io/mjoul" # قد تحتاج إلى مسار المشروع
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # استخدام قائمة النطاقات المحددة
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- خدمة الملفات الثابتة (CSS) ---
FRONTEND_STATIC_DIR = os.path.join(BASE_DIR, "frontend")

# ملاحظة: تم حذف مجلد 'frontend/'، ولكننا نستخدمه هنا لخدمة CSS.
# إذا كان ملف style.css موجود في الجذر حالياً (كما في الصورة 1000023674.jpg)، 
# يجب تركه في مجلد 'frontend' مع التعديل المناسب في 'API_Handler.py'.
if os.path.isdir(FRONTEND_STATIC_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_STATIC_DIR), name="frontend_static")
else:
    print("تحذير: لم يتم العثور على مجلد 'frontend'. لن يتم تحميل ملفات CSS/JS بشكل صحيح.")

# --- تعريف بنية البيانات لطلب API ---
class Scenario(BaseModel):
    text: str
    vector: list[float] 

# --- نقطة نهاية تحليل السيناريو ---
@app.post("/analyze_scenario/")
async def analyze_scenario(scenario: Scenario):
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
        print(f"Internal Error in /analyze_scenario/: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"خطأ داخلي أثناء تحليل السيناريو. يرجى مراجعة سجلات الخادم."
        )

# --- نقطة نهاية خدمة الواجهة الأمامية (اختياري) ---
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """يخدم ملف index.html عند الوصول إلى المسار الجذر ('/')."""
    index_path = os.path.join(BASE_DIR, "index.html")

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return HTMLResponse("<h1>خطأ 404: لم يتم العثور على ملف الواجهة الأمامية (index.html).</h1>", status_code=404)
