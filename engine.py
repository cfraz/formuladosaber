from collections import defaultdict


def grade_assessment(questions, answers):
    total = len(questions)
    correct = 0
    topic_totals = defaultdict(int)
    topic_correct = defaultdict(int)
    details = []
    for index, q in enumerate(questions, start=1):
        topic_totals[q["topic"]] += 1
        is_correct = answers.get(q["id"]) == q["answer"]
        if is_correct:
            correct += 1
            topic_correct[q["topic"]] += 1
        details.append({
            "number": index,
            "topic": q["topic"],
            "correct": is_correct,
            "selected": answers.get(q["id"]),
            "answer": q["answer"],
            "explanation": q["explanation"],
        })
    topic_scores = {
        topic: round(topic_correct[topic] / count * 100)
        for topic, count in topic_totals.items()
    }
    return {
        "total": total,
        "correct": correct,
        "percentage": round(correct / total * 100) if total else 0,
        "topic_scores": topic_scores,
        "details": details,
    }


def classify_topic_scores(scores):
    status = {}
    for topic, score in scores.items():
        if score >= 75:
            status[topic] = "Consolidado"
        elif score >= 50:
            status[topic] = "Em desenvolvimento"
        else:
            status[topic] = "Precisa de reforço"
    return status


def make_study_plan(scores, labels):
    recommendations = []
    for topic, score in sorted(scores.items(), key=lambda x: x[1]):
        if score < 50:
            recommendation = "retome os conceitos básicos e resolva exercícios guiados antes de avançar."
        elif score < 75:
            recommendation = "revise os exemplos e pratique questões de dificuldade intermediária."
        else:
            recommendation = "mantenha a revisão e avance para problemas contextualizados."
        recommendations.append({"topic": labels[topic], "recommendation": recommendation})
    return recommendations


def recommend_practice(bank, topic, grade, limit=3):
    eligible = [q for q in bank if q["topic"] == topic and q["year_min"] <= grade <= q["year_max"]]
    eligible.sort(key=lambda q: q.get("difficulty", 2))
    return eligible[:limit]
