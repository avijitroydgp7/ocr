import re

class AITeacher:
    """
    An Advanced AI Teaching class that analyzes the OCR text,
    breaks down complex concepts, and acts as a virtual tutor.
    """
    def __init__(self):
        self.complex_words_db = {
            "tensorflow": "An open-source machine learning framework created by Google.",
            "ocr": "Optical Character Recognition - teaching computers to read text from images.",
            "algorithm": "A step-by-step set of instructions a computer follows to solve a problem.",
            "intelligence": "The ability to acquire and apply knowledge and skills.",
            "machine": "An apparatus using mechanical power to perform a particular task."
        }

    def analyze_and_teach(self, text: str) -> dict:
        """
        Analyzes the given text and generates an educational breakdown.
        Returns a dictionary containing the lesson plan.
        """
        if not text or text == "No text detected.":
            return {
                "summary": "I couldn't find any readable text. Try getting closer to the camera or using a clearer image.",
                "vocabulary": [],
                "lesson": "Make sure the text is well-lit and in focus!"
            }

        words = re.findall(r'\b\w+\b', text.lower())
        unique_words = set(words)
        
        # 1. Vocabulary Extraction
        found_complex = {}
        for w in unique_words:
            if w in self.complex_words_db:
                found_complex[w.capitalize()] = self.complex_words_db[w]
            elif len(w) > 8:
                found_complex[w.capitalize()] = "This is a complex word. Try breaking it down into syllables to read it!"

        # 2. Reading Level Estimation (Mock logic for demonstration)
        avg_word_length = sum(len(w) for w in words) / max(1, len(words))
        if avg_word_length > 6:
            level = "Advanced (High School/College)"
        elif avg_word_length > 4:
            level = "Intermediate (Middle School)"
        else:
            level = "Beginner (Elementary)"

        # 3. Lesson Generation
        lesson = f"📚 **AI Tutor Analysis**\n\n"
        lesson += f"**Reading Level:** {level}\n"
        lesson += f"**Word Count:** {len(words)} words\n\n"
        
        if found_complex:
            lesson += "**📖 Vocabulary Focus:**\n"
            for word, meaning in found_complex.items():
                lesson += f"- **{word}**: {meaning}\n"
        else:
            lesson += "Great job! This text looks straightforward and easy to read. Keep practicing!\n"
            
        return {
            "summary": "Text successfully parsed.",
            "vocabulary": found_complex,
            "lesson": lesson
        }