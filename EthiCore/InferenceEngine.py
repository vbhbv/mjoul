
# EthiCore/InferenceEngine.py
# محرك الاستدلال: يولد أسئلة استجوابية بدلاً من قرارات نهائية.

import yaml
import os

class InferenceEngine:
    """
    يجمع مخرجات الشبكات الأخلاقية ويولد أسئلة استجوابية للمستخدم.
    يعتمد على ملفات config للحيادية والتحكم.
    """
    def __init__(self, config_path="config"):
        # تحميل الإعدادات من ملفات YAML
        self.thresholds = self._load_config(os.path.join(config_path, "thresholds.yaml"))
        self.conflict_rules = self._load_config(os.path.join(config_path, "conflict_rules.yaml"))
        
    def _load_config(self, filepath):
        """وظيفة مساعدة لتحميل ملفات YAML."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"خطأ: لم يتم العثور على ملف الإعدادات: {filepath}")
            return {}
        
    def generate_questions(self, scores: dict, scenario_context: str) -> list:
        """يولد قائمة من الأسئلة بناءً على نتائج الشبكات والسياق."""
        questions = []
        
        # 1. تحديد الأولوية والعتبات بناءً على السياق
        context_rules = self.conflict_rules.get("contextual_overrides", {}).get(scenario_context, {})
        
        # 2. تقييم مدى اليقين (Confidence Check)
        for net, score in scores.items():
            threshold = self.thresholds.get("base_thresholds", {}).get(net, 0.75) # افتراضي
            
            if score < self.thresholds.get("warning_threshold", 0.5):
                questions.append(f"؟ما هي المعلومات الإضافية التي قد تزيد من اليقين بخصوص تحليل {net}؟")
            elif score < threshold:
                questions.append(f"؟بالرغم من عدم اليقين، هل يمكن ترجيح تحليل {net} لكونه يقدم رؤية {net}؟")

        # 3. تحليل التعارضات (Conflict Analysis)
        scores_list = list(scores.values())
        max_score = max(scores_list)
        min_score = min(scores_list)
        
        if (max_score - min_score) > self.thresholds.get("conflict_difference_threshold", 0.35):
            
            # تحديد الشبكات المتعارضة
            net_max = [n for n, s in scores.items() if s == max_score][0]
            net_min = [n for n, s in scores.items() if s == min_score][0]
            
            questions.append(
                f"؟يوجد تعارض حاد بين تحليل {net_max} و {net_min}. ما هي الأولوية التي يجب تطبيقها في هذا السياق: الواجب أم المنفعة أم الفضيلة؟"
            )
            
            # تطبيق قاعدة الأولوية السياقية
            priority_list = context_rules.get("priority", self.conflict_rules.get("default_priority", []))
            
            if priority_list:
                questions.append(
                    f"؟بناءً على السياق {scenario_context}، تقترح قواعد الأولوية التركيز على {priority_list[0]}. هل هذا الترتيب يتماشى مع قيم المؤسسة؟"
                )

        # 4. توليد الأسئلة النهائية (Reflective Questions)
        if not questions:
            questions.append("؟تبدو الخيارات متوازنة. ما هو المبدأ الأخلاقي الذي تراه الأكثر أهمية لسمعة الشركة على المدى الطويل؟")

        return questions
