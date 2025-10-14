from io import BytesIO
from typing import IO, Dict
import xml.etree.ElementTree as ET
from docx.shared import RGBColor
from docx.enum.text import WD_COLOR_INDEX
from src.document_processing.helpers.jisebi_evaluation import JISEBIEvaluation
from src.document_processing.helpers.jisebi_document import JISEBIDocument
from jinja2 import Template
from typing import Dict
from datetime import datetime
import pdfkit
from PyPDF2 import PdfMerger
import random
import traceback
import string
import os
from src.core.config import get_settings, Settings

def load_template_from_html(filename: str) -> Template:
    html_path = os.path.join(os.getcwd(), filename)
    with open(html_path, "r", encoding="utf-8") as f:
        template_str = f.read()
    return Template(template_str)

class JISEBIReporting:

    def __init__(self, evaluation:JISEBIEvaluation):
        self.jisebi_document:JISEBIDocument  = evaluation.jisebi_document  # Initialize the variable with the given value
        self.jisebi_evaluation: JISEBIEvaluation = evaluation
        self.jisebi_report: Dict = None

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
        contents = self.jisebi_document.contents
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
            
        # # Get the text to highlight
        # text_to_highlight = full_text[start_index:end_index]
        
        # # Create a new paragraph with the same style
        # new_paragraph = doc.add_paragraph()
        # new_paragraph.style = paragraph.style
        
        # # Copy any paragraph formatting
        # new_paragraph.paragraph_format.alignment = paragraph.paragraph_format.alignment
        # new_paragraph.paragraph_format.left_indent = paragraph.paragraph_format.left_indent
        # new_paragraph.paragraph_format.right_indent = paragraph.paragraph_format.right_indent
        # new_paragraph.paragraph_format.first_line_indent = paragraph.paragraph_format.first_line_indent
        # new_paragraph.paragraph_format.line_spacing = paragraph.paragraph_format.line_spacing
        # new_paragraph.paragraph_format.space_before = paragraph.paragraph_format.space_before
        # new_paragraph.paragraph_format.space_after = paragraph.paragraph_format.space_after
        
        # # Add text before the highlighted portion
        # if start_index > 0:
        #     before_text = full_text[:start_index]
        #     before_run = new_paragraph.add_run(before_text)
        #     self.copy_run_formatting(paragraph, before_run)
            
        # # Add the highlighted text
        # highlight_run = new_paragraph.add_run(text_to_highlight)
        # self.copy_run_formatting(paragraph, highlight_run)
        # highlight_run.font.highlight_color = highlight_color
        
        # # Add text after the highlighted portion
        # if end_index < len(full_text):
        #     after_text = full_text[end_index:]
        #     after_run = new_paragraph.add_run(after_text)
        #     self.copy_run_formatting(paragraph, after_run)
            
        # # Replace the original paragraph with our new one
        # # p_index = doc.paragraphs.index(paragraph)
        # p_element = paragraph._element
        # new_p_element = new_paragraph._element
        
        # parent = p_element.getparent()

        # if parent is None:
        #     print("p_element has no parent. Attempting to locate or reattach...")

        #     # Find the parent manually within the document tree
        #     root = p_element.getroottree()
        #     parent = root.getroot()

        #     if parent is not None:
        #         print("Reattached p_element to the tree.")
        #         parent.append(p_element)  # Temporarily reattach it
        #     else:
        #         print("Could not find a suitable parent. Aborting operation.")
        #         return

        # if parent is not None:
        #     parent.replace(p_element, new_p_element)
        #     # Remove the extra paragraph we created
        #     self.remove_paragraph(doc.paragraphs[-1])

        # else:
        #     print("Could not find or reattach the parent. Skipping replacement.")

        # Track character positions
        char_pos = 0
        for run in paragraph.runs:
            run_text_len = len(run.text)
            run_start = char_pos
            run_end = char_pos + run_text_len

            # Check if this run overlaps with the highlight range
            overlap_start = max(run_start, start_index)
            overlap_end = min(run_end, end_index)

            if overlap_start < overlap_end:
                # If the run is fully within the highlight range, just highlight it
                if run_start >= start_index and run_end <= end_index:
                    run.font.highlight_color = highlight_color
                else:
                    # If only part of the run is in the range, split the run
                    before = run.text[:overlap_start - run_start]
                    highlight = run.text[overlap_start - run_start:overlap_end - run_start]
                    after = run.text[overlap_end - run_start:]

                    # Replace the run with three runs: before, highlight, after
                    run.text = before
                    highlight_run = paragraph.add_run(highlight)
                    highlight_run.font.highlight_color = highlight_color
                    self.copy_run_formatting(run, highlight_run)
                    after_run = paragraph.add_run(after)
                    self.copy_run_formatting(run, after_run)
            char_pos += run_text_len

        return True

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

    def export_document(self, path:str | IO[BytesIO]):
        self.jisebi_document.raw_document.save(path)

    async def set_report(self): 
        self.jisebi_report = await self.jisebi_evaluation.generate_overall_summary()

    async def generate_report(self, path: str | bool) -> IO[BytesIO]:

        document = self.jisebi_document

        if self.jisebi_report == None:
            await self.set_report()
        
        report = self.jisebi_report

        for key, data in report.items():
            # paragraph = document.introduction["object"][key]
            if key == 'semantic' or key == 'novelty':
                continue
                
            if data['section_issue']['sequence'] != []:
                obj_index = getattr(document, key)["index"]["first"]
                paragraph_start = 0
                paragraph_end = len(getattr(document, key)["heading"]["content"])
                self.add_highlight(obj_index, paragraph_start, paragraph_end, WD_COLOR_INDEX.YELLOW)
            
            if key in ['title', 'introduction', 'method', 'result', 'discussion', 'conclusion', 'references', 'literature_review']:
                
                if "heading" in data:
                    if data['heading'] != {}:
                        for paragraph_index, issue in data["heading"].items():

                            if "index" in getattr(document, key):
                                obj_index = getattr(document, key)["index"]["first"] + int(paragraph_index)

                            if "heading" in getattr(document, key):
                                obj_index = getattr(document, key)["heading"]["index"]["first"] + int(paragraph_index)
                            
                            if issue["paragraph_issues"] != {}:
                                paragraph_start = 0
                                paragraph_end = len(self.jisebi_document.contents[obj_index].text)
                                self.add_highlight(obj_index, paragraph_start, paragraph_end, WD_COLOR_INDEX.RED)

                            if issue["run_issues"] != []:

                                paragraph = self.jisebi_document.contents[obj_index]
                                
                                for run_issue in issue["run_issues"]:
                                    run_index = run_issue["run_index"]
                                    run = paragraph.runs[run_index]
                                    run.font.highlight_color = WD_COLOR_INDEX.RED

                if "body" in data:
                    if data["body"] != {}:
                        for paragraph_index, issue in data["body"].items():

                            if "index" in getattr(document, key):
                                obj_index = getattr(document, key)["index"]["first"] + int(paragraph_index)

                            if "paragraph" in getattr(document, key):
                                obj_index = getattr(document, key)["paragraph"]["index"]["first"] + int(paragraph_index)
                            
                            if issue["paragraph_issues"] != {}:
                                paragraph_start = 0
                                paragraph_end = len(self.jisebi_document.contents[obj_index].text)
                                self.add_highlight(obj_index, paragraph_start, paragraph_end, WD_COLOR_INDEX.RED)

                            if issue["run_issues"] != []:

                                paragraph = self.jisebi_document.contents[obj_index]
                                
                                for run_issue in issue["run_issues"]:
                                    run_index = run_issue["run_index"]
                                    run = paragraph.runs[run_index]
                                    run.font.highlight_color = WD_COLOR_INDEX.RED

                # obj_index = getattr(document, key)["index"]["first"]
                # paragraph_start = 0
                # paragraph_end = len(getattr(document, key)["heading"]["content"])
                # self.add_highlight(obj_index, paragraph_start, paragraph_end, WD_COLOR_INDEX.RED)

        if (path == False):
            file_stream = BytesIO()
            self.export_document(file_stream)
            file_stream.seek(0)
            return file_stream
        else:
            self.export_document(path)
            return "exported"

    
            # if data.heading != {}:

            # if data.sequence != {}:

        #     processed_runs = set()

        #     for issue_data in data['issues']:
        #         run_index = issue_data.get('run_index')
        #         if run_index is None or run_index in processed_runs:
        #             continue
                    
        #         # Make sure run_index is valid
        #         if run_index >= len(paragraph.runs):
        #             print(f"Run index {run_index} is out of range for paragraph {para_index}")
        #             continue
                    
        #         # Add highlight to the run
        #         run = paragraph.runs[run_index]
        #         run.font.highlight_color = WD_COLOR_INDEX.YELLOW
                
        #         highlighted_count += 1
        #         processed_runs.add(run_index)

        # for key, data in structural_report.items():
        #     obj_index = getattr(newDoc, key)["index"]["first"]
        #     paragraph_start = 0
        #     paragraph_end = len(getattr(newDoc, key)["heading"]["content"])
        #     newDoc.add_highlight(obj_index, paragraph_start, paragraph_end, WD_COLOR_INDEX.RED)

    async def generate_dashboard_html(self) -> str:
        """
        Generate an A4-sized HTML dashboard from the supplied JSON report data.
        
        Args:
            report_data: Dictionary containing paper structure and issues
            
        Returns:
            String containing HTML for the dashboard
        """
        
        # Extract and prepare the data

        if self.jisebi_report == None:
            await self.set_report()

        report_data = self.jisebi_report

        sections_with_issues = []
        total_issues = 0
        
        for section_name, section_data in report_data.items():
            section_issues = {
                "name": section_name.replace("_", " ").title(),
                "not_found": [],
                "sequence": [],
                "body_issues": 0,
                "style_issues": 0
            }
            
            # Check section level issues
            if section_name == "semantic" or section_name == "novelty":
                continue
            if "section_issue" in section_data:
                if "not_found" in section_data["section_issue"] and section_data["section_issue"]["not_found"] and section_name != "literature_review":
                    section_issues["not_found"] = section_data["section_issue"]["not_found"]
                    # total_issues += len(section_data["section_issue"]["not_found"])
                
                if "sequence" in section_data["section_issue"] and section_data["section_issue"]["sequence"]:
                    section_issues["sequence"] = section_data["section_issue"]["sequence"]
                    # total_issues += len(section_data["section_issue"]["sequence"])
            
            # Check body issues (especially in references)
            if ("body" in section_data and isinstance(section_data["body"], dict)) or ("heading" in section_data and isinstance(section_data["heading"], dict)):
                style_issues = 0
                
                if "body" in section_data and isinstance(section_data["body"], dict):
                    for paragraph_id, paragraph_data in section_data["body"].items():
                        if "paragraph_issues" in paragraph_data:
                            if "style" in paragraph_data["paragraph_issues"]:
                                style_issues += 1
                                # total_issues += 1
                
                if "heading" in section_data and isinstance(section_data["heading"], dict):
                    for paragraph_id, paragraph_data in section_data["heading"].items():
                        if "paragraph_issues" in paragraph_data:
                            if "style" in paragraph_data["paragraph_issues"]:
                                style_issues += 1
                                # total_issues += 1
                
                if style_issues > 0:
                    section_issues["style_issues"] = style_issues
            
            # Only include sections that have issues
            if section_issues["not_found"] or section_issues["sequence"] or section_issues["style_issues"]:
                sections_with_issues.append(section_issues)
                total_issues += 1
        
        # Calculate section order issues
        section_order_issues = []
        for section_data in sections_with_issues:
            for seq_issue in section_data["sequence"]:
                section_order_issues.append(f"{section_data['name']}: {seq_issue}")
        
        # Get overall summary
        sections_with_sequence_issues = sum(1 for section in sections_with_issues if section["sequence"])
        sections_with_not_found_issues = sum(1 for section in sections_with_issues if section["not_found"])
        sections_with_style_issues = sum(1 for section in sections_with_issues if section["style_issues"] > 0)

        # Create a Template object using the HTML file and os.getcwd()
        template = load_template_from_html("files/reporting_template.html")
        
        # Replace the now tag with actual datetime for demonstration
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Render the template with the data
        html = template.render(
            data = report_data,
            title = self.jisebi_document.title["content"],
            current_time=current_time,
            total_issues=total_issues,
            sections_with_issues=sections_with_issues,
            sections_with_sequence_issues=sections_with_sequence_issues,
            sections_with_not_found_issues=sections_with_not_found_issues,
            sections_with_style_issues=sections_with_style_issues,
            sections=["title", "authors", "abstract", "introduction", "method", "literature_review", "result", "discussion", "conclusion", "references"]
        )
        
        return html

    async def save_dashboard_to_file(self, output_file: str = "files/paper_review_dashboard.html") -> None:
        """
        Generate the dashboard HTML and save it to a file
        
        Args:
            report_data: Dictionary containing paper structure and issues
            output_file: Path to save the HTML file
        """
        html = await self.generate_dashboard_html()
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"Dashboard saved to {output_file}")

    async def generate_final_report(self):
        try:
            settings: Settings = get_settings()
            randomname = ''.join(random.choices(string.ascii_letters, k=15))
            current_dir = os.getcwd().replace("\\", "/")

            # Convert HTML to PDF
            options = {
                'page-size': 'Letter'
            }

            pdfkit.from_string(await self.generate_dashboard_html(), output_path=f'{current_dir}/files/export/{randomname}-summary.pdf', options=options)
   
            docx_response = await self.generate_report(f'{current_dir}/files/export/{randomname}-report.docx')

            if docx_response != "exported":
                raise Exception("Failed generating docx")

            # Convert DOCX to PDF

            docx_path = f'{current_dir}/files/export/{randomname}-report.docx'

            if settings.PLATFORM == "WINDOWS":
                
                import comtypes.client
                word = comtypes.client.CreateObject('Word.Application')
                word.Visible = False
                doc = word.Documents.Open(docx_path)
                doc.SaveAs(f'{current_dir}/files/export/{randomname}-report.pdf', FileFormat=17) # 17 is PDF format
                doc.Close()
                word.Quit()

            elif settings.PLATFORM == "LINUX":
                import subprocess
                subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf:writer_pdf_Export", docx_path, "--outdir", f'{current_dir}/files/export'])

            # Merge the PDFs
            merger = PdfMerger()
            merger.append(f'{current_dir}/files/export/{randomname}-summary.pdf')
            merger.append(f'{current_dir}/files/export/{randomname}-report.pdf')
            merger.write(f'{current_dir}/files/export/{randomname}-merged.pdf')
            merger.close()

            # Open the PDF file in binary mode
            with open(f'{current_dir}/files/export/{randomname}-merged.pdf', "rb") as pdf_file:
                # Read the PDF content
                pdf_content = pdf_file.read()

                # Create a BytesIO stream from the content
                pdf_stream = BytesIO(pdf_content)
                pdf_stream.seek(0)  # Reset the stream pointer to the beginning
            
            files = ["report.pdf", "report.docx", "summary.pdf", "merged.pdf"]
            for type in files:
                try:
                    if os.path.exists(f'{current_dir}/files/export/{randomname}-{type}'):
                        os.remove(f'{current_dir}/files/export/{randomname}-{type}')
                        print(f"{f'{current_dir}/files/export/{randomname}-{type}'} has been deleted.")
                except Exception as e:
                    print(e)

            return pdf_stream
        
        except Exception as e:
            traceback.print_exc()
            files = ["report.pdf", "report.docx", "summary.pdf", "merged.pdf"]
            for type in files:
                try:
                    if os.path.exists(f'{current_dir}/files/export/{randomname}-{type}'):
                        os.remove(f'{current_dir}/files/export/{randomname}-{type}')
                        print(f"{f'{current_dir}/files/export/{randomname}-{type}'} has been deleted.")
                except Exception as e:
                    print(e)
            raise Exception({
                "failure": "Failed generating final report",
                "detail": e
            })

