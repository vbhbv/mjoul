# EthiCore/InferenceEngine.py
# محرك الاستدلال: يولد أسئلة استجوابية بناءً على الدرجات المعدلة (بما في ذلك الأوزان السياقية).

import yaml
import os

class InferenceEngine:
    """
    يجمع مخرجات الشبكات الأخلاقية ويولد أسئلة استجوابية للمستخدم.
    يطبق التحكم الخارجي (Weighting and Conflict Resolution).
    """
    def __init__(self, config_path="config"):
        # بناء المسار الآمن لملفات الإعدادات
        thresholds_path = os.path.join(config_path, "thresholds.yaml")
        conflict_rules_path = os.path.join(config_path, "conflict_rules.yaml")
        
        self.thresholds = self._load_config(thresholds_path)
        self.conflict_rules = self._load_config(conflict_rules_path)
        
    def _load_config(self, filepath):
        """وظيفة مساعدة لتحميل ملفات YAML."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # رسالة خطأ واضحة إذا فشل تحميل الإعدادات
            print(f"خطأ: لم يتم العثور على ملف الإعدادات: {filepath}. استخدام الإعدادات الافتراضية.")
            return {}
        
    def _apply_weighting(self, scores: dict, context: str) -> dict:
        """يطبق قواعد الأوزان السياقية (Contextual Overrides)."""
        adjusted_scores = scores.copy()
        context_overrides = self.conflict_rules.get("contextual_overrides", {}).get(context, {})
        boosts = context_overrides.get("threshold_boost", {})
        
        for net, boost_value in boosts.items():
            if net in adjusted_scores:
                adjusted_scores[net] += boost_value
                adjusted_scores[net] = min(adjusted_scores[net], 1.0) # لا تتجاوز 1
        
        return adjusted_scores

    def generate_questions(self, scores: dict, scenario_context: str) -> list:
        """يولد قائمة من الأسئلة بناءً على نتائج الشبكات والسياق."""
        
        # الخطوة 1: تطبيق الأوزان السياقية
        adjusted_scores = self._apply_weighting(scores, scenario_context)
        questions = []
        
        # الخطوة 2: تقييم مدى اليقين (Confidence Check)
        base_thresholds = self.thresholds.get("base_thresholds", {})
        warning_threshold = self.thresholds.get("warning_threshold", 0.5)

        for net, score in adjusted_scores.items():
            base_t = base_thresholds.get(net, 0.75)
            
            if score < warning_threshold:
                questions.append(f"؟درجة اليقين في تحليل {net} منخفضة ({score:.2f}). ما هي المعلومات التي قد تعزز هذا الجانب؟")
            elif score < base_t:
                questions.append(f"؟بالرغم من أن {net} لم يتجاوز عتبة التفعيل، هل يمكن ترجيحه لكونه يقدم رؤية {net}؟")

        # الخطوة 3: تحليل التعارضات
        if adjusted_scores:
            net_names = list(adjusted_scores.keys())
            
            # (نحتاج لثلاث شبكات على الأقل لتحليل التعارض)
            if len(net_names) >= 3:
                # العثور على الحد الأقصى والحد الأدنى للدرجات
                max_net = max(adjusted_scores, key=adjusted_scores.get)
                min_net = min(adjusted_scores, key=adjusted_scores.get)
                max_score = adjusted_scores[max_net]
                min_score = adjusted_scores[min_net]
                
                if (max_score - min_score) > self.thresholds.get("conflict_difference_threshold", 0.35):
                    
                    # استخدام قواعد الأولوية لتوجيه السؤال
                    context_rules = self.conflict_rules.get("contextual_overrides", {}).get(scenario_context, {})
                    priority_list = context_rules.get("priority", self.conflict_rules.get("default_priority", []))
                    
                    # إذا كانت هناك أولوية محددة
                    if priority_list:
                         questions.append(
                            f"؟يوجد تعارض حاد بين {max_net} و {min_net}. الأولوية المحددة في '{scenario_context}' هي '{priority_list[0]}'. هل يجب تجاوز هذه الأولوية في هذه الحالة تحديداً؟"
                        )
                    else:
                        questions.append(
                            f"؟هناك تعارض كبير بين {max_net} و {min_net}. ما هي الإطار الأخلاقي الذي يجب أن يسود لضمان قرار عادل؟"
                        )

        # الخطوة 4: توليد الأسئلة النهائية
        if not questions:
            questions.append("؟تبدو الخيارات متوازنة ومقبولة. ما هو القرار الذي تتوقع أن يكون له التأثير الإيجابي الأكبر على سمعة الشركة على مدار العشر سنوات القادمة؟")
            
        return questions
      
