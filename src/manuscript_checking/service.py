import spacy
import re
import nltk
from nltk.tokenize import sent_tokenize
from src.discon_analyzer.constants import (
    DISCUSSION_COMPARISON_KEYWORDS,
    CONCLUSION_CONTRIBUTION_KEYWORDS,
    CITATION_PATTERNS,
    CONTRIBUTION_VERBS,
    COMPARISON_VERBS
)
from src.config import settings

class AnalyzerService:
    def __init__(self):
        """Initialize the analyzer service with NLP models"""
        print("Loading NLP models...")
        self.nlp = spacy.load(settings.SPACY_MODEL)
        
        # Try to download NLTK data (for better sentence tokenization)
        try:
            nltk.download('punkt', quiet=True)
        except:
            print("Warning: NLTK punkt download failed. Falling back to spaCy sentence tokenization.")
        
        # Load constants from constants.py
        self.discussion_comparison_keywords = DISCUSSION_COMPARISON_KEYWORDS
        self.conclusion_contribution_keywords = CONCLUSION_CONTRIBUTION_KEYWORDS
        self.citation_patterns = CITATION_PATTERNS
        self.contribution_verbs = CONTRIBUTION_VERBS
        self.comparison_verbs = COMPARISON_VERBS
    
    def tokenize_sentences(self, text):
        """Sentence tokenization using NLTK with fallback to spaCy"""
        if not text:
            return []
            
        try:
            # Try NLTK first for better handling of scientific text
            sentences = sent_tokenize(text)
            return sentences
        except:
            # Fall back to spaCy if NLTK fails
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents]
    
    def contains_citation(self, sentence):
        """Check if a sentence contains a citation"""
        for pattern in self.citation_patterns:
            if re.search(pattern, sentence):
                return True
        return False
    
    def semantic_analysis_for_comparison(self, sentence):
        """Use spaCy for semantic analysis of potential comparison statements"""
        doc = self.nlp(sentence)
        
        # Check for comparison verbs and their subjects/objects
        for token in doc:
            # Check if the verb is a comparison verb
            if token.lemma_.lower() in self.comparison_verbs:
                # Look for subjects or objects that indicate research comparison
                research_terms = ["study", "research", "paper", "work", "finding", "result", 
                                 "approach", "method", "literature", "previous", "prior", "existing"]
                
                # Check if any child of the verb contains research terms
                has_research_subject = any(child.text.lower() in research_terms for child in token.children)
                
                # If we found a comparison verb with research-related subjects
                if has_research_subject:
                    return True
                
                # Check for specific subject-object structures indicating comparison
                subjects = [child for child in token.children if child.dep_ in ("nsubj", "nsubjpass")]
                objects = [child for child in token.children if child.dep_ in ("dobj", "pobj")]
                
                # Check if "our" or "this" study is compared to others
                if any(subj.text.lower() in ["our", "this", "the", "these"] for subj in subjects):
                    if any(obj.text.lower() in research_terms for obj in objects):
                        return True
        
        # Look for comparison structures using dependency parsing
        for token in doc:
            # Find prepositions that often indicate comparison
            if token.text.lower() in ["like", "unlike", "as", "than"]:
                if any(child.text.lower() in ["previous", "prior", "existing", "other"] for child in token.children):
                    return True
        
        # Check for structures indicating reference to literature
        literature_terms = ["literature", "studies", "research", "researchers", "papers", "findings"]
        if any(token.text.lower() in literature_terms for token in doc):
            return True
            
        return False
    
    def semantic_analysis_for_contribution(self, sentence):
        """Use spaCy for semantic analysis of potential contribution statements"""
        doc = self.nlp(sentence)
        
        # Check for ownership terms followed by contribution verbs
        ownership_terms = ["our", "this", "the study", "the paper", "the research", "we"]
        
        # Check for contribution verbs and their subjects
        for token in doc:
            # Check if the verb is a contribution verb
            if token.lemma_.lower() in self.contribution_verbs:
                # Look for subjects that indicate paper ownership
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        # Check if the subject or its children contain ownership terms
                        subject_text = child.text.lower()
                        if any(term in subject_text for term in ownership_terms):
                            return True
                        
                        # Check if "paper", "study", "research", "work" is the subject
                        research_terms = ["paper", "study", "research", "work", "finding", "analysis"]
                        if subject_text in research_terms:
                            # Check for determiners like "this", "our"
                            for det in child.children:
                                if det.dep_ == "det" and det.text.lower() in ["this", "our", "the"]:
                                    return True
        
        # Look for explicit contribution phrases
        contribution_terms = ["contribution", "advancement", "innovation", "novel", "new", 
                             "significant", "important", "key", "major", "primary", "main"]
        
        # Check if any contribution terms appear in possessive constructions with ownership terms
        for token in doc:
            if token.text.lower() in contribution_terms:
                # Check if there's an ownership term with possessive relation
                has_ownership = False
                for child in token.children:
                    if child.dep_ == "poss" and child.text.lower() in ["our", "this", "its"]:
                        has_ownership = True
                        break
                if has_ownership:
                    return True
                    
        # Check for "first" followed by verbs like "to show", "to demonstrate", etc.
        first_indicators = [token for token in doc if token.text.lower() == "first"]
        for first in first_indicators:
            next_tokens = [tok for tok in doc if tok.i > first.i]
            for next_token in next_tokens:
                if next_token.dep_ == "xcomp" and next_token.lemma_ in self.contribution_verbs:
                    return True
                
        return False
    
    def is_discussion_comparison(self, sentence):
        """Enhanced check if a sentence in discussion contains comparison with previous research"""
        sentence_lower = sentence.lower()
        
        # Check for direct comparison phrases
        for phrase in self.discussion_comparison_keywords:
            if phrase in sentence_lower:
                return True
                
        # Enhanced patterns for comparison with previous research
        research_comparison_patterns = [
            r'(our|these) (results|findings)( are| were)? (similar to|different from)',
            r'(our|these) (results|findings)( are| were)? (consistent|inconsistent) with',
            r'(our|these) (results|findings)( are| were)? (supported by|contradicted by)',
            r'(in line|aligned) with (previous|prior|existing) (research|studies|literature|work)',
            r'(previous|prior|existing) (research|studies|work|literature) (has|have) (shown|demonstrated|suggested)',
            r'(unlike|similar to) (previous|prior|existing) (research|studies|work|literature)',
            r'(aligns|agrees|disagrees) with [^.]*literature',
            r'(studies|researchers|authors)( have)? (found|reported|observed|noted)',
            r'(Smith|researchers|authors)( et al\.?)?( $$\d{4}$$)?( have)? (found|reported|observed|noted)',
            r'(our|these) findings (support|challenge|contradict)',
            r'(others|other researchers|other studies) have (found|suggested|reported)',
            r'(in|the) literature',
            r'(recent|prior|previous|past|earlier) (work|study|studies|research|investigations)'
        ]
        
        for pattern in research_comparison_patterns:
            if re.search(pattern, sentence_lower):
                return True
        
        # Check for citations, which often indicate comparison with previous research
        if self.contains_citation(sentence):
            return True
                
        # Use semantic analysis for more complex cases
        if self.semantic_analysis_for_comparison(sentence):
            return True
                
        return False
    
    def is_conclusion_contribution(self, sentence):
        """Enhanced check if a sentence in conclusion contains contribution claims"""
        sentence_lower = sentence.lower()
        
        # Check for direct contribution phrases
        for phrase in self.conclusion_contribution_keywords:
            if phrase in sentence_lower:
                return True
                
        # Enhanced patterns for contribution claims
        contribution_patterns = [
            r'(key|main|major|significant|important) (contribution|finding|result) (of|from) (this|our) (study|research|work|paper)',
            r'(this|our) (study|research|work|paper) (provides|offers|presents|gives) (a|an) (novel|innovative|unique|original|new)',
            r'(this|our) (study|research|work|paper) (is|was) the first to',
            r'(the|our) (significance|importance|value|relevance) of (this|our) (study|research|work)',
            r'(this|our) (study|research|work|paper) (enhances|improves|advances|extends) (our|the) (understanding|knowledge)',
            r'(we|this paper|this research|this study|this work) (present|presented|introduce|introduced|develop|developed)',
            r'(novel|new|innovative) (approach|method|framework|technique|tool|solution)',
            r'(we|this study) (establish|established|identify|identified|discover|discovered)',
            r'(we|this study) (fill|filled|address|addressed) (a|the) (gap|need|limitation)',
            r'(important|significant|valuable) (implication|application|insight|finding)',
            r'(we|this paper) (demonstrate|demonstrated|show|showed) that',
            r'(this research|this work|this study) (contributes|contributed) to',
            r'(the|our) (findings|results) (suggest|indicate|reveal|demonstrate)',
            r'(practical|theoretical|methodological) (implications|applications|contributions)',
            r'(the|this) (study|paper|research) (adds|expands|extends) (to|the|our)'
        ]
        
        for pattern in contribution_patterns:
            if re.search(pattern, sentence_lower):
                return True
                
        # Use semantic analysis for more complex cases
        if self.semantic_analysis_for_contribution(sentence):
            return True
                
        return False
    
    def analyze_discussion(self, text):
        """Analyze discussion section for comparison statements"""
        comparison_sentences = []
        sentences = self.tokenize_sentences(text)
        
        for sent_text in sentences:
            sent_text = sent_text.strip()
            if self.is_discussion_comparison(sent_text):
                comparison_sentences.append(sent_text)
        
        return comparison_sentences
    
    def analyze_conclusion(self, text):
        """Analyze conclusion section for contribution claims"""
        contribution_sentences = []
        sentences = self.tokenize_sentences(text)
        
        for sent_text in sentences:
            sent_text = sent_text.strip()
            if self.is_conclusion_contribution(sent_text):
                contribution_sentences.append(sent_text)
        
        return contribution_sentences
    
    def analyze_paper(self, paper):
        """Analyze a single paper's discussion and conclusion sections"""
        paper_id = paper.get("id", "unknown")
        paper_title = paper.get("title", "Untitled")
        
        has_comparison = False
        has_contribution = False
        comparison_count = 0
        contribution_count = 0
        comparison_sentences = []
        contribution_sentences = []
        
        # Analyze discussion
        if "discussion" in paper and paper["discussion"]:
            comparisons = self.analyze_discussion(paper["discussion"])
            comparison_count = len(comparisons)
            has_comparison = comparison_count > 0
            comparison_sentences = comparisons
        
        # Analyze conclusion
        if "conclusion" in paper and paper["conclusion"]:
            contributions = self.analyze_conclusion(paper["conclusion"])
            contribution_count = len(contributions)
            has_contribution = contribution_count > 0
            contribution_sentences = contributions
        
        return {
            "id": paper_id,
            "title": paper_title,
            "has_comparison": has_comparison,
            "has_contribution": has_contribution,
            "comparison_count": comparison_count,
            "contribution_count": contribution_count,
            "comparison_sentences": comparison_sentences,
            "contribution_sentences": contribution_sentences
        }