# TO BE REMOVED - FOR TESTING PURPOSES
async def rendur():
    """
    Generate an A4-sized HTML dashboard from the supplied JSON report data.
    
    Args:
        report_data: Dictionary containing paper structure and issues
        
    Returns:
        String containing HTML for the dashboard
    """
    
    # Extract and prepare the data

    

    # Create a Template object using the HTML file and os.getcwd()
    template = load_template_from_html("files/reporting_template.html")
    
    # Replace the now tag with actual datetime for demonstration
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html = template.render(
        title = "Paper Title",
        current_time="2025-04-23 22:42:27",
        total_issues=8,
        sections_with_issues=2,
        sections_with_sequence_issues=0,
        sections_with_not_found_issues=1,
        sections_with_style_issues=1,
        sections=["title", "authors", "abstract", "introduction", "method", "literature_review", "result", "discussion", "conclusion", "references"],
        data = {
            "title": {
                "section_issue": {
                    "not_found": [],
                    "sequence": []
                },
                "body": {}
            },
            "authors": {
                "section_issue": {
                    "not_found": [],
                    "sequence": []
                },
                "authors": {},
                "affiliations": {
                    "1": {},
                    "2": {}
                },
                "emails": {
                    "1": {},
                    "2": {}
                }
            },
            "abstract": {
                "section_issue": {
                    "not_found": [],
                    "sequence": [],
                    "semantic": [
                        "Potential location or organization detected. Please check."
                    ]
                },
                "header": {},
                "background": {
                    "prefix": [
                        {
                            "run_index": 0,
                            "text": "Background:",
                            "issues": {
                                "font_size": "Font size is 10pt instead of 9pt"
                            }
                        }
                    ],
                    "body": [
                        {
                            "run_index": 0,
                            "text": " What is the latest knowledge on the issue? ",
                            "issues": {
                                "font_size": "Font size is 10pt instead of 9pt"
                            }
                        }
                    ]
                },
                "objective": {
                    "prefix": [
                        {
                            "run_index": 0,
                            "text": "Objective:",
                            "issues": {
                                "font_size": "Font size is 10pt instead of 9pt"
                            }
                        }
                    ],
                    "body": [
                        {
                            "run_index": 0,
                            "text": " What did you want to find out? ",
                            "issues": {
                                "font_size": "Font size is 10pt instead of 9pt"
                            }
                        }
                    ]
                },
                "methods": {
                    "prefix": [
                        {
                            "run_index": 0,
                            "text": "Methods:",
                            "issues": {
                                "font_size": "Font size is 10pt instead of 9pt"
                            }
                        }
                    ],
                    "body": [
                        {
                            "run_index": 0,
                            "text": " How did you go about finding it? What type of methodology did you use? A quantitative study/a randomized controlled study/a qualitative survey/a literature review/a double blind trial",
                            "issues": {
                                "font_size": "Font size is 10pt instead of 9pt"
                            }
                        }
                    ]
                },
                "results": {
                    "prefix": [
                        {
                            "run_index": 0,
                            "text": "Results:",
                            "issues": {
                                "font_size": "Font size is 10pt instead of 9pt"
                            }
                        }
                    ],
                    "body": [
                        {
                            "run_index": 0,
                            "text": " What did you find? What data or outcomes did you observe? Do not be vague! State exactly what you found.",
                            "issues": {
                                "font_size": "Font size is 10pt instead of 9pt"
                            }
                        }
                    ]
                },
                "conclusion": {
                    "prefix": [
                        {
                            "run_index": 0,
                            "text": "Conclusion:",
                            "issues": {
                                "font_size": "Font size is 10pt instead of 9pt"
                            }
                        }
                    ],
                    "body": [
                        {
                            "run_index": 0,
                            "text": " What did your results tell you? Did you find out what you wanted? Why or why not? What should be studied next?",
                            "issues": {
                                "font_size": "Font size is 10pt instead of 9pt"
                            }
                        }
                    ]
                },
                "keywords": {
                    "body": {
                        "0": {
                            "run_issues": [
                                {
                                    "run_index": 0,
                                    "text": "Keywords",
                                    "issues": {
                                        "bold": "Bold is True instead of False",
                                        "italic": "Italic is True instead of False"
                                    }
                                },
                                {
                                    "run_index": 1,
                                    "text": ":",
                                    "issues": {
                                        "bold": "Bold is True instead of False",
                                        "italic": "Italic is True instead of False"
                                    }
                                }
                            ],
                            "paragraph_issues": {}
                        }
                    },
                    "prefix": [
                        {
                            "run_index": 0,
                            "text": "Keywords",
                            "issues": {
                                "font_size": "Font size is 10pt instead of 8pt"
                            }
                        }
                    ]
                },
                "article_history": {
                    "body": {
                        "0": {
                            "run_issues": [
                                {
                                    "run_index": 0,
                                    "text": "Article history:",
                                    "issues": {
                                        "bold": "Bold is True instead of False",
                                        "italic": "Italic is True instead of False"
                                    }
                                }
                            ],
                            "paragraph_issues": {}
                        }
                    },
                    "prefix": []
                }
            },
            "introduction": {
                "section_issue": {
                    "not_found": [],
                    "sequence": [
                        "Should come before literature_review"
                    ],
                    "semantic": [
                        "Potential location or organization detected. Please check."
                    ]
                },
                "heading": {},
                "body": {
                    "0": {
                        "run_issues": [
                            {
                                "run_index": 0,
                                "text": "Related Works",
                                "issues": {
                                    "font_size": "Font size is 14.0pt instead of 10pt"
                                }
                            },
                            {
                                "run_index": 2,
                                "text": "or Literature review section is optional.",
                                "issues": {
                                    "font_name": "Font name is 'Antonio SemiBold' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 6,
                                "text": "only shown in ",
                                "issues": {
                                    "font_size": "Font size is 11.5pt instead of 10pt"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    }
                }
            },
            "method": {
                "section_issue": {
                    "not_found": [],
                    "sequence": []
                },
                "heading": {},
                "body": {
                    "21": {
                        "run_issues": [
                            {
                                "run_index": 0,
                                "text": "The significance of The Relationships in The Model",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    },
                    "23": {
                        "run_issues": [
                            {
                                "run_index": 3,
                                "text": "\t*alpha=0.05",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            },
                            {
                                "run_index": 4,
                                "text": " (this is additional ",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            },
                            {
                                "run_index": 5,
                                "text": "legend/caption",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            },
                            {
                                "run_index": 7,
                                "text": "for clarity",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            },
                            {
                                "run_index": 8,
                                "text": " of data description, if needed)",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    },
                    "36": {
                        "run_issues": [
                            {
                                "run_index": 1,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 2,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 3,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 4,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 5,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 6,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 7,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 8,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 9,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 10,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 11,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 12,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 14,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 15,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 16,
                                "text": "",
                                "issues": {
                                    "font_name": "Font name is 'Symbol' instead of 'Times New Roman'"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    }
                }
            },
            "result": {
                "section_issue": {
                    "not_found": [],
                    "sequence": []
                },
                "heading": {
                    "0": {
                        "run_issues": [
                            {
                                "run_index": 1,
                                "text": "ults",
                                "issues": {
                                    "font_name": "Font name is 'Algerian' instead of 'Times New Roman'"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    }
                },
                "body": {}
            },
            "discussion": {
                "section_issue": {
                    "not_found": [],
                    "sequence": [],
                    "semantic": {}
                },
                "heading": {},
                "body": {}
            },
            "conclusion": {
                "section_issue": {
                    "not_found": [],
                    "sequence": [],
                    "semantic": [
                        "The section does not indicate any contribution statement",
                        "Potential location or organization detected. Please check."
                    ]
                },
                "heading": {},
                "body": {
                    "15": {
                        "run_issues": [
                            {
                                "run_index": 2,
                                "text": "There were no animal subjects",
                                "issues": {
                                    "font_name": "Font name is 'Anton' instead of 'Times New Roman'"
                                }
                            },
                            {
                                "run_index": 15,
                                "text": "this statement is mandatory.",
                                "issues": {
                                    "font_name": "Font name is 'a_Campus' instead of 'Times New Roman'"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    }
                }
            },
            "references": {
                "section_issue": {
                    "not_found": [],
                    "sequence": []
                },
                "heading": {},
                "body": {
                    "0": {
                        "run_issues": [],
                        "paragraph_issues": {
                            "style": "Style is Normal instead of references"
                        }
                    },
                    "1": {
                        "run_issues": [],
                        "paragraph_issues": {
                            "style": "Style is Normal instead of references"
                        }
                    },
                    "3": {
                        "run_issues": [
                            {
                                "run_index": 0,
                                "text": "G. Eason, B. Noble, and I.N. Sneddon, “On certain integrals of Lipschitz-Hankel type involving products of Bessel functions,” Phil. Trans. Roy. Soc. London, vol. A247, pp. 529-551, April 1955. (",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            },
                            {
                                "run_index": 1,
                                "text": "references",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            },
                            {
                                "run_index": 2,
                                "text": ")",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    },
                    "4": {
                        "run_issues": [
                            {
                                "run_index": 0,
                                "text": "J. Clerk Maxwell, A Treatise on Electricity and Magnetism, 3rd ed., vol. 2. Oxford: Clarendon, 1892, pp.68-73.",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    },
                    "5": {
                        "run_issues": [
                            {
                                "run_index": 0,
                                "text": "I.S. Jacobs and C.P. Bean, “Fine particles, thin films and exchange anisotropy,” in Magnetism, vol. III, G.T. Rado and H. Suhl, Eds. New York: Academic, 1963, pp. 271-350.",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    },
                    "6": {
                        "run_issues": [
                            {
                                "run_index": 0,
                                "text": "K. Elissa, “Title of paper if known,” unpublished.",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    },
                    "7": {
                        "run_issues": [
                            {
                                "run_index": 0,
                                "text": "R. Nicole, “Title of paper with only first word capitalized,” J. Name Stand. Abbrev., in press.",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    },
                    "8": {
                        "run_issues": [
                            {
                                "run_index": 0,
                                "text": "Y. Yorozu, M. Hirano, K. Oka, and Y. Tagawa, “Electron spectroscopy studies on magneto-optical media and plastic substrate interface,” IEEE Transl. J. Magn. Japan, vol. 2, pp. 740-741, August 1987 [Digests 9th Annual Conf. Magnetics Japan, p. 301, 1982].",
                                "issues": {
                                    "font_size": "Font size is 8.0pt instead of 10pt"
                                }
                            }
                        ],
                        "paragraph_issues": {}
                    },
                    "11": {
                        "run_issues": [],
                        "paragraph_issues": {
                            "style": "Style is Normal instead of references"
                        }
                    }
                }
            },
            "literature_review": {
                "section_issue": {
                    "not_found": [],
                    "sequence": [
                        "Should come after introduction"
                    ]
                },
                "heading": {},
                "body": {}
            },
            "semantic": {
                "grammar": {
                    "status": True,
                    "data": {
                        "original": "Title of the Paper",
                        "corrected": "Fix grammar and typos. Title of the Paper.",
                        "highlighted_typos": [
                            {
                                "word": "Fix",
                                "status": "suggested addition"
                            },
                            {
                                "word": "grammar",
                                "status": "suggested addition"
                            },
                            {
                                "word": "and",
                                "status": "suggested addition"
                            },
                            {
                                "word": "typos.",
                                "status": "suggested addition"
                            },
                            {
                                "word": "Title",
                                "status": "correct"
                            },
                            {
                                "word": "of",
                                "status": "correct"
                            },
                            {
                                "word": "the",
                                "status": "correct"
                            },
                            {
                                "word": "_Paper_",
                                "status": "typo (underlined)"
                            }
                        ]
                    }
                },
                "abstract": {
                    "keyword_results": [
                        "Keywords: Keyword 1 exists.",
                        "Keyword 2 exists.",
                        "Keyword 3 exists.",
                        "Keyword 4 exists.",
                        "Keyword 5 exists.",
                        "Keyword 6 (Min 3 exists.",
                        "Max 6 phrases/keywords. A combination of all keywords represents the content exists.",
                        "contribution exists.",
                        "or purpose of the manuscript.) exists."
                    ],
                    "nlp_result": [
                        {
                            "label": "Background",
                            "sentences": [],
                            "empty": True
                        },
                        {
                            "label": "Objective",
                            "sentences": [
                                "Objective: What did you want to find out?",
                                "A combination of all keywords represents the content, contribution, or purpose of the manuscript.)"
                            ],
                            "empty": False
                        },
                        {
                            "label": "Methods",
                            "sentences": [
                                "Background: What is the latest knowledge on the issue?",
                                "Methods: How did you go about finding it?",
                                "What type of methodology did you use?",
                                "What data or outcomes did you observe?",
                                "Do not be vague!",
                                "State exactly what you found.",
                                "Did you find out what you wanted?",
                                "Why or why not?",
                                "What should be studied next?",
                                "(Abstract consists of 150 to a maximum of 300 words.",
                                "Abstracts are arranged in a structured manner.)",
                                "Keywords: Keyword 1, Keyword 2, Keyword 3, Keyword 4, Keyword 5, Keyword 6 (Min 3, Max 6 phrases/keywords.",
                                "Article history: Received 5 April 20XX, first decision 22 April 20XX, accepted 22 August 20XX, available online 28 October 20XX"
                            ],
                            "empty": False
                        },
                        {
                            "label": "Results",
                            "sentences": [
                                "A quantitative study/a randomized controlled study/a qualitative survey/a literature review/a double blind trial\nResults: What did you find?",
                                "Conclusion: What did your results tell you?"
                            ],
                            "empty": False
                        },
                        {
                            "label": "Conclusions",
                            "sentences": [],
                            "empty": True
                        }
                    ],
                    "common_keywords": [
                        "keyword",
                        "20xx",
                        "keywords",
                        "find",
                        "study"
                    ],
                    "word_count": 158
                }
            },
            "novelty": {
                "num_results": 20,
                "average_similarity": 0.0,
                "details": {
                    "query": "Title of the Paper",
                    "num_results": 20,
                    "journals": [
                        {
                            "doi": "10.24071/llt.v23i2.2581.s280",
                            "title": "Paper title page",
                            "abstract": "",
                            "url": "https://doi.org/10.24071/llt.v23i2.2581.s280",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.5194/bg-2016-177-rc2",
                            "title": "see title of paper",
                            "abstract": "",
                            "url": "https://doi.org/10.5194/bg-2016-177-rc2",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.5194/essd-2020-203-sc4",
                            "title": "Title of the paper",
                            "abstract": "",
                            "url": "https://doi.org/10.5194/essd-2020-203-sc4",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.5555/testconfpaperwebdeposit",
                            "title": "Test Conference Paper",
                            "abstract": "",
                            "url": "https://doi.org/10.5555/testconfpaperwebdeposit",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.5555/conferences123",
                            "title": "Paper Title",
                            "abstract": "",
                            "url": "https://doi.org/10.5555/conferences123",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.1117/12.280779",
                            "title": "&lt;title&gt;Interactive paper as security substrate&lt;/title&gt;",
                            "abstract": "",
                            "url": "https://doi.org/10.1117/12.280779",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.5555/abcdef123",
                            "title": "Paper Title",
                            "abstract": "",
                            "url": "https://doi.org/10.5555/abcdef123",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.1117/12.280771",
                            "title": "&lt;title&gt;Photoerasing paper and thermocoloring film&lt;/title&gt;",
                            "abstract": "",
                            "url": "https://doi.org/10.1117/12.280771",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.1117/12.280763",
                            "title": "&lt;title&gt;Chemical control of water penetration in paper&lt;/title&gt;",
                            "abstract": "",
                            "url": "https://doi.org/10.1117/12.280763",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.5194/gmd-2016-69-sc2",
                            "title": "Reply to comment on paper title by Executive Editor",
                            "abstract": "",
                            "url": "https://doi.org/10.5194/gmd-2016-69-sc2",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.5194/gmd-2020-238-ac1",
                            "title": "Amendment of paper title and data availability",
                            "abstract": "",
                            "url": "https://doi.org/10.5194/gmd-2020-238-ac1",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.1117/12.280777",
                            "title": "&lt;title&gt;Integrated electronic circuits and devices based on interactive paper&lt;/title&gt;",
                            "abstract": "",
                            "url": "https://doi.org/10.1117/12.280777",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.1117/12.280765",
                            "title": "&lt;title&gt;Paper and the electronic age: evolution or revolution&lt;/title&gt;",
                            "abstract": "",
                            "url": "https://doi.org/10.1117/12.280765",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.1117/12.280768",
                            "title": "&lt;title&gt;Effect of RC paper support on photographic stability&lt;/title&gt;",
                            "abstract": "",
                            "url": "https://doi.org/10.1117/12.280768",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.21428/d28e8e57.3272dd18",
                            "title": "Evaluation summary and metrics: “Title of paper” (template)",
                            "abstract": "",
                            "url": "https://doi.org/10.21428/d28e8e57.3272dd18",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.1117/12.280774",
                            "title": "&lt;title&gt;Influence of microbial contamination on the quality of printing paper&lt;/title&gt;",
                            "abstract": "",
                            "url": "https://doi.org/10.1117/12.280774",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.1117/12.280782",
                            "title": "&lt;title&gt;Chemical approaches to new coating and filler particles for paper technology&lt;/title&gt;",
                            "abstract": "",
                            "url": "https://doi.org/10.1117/12.280782",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.1117/12.280778",
                            "title": "&lt;title&gt;Potential use of individual components in interactive paper&lt;/title&gt;",
                            "abstract": "",
                            "url": "https://doi.org/10.1117/12.280778",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.5194/essd-2023-168-rc1",
                            "title": "The paper should have a clear focus on the validation dataset (relfecting the title of the paper)",
                            "abstract": "",
                            "url": "https://doi.org/10.5194/essd-2023-168-rc1",
                            "similarity": 0.0,
                            "common_keywords": []
                        },
                        {
                            "doi": "10.1017/9781316650431.012",
                            "title": "Title",
                            "abstract": "",
                            "url": "https://doi.org/10.1017/9781316650431.012",
                            "similarity": 0.0,
                            "common_keywords": []
                        }
                    ]
                }
            }
        }
    )
        

    return html