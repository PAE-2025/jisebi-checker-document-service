import re
import docx
from io import BytesIO
from typing import Literal, Dict, TypedDict, Union
import xml.etree.ElementTree as ET
from docx.shared import RGBColor
from docx.enum.text import WD_COLOR_INDEX
from copy import deepcopy

class JISEBIDocument:

    def __init__(self, directory):
        self.raw_document       = docx.Document(directory)  # Initialize the variable with the given value
        self.contents           = list(self.raw_document.iter_inner_content())
        self.paragraphs         = self.raw_document.paragraphs
        self.title              = self.extract_title()
        self.authors            = self.extract_authors()
        self.abstract           = self.extract_abstract()
        self.introduction       = self.extract_section("Introduction")
        self.literature_review  = self.extract_section("Literature Review")
        self.method             = self.extract_section("Method")
        self.result             = self.extract_section("Result")
        self.discussion         = self.extract_section("Discussion")
        self.conclusion         = self.extract_section("Conclusion")
        self.references         = self.extract_references()
        self.headers            = self.extract_header()
        self.footer             = self.extract_footer()
        self.default_font       = self.get_default_font()
        self.unidentified       = self.check_unidentified()

    def is_heading(self, paragraph):
        if (paragraph.style.name in ['JISEBI Heading 1', 'Heading 1', 'JISEBI Reference heading']):
            return True
        return False

    def is_subheading(self, paragraph):
        if (paragraph.style.name in ['JISEBI Heading 2', 'JISEBI Heading 3', 'Heading 2', 'Heading 3', 'Caption']):
            return True
        return False

    def is_blank(self, paragraph):
        if (re.match(r'^\s*$', paragraph.text)):
            return True
        return False
        
    def extract_title(self):
        try:            
            # Get the full text from paragraphs
            contents = self.contents

            if (type(contents[0]) == docx.text.paragraph.Paragraph):
                content = contents[0].text
                index = 0
            else:
                content = []
                index =-1
                raise Exception("Title of the manuscript cannot be found")
            
            return {
                "content": content,
                "index": {
                    "first": index,
                    "last": index
                },
                "object": contents[0],
            }
        
        except Exception as e:
            return {"index": -1, "message": f"Error extracting authors: {e}"}

    def extract_authors(self):
        try:
            # Get all paragraphs with text
            contents = self.contents
            author_index = -1
            author_affiliation_start = -1
            author_affiliation_end = -1
            author_data = {}
            affiliation_data = {}

            # Look for author patterns in the first several paragraphs
            for i, paragraph in enumerate(contents):
                if (type(paragraph) == docx.text.paragraph.Paragraph):
                    # Common patterns for author lines
                    if (re.search(r"[A-Za-z\s]+ \d+\)", paragraph.text)):

                        author_text = paragraph.text
                        author_index = i
                        # Remove asterisks and split by commas
                        clean_text = paragraph.text.replace('**', '').strip()
                        author_items = [item.strip() for item in clean_text.split(',')]
                        for i, author in enumerate(author_items, 1):
                            author_data[f"author_{i}"] = author 
                        break
            
            if author_index != -1:
                author_affiliation_start = author_index+1
                author_number = 1
                affiliation_number = 1
                email_number = 1
                for i, content in enumerate(contents[author_affiliation_start:], start=author_affiliation_start):
                    if (type(content) == docx.table.Table):
                        # We're looking for a table with a single cell
                        if len(content.rows) == 1 and len(content.columns) == 1:
                            cell = content.cell(0, 0)
                            # Check if the first paragraph has just the word "Abstract"
                            if cell.paragraphs and re.match(r"^Abstract", cell.paragraphs[0].text.strip()):
                                author_affiliation_end = i-1
                                break
                    elif (type(content) == docx.text.paragraph.Paragraph):
                        if (re.match(r'(?:\d+\))+\s*(.*?),\s*(.*?),\s*(.*?)$', content.text)): 
                            affiliation_data[f"{affiliation_number}"] = {}
                            affiliation_data[f"{affiliation_number}"]["affiliation"] = {}
                            affiliation_data[f"{affiliation_number}"]["affiliation"]["content"] = content.text
                            affiliation_data[f"{affiliation_number}"]["affiliation"]["object"] = content
                            affiliation_data[f"{affiliation_number}"]["affiliation"]["index"] = i
                        if (re.match(r'(.*?)@(.*?)$', content.text)): 
                            affiliation_data[f"{affiliation_number}"]["email"] = {}
                            affiliation_data[f"{affiliation_number}"]["email"]["content"] = content.text
                            affiliation_data[f"{affiliation_number}"]["email"]["object"] = content
                            affiliation_data[f"{affiliation_number}"]["email"]["index"] = i
                            affiliation_number += 1
                        if (re.match(r"^Abstract", content.text)):
                            author_affiliation_end = i-1
                            break
                        elif (self.is_heading(paragraph)):
                            author_affiliation_end = i-1
                            break
            
            if author_affiliation_end == -1:
                raise Exception("Author not found")

            return {
                "index": {
                    "first": author_index,
                    "last": author_affiliation_end
                },
                "object": contents[author_index],
                "authors": {
                    "content": author_text,
                    "index": {
                        "first": author_index,
                        "last": author_index,
                    },
                    "object": contents[author_index]
                },
                "affiliations": {
                    "content": [paragraph.text if type(paragraph) == docx.text.paragraph.Paragraph else "TABLE" for paragraph in contents[author_affiliation_start:author_affiliation_end+1]],
                    "index": {
                        "first": author_affiliation_start,
                        "last": author_affiliation_end
                    },
                    "object": contents[author_affiliation_start:author_affiliation_end+1],
                    "data": affiliation_data
                },
                "data": author_data
            }
        
        except Exception as e:
            print(e)
            return {"index": -1, "message": f"Error extracting authors: {e}"}

    def extract_abstract(self):

        try:
            contents = self.contents
            index = -1
            paragraph_start = -1
            paragraph_end = -1
            background = None
            objective = None
            method = None
            results = None
            conclusion = None
            keywords = None
            article_history = None

            # Check all tables in the document
            for i, content in enumerate(contents):
                if (type(content) == docx.table.Table):
                    # We're looking for a table with a single cell
                    if len(content.rows) == 1 and len(content.columns) == 1:
                        cell = content.cell(0, 0)
                        
                        # Check if the first paragraph has just the word "Abstract"
                        if cell.paragraphs and re.match(r"^Abstract", cell.paragraphs[0].text.strip()):
                            heading_inner_index = 0
                            heading_content = cell.paragraphs[0].text.strip()
                            # Extract all paragraphs after the first one (which is just "Abstract")

                            paragraph_inner_index_start = 1
                            paragraph_inner_index_end = len(cell.paragraphs)-1
                            paragraph_content = [paragraph.text if type(paragraph) == docx.text.paragraph.Paragraph else "TABLE" for paragraph in cell.paragraphs[paragraph_inner_index_start:paragraph_inner_index_end+1]]

                            index = i
                if (type(content) == docx.text.paragraph.Paragraph):
                    if (re.match(r"^Abstract", content.text)):
                            heading_content = content.text
                            heading_index = i
                            paragraph_start = i+1
                            break
            
            if index == -1 and heading_index == -1:
                raise Exception(f"Abstract not found")
            
            if paragraph_start != -1:
                for i, paragraph in enumerate(contents[paragraph_start:], start=paragraph_start):
                    if (self.is_heading(paragraph)):
                        paragraph_end = i-1
                        break

                # Extract the content between the start and end indices
                # content = [paragraph.text for paragraph in contents[start:end+1]]
                paragraph_content = [paragraph.text if type(paragraph) == docx.text.paragraph.Paragraph else "TABLE" for paragraph in contents[paragraph_start:paragraph_end+1]]
            
            if index != -1:
                abstract_paragraphs = contents[index].cell(0,0).paragraphs
            else:
                abstract_paragraphs = contents[paragraph_start:paragraph_end+1]

            for i, paragraph in enumerate(abstract_paragraphs):
                abstract_part = {}
                abstract_part["paragraph_index"] = i
                abstract_part["content"] = paragraph.text
                abstract_part["heading"] = {"content": None, "run_index": {}}
                abstract_part["body"] = {"content": None, "run_index": {}}

                for j, run in enumerate(paragraph.runs):
                    abstract_part["heading"]["content"] = run.text
                    abstract_part["heading"]["run_index"]["first"] = j
                    abstract_part["heading"]["run_index"]["last"] = j
                    abstract_part["body"]["content"] = [run.text for run in paragraph.runs[j+1:]]
                    abstract_part["body"]["run_index"]["first"] = j+1
                    abstract_part["body"]["run_index"]["last"] = len(paragraph.runs)
                    if "background" in run.text.lower():
                        background = abstract_part
                        break
                    if "objective" in run.text.lower():
                        objective = abstract_part
                        break
                    if "method" in run.text.lower():
                        method = abstract_part
                        break
                    if "results" in run.text.lower():
                        results = abstract_part
                        break
                    if "conclusion" in run.text.lower():
                        conclusion = abstract_part
                        break
                    if "keywords" in run.text.lower():
                        keywords = abstract_part
                        break
                    if "article history" in run.text.lower():                        
                        article_history = abstract_part
                        break
                



            if (index != -1):

                return {
                    "index": {
                        "first": index,
                        "last": index
                    },
                    "object": contents[index],
                    "heading": {
                        "content": heading_content,
                        "index": {
                            "first": heading_inner_index,
                            "last": heading_inner_index
                        },
                        "object": contents[index].table.cell(0,0).paragraphs[heading_inner_index]
                    },
                    "paragraph" : {
                        "content": paragraph_content,
                        "index": {
                            "first": paragraph_inner_index_start,
                            "last": paragraph_inner_index_end,
                        },
                        "object": contents[index].table.cell(0,0).paragraphs[paragraph_inner_index_start:paragraph_inner_index_end+1],
                        "background": background,
                        "objective": objective,
                        "methods": method,
                        "results": results,
                        "conclusion": conclusion,
                        "keywords": keywords,
                        "article_history": article_history
                    },
                    "is_table": True
                }

            else:
                return {
                    "index": {
                        "first": index,
                        "last": index
                    },
                    "object": contents[index],
                    "heading": {
                        "content": heading_content,
                        "index": {
                            "first": heading_inner_index,
                            "last": heading_inner_index
                        },
                        "object": contents[index].table.cell(0,0).paragraphs[heading_inner_index]
                    },
                    "paragraph" : {
                        "content": paragraph_content,
                        "index": {
                            "first": paragraph_inner_index_start,
                            "last": paragraph_inner_index_end,
                        },
                        "object": contents[index].table.cell(0,0).paragraphs[paragraph_inner_index_start:paragraph_inner_index_end+1],
                        "background": background,
                        "objective": objective,
                        "methods": method,
                        "results": results,
                        "conclusion": conclusion,
                        "keywords": keywords,
                        "article_history": article_history
                    },
                    "is_table": True
                }

        except Exception as e:
            return {"index": -1, "message": f"Error extracting abstract: {e}"}

    def extract_section(self, section:Literal["Introduction","Literature Review","Method","Result","Discussion","Conclusion"]):
        try:
            # Get all paragraphs with text
            contents = self.contents
            
            start = -1
            end = -1
            content = []
            
            # Find the Introduction header
            for i, paragraph in enumerate(contents):
                if (type(paragraph) == docx.text.paragraph.Paragraph):
                    if (section == "Literature Review"):
                        if (re.match(r'^Literature\s+Review', paragraph.text) or re.match(r'^Related\s+Works', paragraph.text) or
                            re.match(r'^Literature\s+Review\s*$', paragraph.text, re.IGNORECASE) or re.match(r'^Related\s+Works\s*$', paragraph.text, re.IGNORECASE) or
                            re.match(r'^1\.\s*Literature\s+Review\s*$', paragraph.text, re.IGNORECASE)) or re.match(r'^1\.\s*Related\s+Works\s*$', paragraph.text, re.IGNORECASE):
                            start = i+1
                            break
                    else: 
                        if (re.match(rf"^{section}", paragraph.text) or 
                            re.match(rf"^{section}s\s*$", paragraph.text, re.IGNORECASE) or
                            re.match(rf'^{section}\s*$', paragraph.text, re.IGNORECASE) or
                            re.match(rf'^1\.\s*{section}\s*$', paragraph.text, re.IGNORECASE)):
                            start = i+1
                            break
            
            if start == -1:
                raise Exception(f"{section} not found")
            
            # Find the next section header (the lower limit)
            for i, paragraph in enumerate(contents[start:], start=start):
                # Check for paragraphs that are likely section headers:
                # 1. Has 2 or fewer words and ends with a newline or is followed by a paragraph
                # 2. Starts with # or ## (markdown headers)
                # 3. Starts with a number followed by a period (numbered section)
                # 4. Capitalized words with 3 or fewer words that are not part of a normal sentence
                if (self.is_heading(paragraph)):
                    end = i-1
                    break
            
            # If we couldn't find the next section header, assume it goes to the end
            # (unlikely but a fallback)
            if end == -1:
                end = len(contents)
            
            # Extract the content between the start and end indices
            # content = [paragraph.text for paragraph in contents[start:end+1]]
            content = [paragraph.text if type(paragraph) == docx.text.paragraph.Paragraph else "TABLE" for paragraph in contents[start:end+1]]


            return {
                "index": {
                        "first": start-1,
                        "last": end
                    },
                "object": contents[start-1:end+1],
                "heading": {
                    "content": contents[start-1].text,
                    "index": {
                        "first": start-1,
                        "last": start-1
                    },
                    "object": contents[start-1]
                },
                "paragraph": {
                    "content": content,
                    "index": {
                        "first": start,
                        "last": end
                    },
                    "object": contents[start:end+1]
                }
            }
        
        except Exception as e:
            return {"index": -1, "message":f"Error extracting {section}: {e}"}

    def extract_references(self):
        try:
            # Get all paragraphs with text
            contents = self.contents
            
            start = -1
            end = -1
            content = []
            
            # Find the Introduction header
            for i, paragraph in enumerate(contents):
                if (type(paragraph) == docx.text.paragraph.Paragraph):
                    if (re.match(rf"^Reference", paragraph.text) or 
                        re.match(rf"^References\s*$", paragraph.text, re.IGNORECASE) or
                        re.match(rf'^Reference\s*$', paragraph.text, re.IGNORECASE) or
                        re.match(rf'^1\.\s*Reference\s*$', paragraph.text, re.IGNORECASE)):
                        start = i+1
                        break
            
            if start == -1:
                raise Exception(f"References not found")
            
            # Find the Publisher's Note or the last paragraph of the document
            for i, paragraph in enumerate(contents[start:], start=start):
                if (re.match(r"Publisher's Note.*", paragraph.text)):
                    end = i-1
                    break
            
            # If we couldn't find the next section header, assume it goes to the end
            # (unlikely but a fallback)
            if end == -1:
                end = len(contents)
            
            # Extract the content between the start and end indices
            # content = [paragraph.text for paragraph in contents[start:end+1]]
            content = [paragraph.text if type(paragraph) == docx.text.paragraph.Paragraph else "TABLE" for paragraph in contents[start:end+1]]

            return {
                "index": {
                        "first": start-1,
                        "last": end
                    },
                "object": contents[start-1:end+1],
                "heading": {
                    "content": contents[start-1].text,
                    "index": {
                        "first": start-1,
                        "last": start-1
                    },
                    "object": contents[start-1]
                },
                "paragraph": {
                    "content": content,
                    "index": {
                        "first": start,
                        "last": end
                    },
                    "object": contents[start:end+1]
                }
            }

        except Exception as e:
            return {"index": -1, "message": f"Error extracting authors: {e}"}

    def check_unidentified(self):
        sections = [ self.title, self.authors, self.abstract, self.introduction, self.method, self.result, self.discussion, self.conclusion, self.references] 

        if self.literature_review["index"] != -1:
            sections.append(self.literature_review)

        ranges = [(section["index"]["first"], section["index"]["last"]) for section in sections if section["index"] != -1]

        # Sort ranges by the start index
        ranges.sort(key=lambda x: x[0])

        # Find gaps between consecutive ranges
        gaps = []
        for i in range(1, len(ranges)):
            current_start = ranges[i][0]
            previous_end = ranges[i-1][1]
            
            if current_start > previous_end + 1:
                # There's a gap between the previous range's end and current range's start
                gaps.append((previous_end + 1, current_start - 1))

        return gaps

    def extract_header(self):
            
        try:
            # Get the first section
            section = self.raw_document.sections[0]

            # Get first page header
            first_page_header = section.first_page_header
            default_page_header = section.header
            
            return {
                "first_page": {
                    "content": [paragraph.text for paragraph in first_page_header.paragraphs[:]],
                },
                "default_page": {
                    "content": [paragraph.text for paragraph in default_page_header.paragraphs[:]],
                }
            }
        except Exception as e:
            return {
                "first_page": {
                    "content": None,
                },
                "default_page": {
                    "content": None,
                }
            }

    def extract_footer(self):
            
        try:
            # Get the first section
            section = self.raw_document.sections[0]

            # Get first page header
            first_page_header = section.first_page_footer
            
            return {
                "first_page": {
                    "content": [paragraph.text for paragraph in first_page_header.paragraphs[:]],
                },
            }
        except Exception as e:
            return {
                "first_page": {
                    "content": None,
                },
                "message": e
            }

    def get_default_font(self):

        doc = self.raw_document 

        xml = doc.styles.element.xml
        xml_lines = xml.splitlines()
        import re
        document_defaults_flag = False
        xml_string = ""
        for line in xml_lines:
            if "<w:docDefaults>" in line:
                document_defaults_flag = True
            if document_defaults_flag is True:
                xml_string += "\n"+line
            if "</w:docDefaults>" in line:
                document_defaults_flag = False
                break
            
        # Regular expression to extract the value of w:ascii attribute from <w:rFonts>
        font_name_match = re.search(r'w:rFonts[^>]*w:ascii="([^"]+)"', xml_string)

        # If a match is found, print the captured value
        if font_name_match:
            font_name = font_name_match.group(1)  # Extract the value of w:ascii
        else:
            font_name = "Times New Roman"

            # Regular expression to extract the value of w:ascii attribute from <w:rFonts>
        font_size_match = re.search(r'w:sz[^>]*w:val="([^"]+)"', xml_string)

        # If a match is found, print the captured value
        if font_size_match:
            font_size = font_size_match.group(1)  # Extract the value of w:ascii
        else:
            font_size = 10

        return {
            "name": font_name,
            "size": font_size
        }



