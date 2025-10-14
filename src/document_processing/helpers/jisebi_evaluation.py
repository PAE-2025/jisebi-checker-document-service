import re
import docx
from io import BytesIO
from typing import Literal, Dict, TypedDict, Union, List, Any
import xml.etree.ElementTree as ET
from docx.shared import RGBColor
from docx.enum.text import WD_COLOR_INDEX
from copy import deepcopy
from src.document_processing.helpers.jisebi_document import JISEBIDocument
from src.core.requests.semantic_checking_service import SemanticCheckingService
import asyncio
semantic = SemanticCheckingService()

def stringify(string_list):
    if isinstance(string_list, list) and all(isinstance(item, str) for item in string_list):
        return "\n".join(filter(None, string_list))
    return string_list  # Return unchanged if not a list of strings
class JISEBIEvaluation:

    def __init__(self, document:JISEBIDocument):
        self.jisebi_document:JISEBIDocument  = document  # Initialize the variable with the given value


    async def generate_overall_summary(self):
        
        result1, result2, result3, novelty, discon, ner, grammar, abstract = await asyncio.gather(
            self.sections_exist(), 
            self.sections_order(), 
            self.check_document_font(),
            self.check_novelty_condition(),
            self.check_discon(),
            self.check_ner(),
            self.check_grammar(),
            self.check_abstract()
        )

        # print(novelty)
        # print(discon)
        # print(ner)
        # print(grammar)

        reports = [result1, result2, result3, discon, ner, abstract]
        merged_reports = {}

        for report in reports:
            if report == None:
                continue
            merged_reports = self.merge_reports(merged_reports, report)

        merged_reports["novelty"] = novelty
    
        return merged_reports

    def merge_reports(self, dict1:dict, dict2:dict):
        """
        Recursively merge two dictionaries, including nested dictionaries.

        - Values in dict2 override dict1 if there are conflicts at the same level.
        - If both values are dictionaries, they will be merged recursively.
        
        Parameters:
        dict1 (dict): Base dictionary.
        dict2 (dict): Dictionary with updated values.
        
        Returns:
        dict: Merged dictionary containing elements from both dict1 and dict2.
        """
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # If both are dictionaries, merge them recursively
                result[key] = self.merge_reports(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                # Merge lists by appending elements
                result[key] += value
            else:
                # Otherwise, just update the value
                result[key] = value
                
        return result
    
    async def check_novelty_condition(self):
        if self.jisebi_document.title["index"] == -1 or self.jisebi_document.abstract["index"] == -1:
            return None
        else:
            response = await semantic.check_novelty(
                stringify(self.jisebi_document.title["content"]), 
                stringify(self.jisebi_document.abstract["paragraph"]["content"])
            )
            similarities = [journal["similarity"] for journal in response["journals"]]
            average_similarity = sum(similarities) / len(similarities) if similarities else 0.0

            return {
                "num_results": response["num_results"],
                "average_similarity": average_similarity,
                "details": response
            }
    
    async def check_discon(self):
        if self.jisebi_document.discussion["index"] == -1 or self.jisebi_document.conclusion["index"] == -1:
            return {}
        else:

            result = {
                "discussion": {
                    "section_issue": {
                        "semantic": {}
                    }
                },
                "conclusion": {
                    "section_issue": {
                        "semantic": {}
                    }
                }
            }

            response = await semantic.check_discon(
                stringify(self.jisebi_document.discussion["paragraph"]["content"]), 
                stringify(self.jisebi_document.conclusion["paragraph"]["content"])
            )

            if response["has_comparison"] == False:
                result["discussion"]["section_issue"]["semantic"] = ["The section does not indicate any comparison"]
            if response["has_contribution"] == False:
                result["conclusion"]["section_issue"]["semantic"] = ["The section does not indicate any contribution statement"]

            return result

        
    async def check_ner(self):

        sections = ['title', 'abstract', 'introduction', 'conclusion']
        payload = []
        result = {}

        for section in sections:
            section_object = getattr(self.jisebi_document, section)
            if section_object["index"] != -1:
                result[section] = {}
                if section == 'title':
                    payload.append(stringify(section_object["content"]))
                else:
                    payload.append(stringify(section_object["paragraph"]["content"]))
        if payload == []:
            result = {}
        else:
            response = await semantic.check_ner(payload)

            
            for index, (key, value) in enumerate(result.items()):
                if response["entities"][index] != []:
                    result[key] = {
                        "section_issue": {
                            "semantic": ["Potential location or organization detected. Please check."]
                        }
                    }
        

            # for index, (key, value) in enumerate(result.items()):
            #     result[key] = {
            #         "text": response["text"][index],
            #         "entities": response["entities"][index]
            #     }
        
        return result

    async def check_grammar(self):
        if self.jisebi_document.title["index"] == -1:
            return None
        else:
            return await semantic.check_grammar(stringify(self.jisebi_document.title["content"]))
        
    async def check_abstract(self):
        if self.jisebi_document.abstract["index"] == -1:
            return None
        else:
            abstract = stringify(self.jisebi_document.abstract["paragraph"]["content"])
            keyword = stringify(self.jisebi_document.abstract["paragraph"]["keywords"]["content"])
            response = await semantic.check_abstract(abstract, keyword)

            result = {
                "abstract": {
                    "section_issue": { 
                        "semantic": [] 
                    }
                }
            }

            if (all(item.strip().endswith("exists.") for item in response["keyword_results"]) == False):
                result["abstract"]["section_issue"]["semantic"].append("Not all keywords mentioned exist in the abstract. Please check.")
            if(all(item["empty"] == False for item in response["nlp_result"]) == False):
                result["abstract"]["section_issue"]["semantic"].append("Abstract structure incomplete. Please check.")

            return result



    async def sections_exist(self):

        document = self.jisebi_document

        result = {
            "title": {"section_issue": {"not_found": []}},
            "authors": {"section_issue": {"not_found": []}},
            "abstract": {"section_issue": {"not_found": []}},
            "introduction": {"section_issue": {"not_found": []}},
            "method": {"section_issue": {"not_found": []}},
            "result": {"section_issue": {"not_found": []}},
            "discussion": {"section_issue": {"not_found": []}},
            "conclusion":{"section_issue": {"not_found": []}},
            "references": {"section_issue": {"not_found": []}},
            "literature_review": {"section_issue": {"not_found": []}},
        }
    
        sections = ['title', 'authors', 'abstract', 'introduction', 'method', 'result', 'discussion', 'conclusion', 'references', 'literature_review']
        
        for section in sections:
            section_object = getattr(document, section)
            if section not in ["authors", "abstract"]:
                if section_object["index"] == -1:
                    result[section]["section_issue"]["not_found"].append(f"The {section} cannot be found")

            elif section == "authors":
                if section_object["index"] == -1:
                    result[section]["section_issue"]["not_found"].append(f"The {section} cannot be found")
                    continue

                if section_object["authors"]["index"] == -1:
                    result[section]["section_issue"]["not_found"].append(f"The Author(s)'s name cannot be found")

                if "affiliation" not in section_object["affiliations"]["data"]["1"]:
                    result[section]["section_issue"]["not_found"].append(f"The Author(s)'s affiliation cannot be found")

                if "email" not in section_object["affiliations"]["data"]["1"]:
                    result[section]["section_issue"]["not_found"].append(f"The Author(s)'s email cannot be found")

            elif section == "abstract":
                if section_object["index"] == -1:
                    result[section]["section_issue"]["not_found"].append(f"The {section} cannot be found")
                    continue
                
                abstract_sections = ["background", "objective", "methods", "results", "conclusion", "keywords", "article_history"]
                for abstract_section in abstract_sections:
                    if "heading" not in section_object["paragraph"][abstract_section]:
                        result[section]["section_issue"]["not_found"].append(f"The Abstract's {abstract_section} cannot be found")

        return result

    async def sections_order(self):

        document = self.jisebi_document

        result = {
            "title": {"section_issue": {"sequence": []}},
            "authors": {"section_issue": {"sequence": []}},
            "abstract": {"section_issue": {"sequence": []}},
            "introduction": {"section_issue": {"sequence": []}},
            "method": {"section_issue": {"sequence": []}},
            "result": {"section_issue": {"sequence": []}},
            "discussion": {"section_issue": {"sequence": []}},
            "conclusion":{"section_issue": {"sequence": []}},
            "references": {"section_issue": {"sequence": []}},
            "literature_review": {"section_issue": {"sequence": []}},
        }

        # Define the expected order of document sections
        expected_order = ['title', 'authors', 'abstract', 'introduction', 'method', 'result', 'discussion', 'conclusion', 'references']
        
        if document.literature_review["index"] != -1:
            result["literature_review"] = {"section_issue": {"sequence": []}}
            expected_order.insert(4, "literature_review")

        # Extract the start indices for each section
        # For title, authors, abstract: use the single index value
        # For other sections: use the 'first' value from the index dictionary
        indices = {}
        for section in expected_order:

            if getattr(document, section)['index'] != -1:

                indices[section] = getattr(document, section)['index']['first']
        
        # Check if the indices are in ascending order
        for i in range(len(expected_order) - 1):
            current = expected_order[i]
            next_section = expected_order[i + 1]
            
            # Skip if either section is missing
            if current not in indices or next_section not in indices:
                continue
            
            # Check if the current section index is greater than or equal to the next section index
            if indices[current] >= indices[next_section]:
                # Flag the out-of-order sections
                if current in result:
                    result[current]["section_issue"]["sequence"].append(f"Should come before {next_section}")
                if next_section in result:
                    result[next_section]["section_issue"]["sequence"].append(f"Should come after {current}")
        
        # Check for any sections with the same index
        unique_indices = set()
        duplicate_indices = set()
        
        for section, idx in indices.items():
            if idx in unique_indices:
                duplicate_indices.add(idx)
            else:
                unique_indices.add(idx)
        
        # Flag sections with duplicate indices
        for section in expected_order:
            if section in indices and indices[section] in duplicate_indices:
                if 'flag' not in result[section]:
                    result[section]["section_issue"]["sequence"].append(f"Has duplicate index {indices[section]}")
                else:
                    result[section]["section_issue"]["sequence"].append(f", has duplicate index {indices[section]}")
        
        # Check for inconsistencies in the range sections (first/last values)
        for section in expected_order:
            if section not in ['title', 'authors', 'abstract'] and section in dir(document):
                if getattr(document, section)['index'] != -1:
                    first = getattr(document, section)['index']['first']
                    last = getattr(document, section)['index']['last']
                
                    # Check if first page is after last page
                    if first > last:
                        if 'flag' not in result[section]:
                            result[section]["section_issue"]["sequence"].append(f"First page ({first}) is after last page ({last})")
                        else:
                            result[section]["section_issue"]["sequence"].append(f", first page ({first}) is after last page ({last})")
        
        result = {key: value for key, value in result.items() if value != ""}
        return result

    async def check_document_font(self):
        result = {
            'title': {}, 
            'authors': {}, 
            'abstract': {}, 
            'introduction': {"heading": {}, "body": {}}, 
            'method': {"heading": {}, "body": {}}, 
            'result': {"heading": {}, "body": {}}, 
            'discussion': {"heading": {}, "body": {}}, 
            'conclusion': {"heading": {}, "body": {}}, 
            'references': {"heading": {}, "body": {}}, 
            'literature_review': {"heading": {}, "body": {}}, 
        }
        # Define the expected order of document sections
    
        sections = ['title', 'authors', 'abstract', 'introduction', 'method', 'result', 'discussion', 'conclusion', 'references']
    
        if self.jisebi_document.literature_review["index"] != -1:
            result["literature_review"] = {"heading": {}, "body": {}}
            sections.insert(4, "literature_review")
        

        for i, section in enumerate(sections):
            section_report = []
            section_object = getattr(self.jisebi_document, section)

            if section_object["index"] == -1:
                continue

            if section == "title":
                result["title"]["body"] = (self.check_paragraph_font(section_object["object"], "Times New Roman", 18, True, None, "JISEBI Title"))
           
            elif section == "authors":

                result["authors"] = {
                    "authors": {},
                    "affiliations": {},
                    "emails": {}
                }
                
                # Checking the Authors
                result["authors"]["authors"] = (self.check_paragraph_font(section_object["authors"]["object"], "Times New Roman", 11, True, None, style="JISEBI Author Name"))
                
                # Checking the Affiliations of the Authors  
                for key, value in section_object["affiliations"]["data"].items():
                    result["authors"]["affiliations"][key] = (self.check_paragraph_font(value["affiliation"]["object"], "Times New Roman", 9, False, True, style="JISEBI Author Affiliation"))
                    result["authors"]["emails"][key] = (self.check_paragraph_font(value["email"]["object"], "Times New Roman", 8, False, False, style="JISEBI Author Email"))
            
            elif section == "abstract":
                abstract_sections = ["background", "objective", "methods", "results", "conclusion", "keywords", "article_history"]
                result["abstract"] = {
                    "header": {},
                    "background": {}, 
                    "objective": {}, 
                    "methods": {}, 
                    "results": {}, 
                    "conclusion": {}, 
                    "keywords": {}, 
                    "article_history": {}
                }
                if section_object["is_table"] == True:
                    abstract_objects = section_object["object"].cell(0, 0).paragraphs
                else:
                    abstract_objects = section_object["object"]

                # Checking the 'Abstract' Header
                result["abstract"]["header"] = (self.check_paragraph_font(section_object["heading"]["object"], "Times New Roman", 9, True, True, style="JISEBI Abstract title"))

                # Check the ["background", "objective", "methods", "results", "conclusion"]
                for abstract_section in abstract_sections:
                    if abstract_section == "keywords":
                        #Checking the 'abstract_section' line styling
                        result["abstract"][abstract_section]["body"] = (self.check_paragraph_font(abstract_objects[section_object["paragraph"][abstract_section]["paragraph_index"]], "Times New Roman", 8, False, False, style="JISEBI Abstract keywords"))
                        # Checking the 'abstract_section' Prefix
                        result["abstract"][abstract_section]["prefix"] = (self.check_paragraph_font(abstract_objects[section_object["paragraph"][abstract_section]["paragraph_index"]].runs[section_object["paragraph"][abstract_section]["heading"]["run_index"]["first"]], "Times New Roman", 8, True, True))
                    elif abstract_section == "article_history":
                        #Checking the 'abstract_section' line styling
                        result["abstract"][abstract_section]["body"] = (self.check_paragraph_font(abstract_objects[section_object["paragraph"][abstract_section]["paragraph_index"]], "Times New Roman", 8, False, False, style="Normal"))
                        # Checking the 'abstract_section' Prefix
                        result["abstract"][abstract_section]["prefix"] = (self.check_paragraph_font(abstract_objects[section_object["paragraph"][abstract_section]["paragraph_index"]].runs[section_object["paragraph"][abstract_section]["heading"]["run_index"]["first"]], "Times New Roman", 8, True, True))
                    else:
                        #Checking the 'abstract_section' line styling
                    
                        prefix_run_index = section_object["paragraph"][abstract_section]["heading"]["run_index"]
                        body_run_index = section_object["paragraph"][abstract_section]["body"]["run_index"]

                        abstract_runs = abstract_objects[section_object["paragraph"][abstract_section]["paragraph_index"]].runs

                        result["abstract"][abstract_section]["prefix"] = (self.check_paragraph_font(abstract_runs[prefix_run_index["first"]], "Times New Roman", 9, True, False))
                        # Checking the 'abstract_section' Prefix
                        result["abstract"][abstract_section]["body"] = (self.check_paragraph_font(abstract_runs[body_run_index["first"]:body_run_index["last"]], "Times New Roman", 9, False, None, style="JISEBI Abstract text"))
            elif section == "references":
                result[section]["heading"] = {}
                result[section]["body"] = {}
                # continue
                result[section]["heading"] = (self.check_paragraph_font(section_object["heading"]["object"], "Times New Roman", 10, False, False, style="JISEBI Reference heading"))
                result[section]["body"] = (self.check_paragraph_font(section_object["paragraph"]["object"], "Times New Roman", 10, None, None, style="references"))
            else:
                # continue

                (result[section])["heading"] = self.check_paragraph_font(section_object["heading"]["object"], "Times New Roman", 10, False, False, style="JISEBI Heading 1")
                result[section]["body"] = self.check_paragraph_font(section_object["paragraph"]["object"], "Times New Roman", 10, None, None, None)
        
        return result

    def check_paragraph_font(self, paragraphs: Union[List, Any], 
                          font_name: str = None, 
                          font_size: int = None, 
                          bold: bool = None, 
                          italic: bool = None,
                          style: str = None) -> Dict:
        """
        Check if paragraphs meet specified font criteria.
        
        Args:
            paragraphs: A single paragraph object or a list of paragraph objects
            font_name: The expected font name
            font_size: The expected font size
            bold: Whether the text should be bold
            italic: Whether the text should be italic
            
        Returns:
            A dictionary containing information about paragraphs that don't meet criteria
        """
        # Convert single paragraph to list for consistent processing

        if not isinstance(paragraphs, list):
            paragraphs = [paragraphs]
                
        results = {}

        if type(paragraphs[0]) == docx.text.run.Run:
            results = (self.check_run_font(paragraphs, font_name, font_size, bold, italic, style))
            return results
            
        else:
            possible_caption = False
            for i, para in enumerate(paragraphs):
                issues = []
                paragraph_issues = {}

                paragraph_style = para.style.name

                # Check style if specified
                if style is not None:
                    if para.style.name is None:  # None means it's using the default setting
                        paragraph_issues["style"] = (f"Style is using document default (possibly 'Normal')")
                    elif para.style.name != style:
                        paragraph_issues["style"] = (f"Style is {para.style.name} instead of {style}")

                #Check if content is a Table
                if type(para) == docx.table.Table:
                    continue
                
                # Check for possible figure caption
                if "Fig" in para.text or "Table" in para.text or "FIG" in para.text or "TABLE" in para.text:
                    possible_caption = True
                

                if (para.text != "" and para.text != None):
                
                    # Check each run in the paragraph
                    run_issues = self.check_run_font(para.runs, font_name, font_size, bold, italic, style, paragraph_style=paragraph_style)
                    if run_issues and run_issues != {"message": "No issues in this part"}:
                        issues = run_issues

                    if possible_caption == True:
                        alternative_check = self.check_run_font(para.runs, font_name, 8, bold, italic, style, paragraph_style=paragraph_style)
                        # Compare run_issues and alternative_check
                        merged_issues = []
                        for idx in range(max(len(run_issues), len(alternative_check))):
                            issue = run_issues[idx] if idx < len(run_issues) else None
                            alt_issue = alternative_check[idx] if idx < len(alternative_check) else None

                            # If either has no issue, treat as no issue
                            if (issue is None or not issue.get("issues")) and (alt_issue is None or not alt_issue.get("issues")):
                                continue  # No issue in either
                            elif (issue is None or not issue.get("issues")) or (alt_issue is None or not alt_issue.get("issues")):
                                continue  # If either has no issue, treat as no issue
                            else:
                                # Both have issues, keep the issue
                                merged_issues.append(issue)

                        issues = merged_issues

                    # If there are issues with this paragraph, add to results
                    if (issues or paragraph_issues):
                        results[f"{i}"] = {
                            "run_issues": issues,
                            "paragraph_issues": paragraph_issues
                        }

            if results == {}:
                pass
            
            return results

    def check_run_font(self, runs: Union[List, Any], 
                    font_name: str = None, 
                    font_size: int = None, 
                    bold: bool = None, 
                    italic: bool = None,
                    style: str = None,
                    paragraph_style: str = None,
                    posssible_caption: bool = False) -> Dict:
        """
        Check if paragraphs meet specified font criteria.
        
        Args:
            paragraphs: A single paragraph object or a list of paragraph objects
            font_name: The expected font name
            font_size: The expected font size
            bold: Whether the text should be bold
            italic: Whether the text should be italic
            
        Returns:
            A dictionary containing information about paragraphs that don't meet criteria
        """
        # Convert single paragraph to list for consistent processing
        if not isinstance(runs, list):
            runs = [runs]

        if not runs:
            return

        default_font_name = "Times New Roman"
        default_font_size = 10
        default_font_bold = False
        default_font_italic = False

        # Resolve default font properties
        if paragraph_style == "Normal":
            default_font_name = self.jisebi_document.default_font["name"]
            default_font_size = self.jisebi_document.default_font["size"] if self.jisebi_document.default_font["size"] != None else 10
            default_font_bold = False
            default_font_italic = False
        
        if paragraph_style != None and paragraph_style != 'None':
            default_font_name = self.jisebi_document.raw_document.styles[paragraph_style].font.name
            default_font_size = self.jisebi_document.raw_document.styles[paragraph_style].font.size.pt if self.jisebi_document.raw_document.styles[paragraph_style].font.size != None else None
            default_font_bold = self.jisebi_document.raw_document.styles[paragraph_style].font.bold
            default_font_italic = self.jisebi_document.raw_document.styles[paragraph_style].font.italic
        
        if default_font_name == None:
            default_font_name = self.jisebi_document.default_font["name"]
        
        if default_font_size == None:
            default_font_size = self.jisebi_document.default_font["size"] if self.jisebi_document.default_font["size"] != None else 10
        
        if default_font_bold == None:
            default_font_bold = False

        if default_font_italic == None:
            default_font_italic = False


        # If default font couldn't be extracted, use Times New Roman as fallback
        if default_font_name is None:
            default_font_name = "Times New Roman"

        run_issues = []
        
        # Check each run in the paragraph
        for run_idx, run in enumerate(runs):
            run_issue = {}

            if re.match(r'^\s*$', run.text):
                continue

            if font_name is not None:
                actual_font = run.font.name
               
                # If the font is None (meaning it's the default font)
                if actual_font is None:

                    actual_font = default_font_name
                
                if actual_font != font_name:
                    run_issue["font_name"] = f"Font name is '{actual_font}' instead of '{font_name}'"
            
            # Check font size if specified
            if font_size is not None:
                # Convert pt to half-points (which is what python-docx uses)
                expected_size = font_size * 2
                if run.font.size is None:
                    actual_font_size = default_font_size
                    if actual_font_size*2 != expected_size:
                        run_issue["font_size"] = f"Font size is {actual_font_size}pt instead of {font_size}pt"
                elif run.font.size.pt * 2 != expected_size:
                    run_issue["font_size"] = f"Font size is {run.font.size.pt}pt instead of {font_size}pt"
            
            # Check bold if specified
            if bold is not None:
                if run.bold is None:  # None means it's using the default setting
                    actual_font_bold = default_font_bold
                    if actual_font_bold != bold:
                        run_issue["bold"] = (f"Bold is {actual_font_bold} instead of {bold} with {paragraph_style}")
                elif run.bold != bold:
                    run_issue["bold"] = (f"Bold is {run.bold} instead of {bold}")
            
            # Check italic if specified
            if italic is not None:
                if run.italic is None:  # None means it's using the default setting
                    actual_font_italic = default_font_italic
                    if actual_font_italic != italic:
                        run_issue["italic"] = (f"Italic is {actual_font_italic} instead of {italic}")
                elif run.italic != italic:
                    run_issue["italic"] = (f"Italic is {run.italic} instead of {italic}")

            if run_issue != {}:
                run_issues.append({
                    "run_index": run_idx,
                    "text": run.text,
                    "issues": run_issue
                })

        return run_issues


