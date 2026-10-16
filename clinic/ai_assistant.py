# A small, explainable ML assistant using TF-IDF (scikit-learn).
# It recommends a specialty, not a diagnosis or medical advice.
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SPECIALTIES = {
    'Orthopedics': 'bone joint knee shoulder back injury fracture muscle pain عظام مفاصل ركبة ظهر كسر',
    'Dermatology': 'skin rash acne itching eczema hair جلد طفح حبوب حكة',
    'Cardiology': 'heart chest heartbeat cardiovascular قلب خفقان صدر',
    'Ophthalmology': 'eyes vision glasses eye irritation عيون نظر',
    'Dentistry': 'teeth tooth gum dental أسنان لثة',
    'General Medicine': 'general checkup fever cough routine visit فحص عام حرارة سعال',
}

def suggest_specialty(message,available_names):
    names=[name for name in available_names if name in SPECIALTIES]
    if not message.strip() or not names: return None
    corpus=[SPECIALTIES[name] for name in names]
    vectorizer=TfidfVectorizer(ngram_range=(1,2),lowercase=True)
    matrix=vectorizer.fit_transform(corpus+[message])
    similarities=cosine_similarity(matrix[-1],matrix[:-1])[0]
    best=int(similarities.argmax())
    return names[best] if similarities[best] > 0.03 else None
