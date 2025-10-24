
# EthiCore/ContextualWeighting.py
# يقوم بتطبيق الأوزان السياقية وقواعد التعارض على الدرجات الأخلاقية.

import yaml
import os

class ContextualWeighting:
    """
    يعدل الأوزان والعتبات والنتائج بناءً على السياق المصنف (Contextual Overrides).
    """
    def __init__(self, config_path="config"):
        # يجب أن تتطابق مسارات الملفات هنا مع موقع مجلد config
        self.thresholds = self._load_config(os.path.join(config_path, "thresholds.yaml"))
        self.conflict_rules = self._load_config(os.path.join(config_path, "conflict_rules.yaml"))
        
    def _load_config(self, filepath):
        """وظيفة مساعدة لتحميل ملفات YAML."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # استخدام إعدادات افتراضية في حال عدم العثور على الملف
            print(f"تحذير: لم يتم العثور على ملف الإعدادات: {filepath}. استخدام الافتراضيات.")
            return {}

    def apply_weighting(self, scores: dict, context: str) -> dict:
        """
        يطبق قواعد السياق على الدرجات الأولية للشبكات الثلاث.
        
        Args:
            scores (dict): الدرجات الأولية: {"UtiliNet": 0.X, "DeontoNet": 0.Y, "VirtuNet": 0.Z}
            context (str): السياق المصنف (مثل "privacy_scenario").
            
        Returns:
            dict: الدرجات المعدلة.
        """
        # الحصول على قواعد التجاوز الخاصة بهذا السياق
        context_overrides = self.conflict_rules.get("contextual_overrides", {}).get(context, {})
        
        # الحصول على التعزيزات (Boosts) المحددة
        boosts = context_overrides.get("threshold_boost", {})
        
        adjusted_scores = scores.copy()
        
        for net, boost_value in boosts.items():
            # تطبيق التعزيز على الشبكة المحددة في ملف config/
            if net in adjusted_scores:
                # يتم تطبيق التعزيز كضرب للأهمية أو إضافة لقيمة النتيجة (اخترنا الإضافة كمثال)
                adjusted_scores[net] += boost_value
                # التأكد من أن النتيجة لا تتجاوز 1
                adjusted_scores[net] = min(adjusted_scores[net], 1.0)

        # يمكن أيضاً تعديل الأوزان بشكل كامل هنا، لكن الإضافة هي طريقة بسيطة للـ "تغليب"
        
        print(f"[ContextualWeighting] تم تعديل الدرجات بناءً على السياق '{context}'.")
        return adjusted_scores