# if __name__ == "__main__":
#     # Example file path

#     highlighted_count = 0
#     for key, data in formatting_report.items():
#         paragraph = newDoc.introduction["object"][key]
        
#         if 'issues' not in data:
#             continue

#         processed_runs = set()

#         for issue_data in data['issues']:
#             run_index = issue_data.get('run_index')
#             if run_index is None or run_index in processed_runs:
#                 continue
                
#             # Make sure run_index is valid
#             if run_index >= len(paragraph.runs):
#                 print(f"Run index {run_index} is out of range for paragraph {para_index}")
#                 continue
                
#             # Add highlight to the run
#             run = paragraph.runs[run_index]
#             run.font.highlight_color = WD_COLOR_INDEX.YELLOW
            
#             highlighted_count += 1
#             processed_runs.add(run_index)

#     for key, data in structural_report.items():
#         obj_index = getattr(newDoc, key)["index"]["first"]
#         paragraph_start = 0
#         paragraph_end = len(getattr(newDoc, key)["heading"]["content"])
#         newDoc.add_highlight(obj_index, paragraph_start, paragraph_end, WD_COLOR_INDEX.RED)
    
#     # print(formatting_report)
#     # print(structural_report)
#     # print(heading_formatting)
#     # print(newDoc.unidentified)
#     # newDoc.add_highlight(0, 0, 2, WD_COLOR_INDEX.BRIGHT_GREEN)
#     newDoc.export_document("files/scanned.docx")


    
#     newReport = JISEBIReport(newDoc)
#     # newReport.check_fonts()


#     def pretty(d, indent=0):
#         for key, value in d.items():
#             print('\t' * indent + str(key))
#             if isinstance(value, dict):
#                 pretty(value, indent+1)
#             else:
#                 print('\t' * (indent+1) + str(value))

#     # pretty(newDoc.authors)
#     # pretty(newReport.check_fonts())
#     # print(newReport.check_document_font())
#     # print(newReport.sections_order())
#     # print(newReport.sections_exist())
#     result = asyncio.run(newReport.generate_overall_report())
#     print(result)
#     # print(newDoc.abstract["object"].cell(0,0).paragraphs[3].text)