import re
import docx
from io import BytesIO
from typing import Literal, Dict, TypedDict, Union
import xml.etree.ElementTree as ET
from docx.shared import RGBColor
from docx.enum.text import WD_COLOR_INDEX
from copy import deepcopy
from helpers.jisebi_evaluation import JISEBIEvaluation
from helpers.jisebi_document import JISEBIDocument

class JISEBIReporting:

    def __init__(self, evaluation:JISEBIEvaluation):
        self.jisebi_document:JISEBIDocument  = evaluation.jisebi_document  # Initialize the variable with the given value
        self.jisebi_evaluation:JISEBIEvaluation = evaluation.generate_overall_summary()

    def add_highlight(self, content_index, start_index, end_index, highlight_color=WD_COLOR_INDEX.YELLOW):
        """
        Add highlight to text in a specific paragraph at given character positions.
        
        Args:
            doc: The Document object
            content_index: Index of the paragraph containing the text
            start_index: Starting character position of text to highlight
            end_index: Ending character position of text to highlight
            highlight_color: Color to use for highlighting (default: YELLOW)
            
        Returns:
            True if successful, False otherwise
        """
        doc = self.jisebi_document.raw_document
        contents = self.contents
    # try:
        # Get the target paragraph
        if content_index >= len(contents):
            print(f"Paragraph index {content_index} is out of range")
            return False
            
        paragraph = contents[content_index]
        
        # Get the full text of the paragraph
        full_text = paragraph.text
        
        if start_index >= len(full_text) or end_index > len(full_text) or start_index > end_index:
            print(f"Invalid text positions: start={start_index}, end={end_index}, text length={len(full_text)}")
            return False
            
        # Get the text to highlight
        text_to_highlight = full_text[start_index:end_index]
        
        # Create a new paragraph with the same style
        new_paragraph = doc.add_paragraph()
        new_paragraph.style = paragraph.style
        
        # Copy any paragraph formatting
        new_paragraph.paragraph_format.alignment = paragraph.paragraph_format.alignment
        new_paragraph.paragraph_format.left_indent = paragraph.paragraph_format.left_indent
        new_paragraph.paragraph_format.right_indent = paragraph.paragraph_format.right_indent
        new_paragraph.paragraph_format.first_line_indent = paragraph.paragraph_format.first_line_indent
        new_paragraph.paragraph_format.line_spacing = paragraph.paragraph_format.line_spacing
        new_paragraph.paragraph_format.space_before = paragraph.paragraph_format.space_before
        new_paragraph.paragraph_format.space_after = paragraph.paragraph_format.space_after
        
        # Add text before the highlighted portion
        if start_index > 0:
            before_text = full_text[:start_index]
            before_run = new_paragraph.add_run(before_text)
            self.copy_run_formatting(paragraph, before_run)
            
        # Add the highlighted text
        highlight_run = new_paragraph.add_run(text_to_highlight)
        self.copy_run_formatting(paragraph, highlight_run)
        highlight_run.font.highlight_color = highlight_color
        
        # Add text after the highlighted portion
        if end_index < len(full_text):
            after_text = full_text[end_index:]
            after_run = new_paragraph.add_run(after_text)
            self.copy_run_formatting(paragraph, after_run)
            
        # Replace the original paragraph with our new one
        # p_index = doc.paragraphs.index(paragraph)
        p_element = paragraph._element
        new_p_element = new_paragraph._element
        p_element.getparent().replace(p_element, new_p_element)
        
        # Remove the extra paragraph we created
        self.remove_paragraph(doc.paragraphs[-1])
        
        return True
        
    # except Exception as e:
    #     print(f"Error while highlighting: {str(e)}")
    #     return False

    def copy_run_formatting(self, source_paragraph, target_run):
        """Copy formatting from the first run of source paragraph to target run."""
        try:
            # Get the first run with formatting or create default formatting
            source_run = None
            for run in source_paragraph.runs:
                if run.text.strip():
                    source_run = run
                    break
                    
            if source_run:
                # Copy font formatting
                if source_run.font.name:
                    target_run.font.name = source_run.font.name
                    
                if source_run.font.size:
                    target_run.font.size = source_run.font.size
                    
                target_run.font.bold = source_run.font.bold
                target_run.font.italic = source_run.font.italic
                target_run.font.underline = source_run.font.underline
                
                if source_run.font.color.rgb:
                    target_run.font.color.rgb = source_run.font.color.rgb
        except:
            # If any error occurs, just continue with default formatting
            pass

    def remove_paragraph(self, paragraph):
        """Remove a paragraph from the document."""
        p = paragraph._element
        p.getparent().remove(p)
        paragraph._p = paragraph._element = None

    def highlight_word(self, content_index, word, highlight_color=WD_COLOR_INDEX.YELLOW, occurrence=0):
        """
        Highlight a specific word in a paragraph.
        
        Args:
            doc: The Document object
            content_index: Index of the paragraph containing the word
            word: The word to highlight
            highlight_color: Color to use for highlighting
            occurrence: Which occurrence of the word to highlight (0 for first, 1 for second, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc = self.jisebi_document.raw_document
            paragraph = doc.paragraphs[content_index]
            text = paragraph.text
            
            # Find the word in the text
            start_pos = -1
            for i in range(occurrence + 1):
                start_pos = text.find(word, start_pos + 1)
                if start_pos == -1:
                    print(f"Word '{word}' (occurrence {occurrence}) not found in paragraph {content_index}")
                    return False
                    
            end_pos = start_pos + len(word)
            
            # Highlight the word
            return self.add_highlight(doc, content_index, start_pos, end_pos, highlight_color)
            
        except Exception as e:
            print(f"Error in highlight_word: {str(e)}")
            return False

    def export_document(self, path:str):
        self.jisebi_document.raw_document.save(path)