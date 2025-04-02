from pydantic import BaseModel, Field
from typing import List, Optional

class PaperInput(BaseModel):
    id: str = Field(..., description="Unique identifier for the paper")
    title: str = Field(..., description="Title of the paper")
    discussion: Optional[str] = Field(None, description="Discussion section text")
    conclusion: Optional[str] = Field(None, description="Conclusion section text")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "paper123",
                "title": "Advances in NLP for Academic Paper Analysis",
                "discussion": "Our results show significant improvements over previous methods. This is consistent with prior studies that have demonstrated the effectiveness of transformer models.",
                "conclusion": "This study contributes to the field by introducing a novel approach to academic paper analysis. Our findings have important implications for future research."
            }
        }

class ComparisonResult(BaseModel):
    has_comparison: bool = Field(..., description="Whether the paper has comparison statements")
    comparison_count: int = Field(..., description="Number of comparison statements found")
    comparison_sentences: List[str] = Field(..., description="List of comparison statements")

class ContributionResult(BaseModel):
    has_contribution: bool = Field(..., description="Whether the paper has contribution claims")
    contribution_count: int = Field(..., description="Number of contribution claims found")
    contribution_sentences: List[str] = Field(..., description="List of contribution claims")

class PaperAnalysisResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the paper")
    title: str = Field(..., description="Title of the paper")
    has_comparison: bool = Field(..., description="Whether the paper has comparison statements")
    has_contribution: bool = Field(..., description="Whether the paper has contribution claims")
    comparison_count: int = Field(..., description="Number of comparison statements found")
    contribution_count: int = Field(..., description="Number of contribution claims found")
    comparison_sentences: List[str] = Field(..., description="List of comparison statements")
    contribution_sentences: List[str] = Field(..., description="List of contribution claims")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "paper123",
                "title": "Advances in NLP for Academic Paper Analysis",
                "has_comparison": True,
                "has_contribution": True,
                "comparison_count": 2,
                "contribution_count": 1,
                "comparison_sentences": [
                    "Our results show significant improvements over previous methods.",
                    "This is consistent with prior studies that have demonstrated the effectiveness of transformer models."
                ],
                "contribution_sentences": [
                    "This study contributes to the field by introducing a novel approach to academic paper analysis."
                ]
            }
        }
