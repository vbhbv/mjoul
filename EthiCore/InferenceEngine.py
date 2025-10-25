# EthiCore/InferenceEngine.py
# محرك الاستدلال: يجمع المخرجات ويولد أسئلة استجوابية بلغة مبسطة.

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
            
            # أسئلة مبسطة للعامة:
            if score < warning_threshold:
                questions.append(f"؟يبدو أن تحليل {net} غير واضح ({score:.2f}). ما هي الحقائق الجديدة التي قد تدعم هذا الجانب من التحليل؟")
            elif score < base_t:
                questions.append(f"؟تحليل {net} مقبول لكنه لم يصل بعد لقناعة كاملة. هل هناك عوامل تدعم رؤية {net} تستحق الاهتمام؟")

        # الخطوة 3: تحليل التعارضات
        if adjusted_scores:
            net_names = list(adjusted_scores.keys())
            
            if len(net_names) >= 3:
                max_net = max(adjusted_scores, key=adjusted_scores.get)
                min_net = min(adjusted_scores, key=adjusted_scores.get)
                max_score = adjusted_scores[max_net]
                min_score = adjusted_scores[min_net]
                
                if (max_score - min_score) > self.thresholds.get("conflict_difference_threshold", 0.35):
                    
                    context_rules = self.conflict_rules.get("contextual_overrides", {}).get(scenario_context, {})
                    priority_list = context_rules.get("priority", self.conflict_rules.get("default_priority", []))
                    
                    # أسئلة تعارض مبسطة:
                    if priority_list:
                         questions.append(
                            f"؟يوجد خلاف كبير بين رؤية {max_net} ورؤية {min_net}. قواعد الأزمة تُرَجِّح '{priority_list[0]}'. هل هناك سبب قهري لكسر هذه الأولوية في هذه الحالة تحديداً؟"
                        )
                    else:
                        questions.append(
                            f"؟التحليلات متناقضة (أعلى قيمة: {max_net}، أدنى قيمة: {min_net}). ما هي القيمة الأخلاقية التي يجب أن تُتَوّج كأولوية في هذا القرار؟"
                        )

        # الخطوة 4: توليد الأسئلة النهائية (إذا كانت الدرجات متوازنة)
        if not questions:
            questions.append("؟تبدو الخيارات متوازنة ومقبولة. ما هو القرار الذي تتوقع أن يكون له التأثير الإيجابي الأكبر على سمعة الشركة على مدار العشر سنوات القادمة؟")
            
        return questions
