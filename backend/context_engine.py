from typing import Dict, Any, List, Optional
from backend.models import Project, Chapter, Paragraph

class ContextEngine:
    """
    Hierarchical context intelligence engine that extracts project-level metadata,
    chapter emotional arcs, and sliding paragraph window context for consistent synthesis delivery.
    """

    def analyze_project_context(self, project: Project) -> Dict[str, Any]:
        return {
            "project_id": project.id,
            "title": project.title,
            "author": project.author,
            "genre": project.genre,
            "description": project.description,
            "total_chapters": len(project.chapters)
        }

    def analyze_chapter_context(self, chapter: Chapter) -> Dict[str, Any]:
        total_words = sum(len(p.text.split()) for p in chapter.paragraphs)
        return {
            "chapter_id": chapter.id,
            "title": chapter.title,
            "summary": chapter.summary,
            "paragraph_count": len(chapter.paragraphs),
            "total_words": total_words,
            "estimated_reading_minutes": round(total_words / 150.0, 1)
        }

    def get_paragraph_context_window(
        self,
        chapter: Chapter,
        paragraph_index: int,
        window_size: int = 1
    ) -> Dict[str, Any]:
        if paragraph_index < 0 or paragraph_index >= len(chapter.paragraphs):
            raise IndexError("Paragraph index out of bounds")

        target_paragraph = chapter.paragraphs[paragraph_index]

        start_prev = max(0, paragraph_index - window_size)
        prev_paragraphs = [p.text for p in chapter.paragraphs[start_prev:paragraph_index]]

        end_next = min(len(chapter.paragraphs), paragraph_index + window_size + 1)
        next_paragraphs = [p.text for p in chapter.paragraphs[paragraph_index + 1:end_next]]

        # Sentiment / Pacing heuristic
        word_count = len(target_paragraph.text.split())
        has_question = "?" in target_paragraph.text
        has_exclamation = "!" in target_paragraph.text

        pacing_directive = "standard narrative pacing"
        if word_count < 8:
            pacing_directive = "brief, energetic transition"
        elif word_count > 35:
            pacing_directive = "sustained long-form narrative clause"

        emotion_directive = "neutral dramatic delivery"
        if has_exclamation:
            emotion_directive = "high emotional intensity / emphasis"
        elif has_question:
            emotion_directive = "curious / inquisitive inflection"

        return {
            "paragraph_id": target_paragraph.id,
            "order": target_paragraph.order,
            "target_text": target_paragraph.text,
            "preceding_context": prev_paragraphs,
            "following_context": next_paragraphs,
            "pacing_directive": pacing_directive,
            "emotion_directive": emotion_directive
        }
