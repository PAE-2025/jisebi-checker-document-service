from io import BytesIO
from typing import IO, Dict
import xml.etree.ElementTree as ET
from docx.shared import RGBColor
from docx.enum.text import WD_COLOR_INDEX
from helpers.jisebi_evaluation import JISEBIEvaluation
from helpers.jisebi_document import JISEBIDocument
from files.reporting_template import template_str
from jinja2 import Template
from typing import Dict
from datetime import datetime
import pdfkit
from PyPDF2 import PdfMerger
import comtypes.client
import random
import string
import os

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
        
        parent = p_element.getparent()

        if parent is None:
            print("p_element has no parent. Attempting to locate or reattach...")

            # Find the parent manually within the document tree
            root = p_element.getroottree()
            parent = root.getroot()

            if parent is not None:
                print("Reattached p_element to the tree.")
                parent.append(p_element)  # Temporarily reattach it
            else:
                print("Could not find a suitable parent. Aborting operation.")
                return

        if parent is not None:
            parent.replace(p_element, new_p_element)
            # Remove the extra paragraph we created
            self.remove_paragraph(doc.paragraphs[-1])

        else:
            print("Could not find or reattach the parent. Skipping replacement.")
        
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
            
            if data['section_issue']['sequence'] != []:
                obj_index = getattr(document, key)["index"]["first"]
                paragraph_start = 0
                paragraph_end = len(getattr(document, key)["heading"]["content"])
                self.add_highlight(obj_index, paragraph_start, paragraph_end, WD_COLOR_INDEX.YELLOW)
            if key in ['introduction', 'method', 'result', 'discussion', 'conclusion', 'references', 'literature_review'] and (data['heading'] != {} or data["body"] != {}):
                if data["body"] != {}:
                    for paragraph_index, issue in data["body"].items():
                        obj_index = getattr(document, key)["paragraph"]["index"]["first"] + int(paragraph_index)
                        if issue["paragraph_issues"] != {}:
                            paragraph_start = 0
                            paragraph_end = len(self.jisebi_document.contents[obj_index].text)
                            self.add_highlight(obj_index, paragraph_start, paragraph_end, WD_COLOR_INDEX.RED)

                        if issue["run_issues"] != []:


                            # print(getattr(document, key)["object"])
                            # for pra in getattr(document, key)["object"]:
                            #     print (pra.text)

                            paragraph = self.jisebi_document.contents[obj_index]
                            
                            # paragraph = self..introduction["object"][key]
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
            if "section_issue" in section_data:
                if "not_found" in section_data["section_issue"] and section_data["section_issue"]["not_found"]:
                    section_issues["not_found"] = section_data["section_issue"]["not_found"]
                    total_issues += len(section_data["section_issue"]["not_found"])
                
                if "sequence" in section_data["section_issue"] and section_data["section_issue"]["sequence"]:
                    section_issues["sequence"] = section_data["section_issue"]["sequence"]
                    total_issues += len(section_data["section_issue"]["sequence"])
            
            # Check body issues (especially in references)
            if "body" in section_data and isinstance(section_data["body"], dict):
                style_issues = 0
                
                for paragraph_id, paragraph_data in section_data["body"].items():
                    if "paragraph_issues" in paragraph_data:
                        if "style" in paragraph_data["paragraph_issues"]:
                            style_issues += 1
                            total_issues += 1
                
                if style_issues > 0:
                    section_issues["style_issues"] = style_issues
            
            # Only include sections that have issues
            if section_issues["not_found"] or section_issues["sequence"] or section_issues["style_issues"]:
                sections_with_issues.append(section_issues)
        
        # Calculate section order issues
        section_order_issues = []
        for section_data in sections_with_issues:
            for seq_issue in section_data["sequence"]:
                section_order_issues.append(f"{section_data['name']}: {seq_issue}")
        
        # Get overall summary
        sections_with_sequence_issues = sum(1 for section in sections_with_issues if section["sequence"])
        sections_with_not_found_issues = sum(1 for section in sections_with_issues if section["not_found"])
        sections_with_style_issues = sum(1 for section in sections_with_issues if section["style_issues"] > 0)

        # Create a Template object
        template = Template(template_str)
        
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
            randomname = ''.join(random.choices(string.ascii_letters, k=15))
            current_dir = os.getcwd()

            print("here1")

            # Convert HTML to PDF
            options = {
                'page-size': 'Letter'
            }
            
            pdfkit.from_string(await self.generate_dashboard_html(), output_path=f'{current_dir}/files/export/{randomname}-summary.pdf',configuration=pdfkit.configuration(wkhtmltopdf="D:/Software/wkhtmltopdf/bin/wkhtmltopdf.exe"), options=options)
            print("here3")
            await self.generate_report(f'{current_dir}/files/export/{randomname}-report.docx')
    
            print("here2")

            # Convert DOCX to PDF
            word = comtypes.client.CreateObject('Word.Application')
            word.Visible = False
            print('tes')
            doc = word.Documents.Open(f'{current_dir}/files/export/{randomname}-report.docx')
            doc.SaveAs(f'{current_dir}/files/export/{randomname}-report.pdf', FileFormat=17) # 17 is PDF format
            doc.Close()
            word.Quit()

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
                
                print("test")
                # Create a BytesIO stream from the content
                pdf_stream = BytesIO(pdf_content)
                pdf_stream.seek(0)  # Reset the stream pointer to the beginning
            
            files = ["report.pdf", "report.docx", "summary.pdf", "merged.pdf"]
            for type in files:
                try:
                    if os.path.exists(f'{current_dir}/files/export/{randomname}-{type}'):
                        os.remove(f'{current_dir}/files/export/{randomname}-{type}')
                        print(f"{f'files/export/{randomname}-merged.pdf'} has been deleted.")
                except Exception as e:
                    print(e)

            return pdf_stream
        
        except Exception as e:
            files = ["report.pdf", "report.docx", "summary.pdf", "merged.pdf"]
            for type in files:
                try:
                    if os.path.exists(f'{current_dir}/files/export/{randomname}-{type}'):
                        os.remove(f'{current_dir}/files/export/{randomname}-{type}')
                        print(f"{f'files/export/{randomname}-merged.pdf'} has been deleted.")
                except Exception as e:
                    print(e)
            raise e

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

    

    # Create a Template object
    template = Template(template_str)
    
    # Replace the now tag with actual datetime for demonstration
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Render the template with the data
    html = template.render(
        title="Paper Title",
        current_time="2025-04-23 22:42:27",
        total_issues=8,
        sections_with_sequence_issues=2,
        sections_with_not_found_issues=0,
        sections_with_style_issues=1,
        data = {
            "title": {
                "section_issue": {
                    "not_found": [],
                    "sequence": []
                }
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
                    "sequence": []
                },
                "header": {},
                "background": {
                    "body": {},
                    "prefix": {}
                },
                "objective": {
                    "body": {},
                    "prefix": {}
                },
                "methods": {
                    "body": {},
                    "prefix": {}
                },
                "results": {
                    "body": {},
                    "prefix": {}
                },
                "conclusion": {
                    "body": {},
                    "prefix": {}
                },
                "keywords": {
                    "body": {},
                    "prefix": {}
                },
                "article_history": {
                    "body": {},
                    "prefix": {}
                }
            },
            "introduction": {
                "section_issue": {
                    "not_found": [],
                    "sequence": [
                        "Should come before literature_review"
                    ]
                },
                "heading": {},
                "body": {}
            },
            "method": {
                "section_issue": {
                    "not_found": [],
                    "sequence": []
                },
                "heading": {},
                "body": {}
            },
            "result": {
                "section_issue": {
                    "not_found": [],
                    "sequence": []
                },
                "heading": {},
                "body": {}
            },
            "discussion": {
                "section_issue": {
                    "not_found": [],
                    "sequence": []
                },
                "heading": {},
                "body": {}
            },
            "conclusion": {
                "section_issue": {
                    "not_found": [],
                    "sequence": []
                },
                "heading": {},
                "body": {}
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
                    "2": {
                        "run_issues": [],
                        "paragraph_issues": {
                            "style": "Style is Normal instead of references"
                        }
                    },
                    "9": {
                        "run_issues": [],
                        "paragraph_issues": {
                            "style": "Style is Normal instead of references"
                        }
                    },
                    "10": {
                        "run_issues": [],
                        "paragraph_issues": {
                            "style": "Style is Normal instead of references"
                        }
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
                    "sequence": [
                        "Should come after introduction"
                    ]
                },
                "heading": {},
                "body": {}
            }
        }
    )

    # paper title, current time, section with issues, sequence issues, styling issues, missing sections, 

    
    return html