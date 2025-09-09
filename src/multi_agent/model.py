from typing import List, Dict, Optional, Literal, Any, Union
from pydantic import BaseModel, Field

# -------- 0) INPUT & BA --------

class UserRequest(BaseModel):
    question: str = Field(..., description="The user's question")
    topic: str = Field(..., description="The topic of interest")
    dataset_path: str = Field(..., description="Path to the dataset file")
    additional_context: Optional[str] = Field(None, description="Any additional context or constraints")
    current_year: int = Field(..., description="The current year")

class BusinessObjective(BaseModel):
    objective: str = Field(..., description="Defined business objective")
    problem_type: Literal["classification", "regression", "forecasting", "clustering", "unknown"] = Field(..., description="Type of problem")
    success_criteria: List[str] = Field(default_factory=list, description="Criteria for measuring success")
    key_questions: List[str] = Field(default_factory=list, description="Key questions to address")
    key_metrics: List[str] = Field(default_factory=list, description="Key metrics to track")  # consider Literal[...]

class DatasetSpec(BaseModel):
    rows: Optional[int] = Field(None, description="Number of rows")
    columns: Optional[int] = Field(None, description="Number of columns")
    target: Optional[str] = Field(None, description="Target variable name")
    features: List[str] = Field(default_factory=list, description="Feature names")
    time_column: Optional[str] = Field(None, description="Time column if applicable")

class BAReport(BaseModel):
    business_objective: BusinessObjective
    dataset_spec: DatasetSpec
    suitability: Literal["sufficient", "partially_sufficient", "insufficient"] = Field(..., description="Dataset suitability for objective")
    strengths: List[str] = Field(default_factory=list, description="Dataset strengths")
    limitations: List[str] = Field(default_factory=list, description="Dataset limitations")
    risks: List[str] = Field(default_factory=list, description="Risks")
    recommendations: List[str] = Field(default_factory=list, description="Next steps")

# ---------- 1) DATA UNDERSTANDING (DA) ----------

from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class NumericSummary(BaseModel):
    column: str = Field(..., description="Column name")
    count: int = Field(..., description="Non-null count")
    mean: Optional[float] = Field(None, description="Mean")
    std: Optional[float] = Field(None, description="Std dev")
    min: Optional[float] = Field(None, description="Min")
    q1: Optional[float] = Field(None, description="25th percentile")
    median: Optional[float] = Field(None, description="Median")
    q3: Optional[float] = Field(None, description="75th percentile")
    max: Optional[float] = Field(None, description="Max")
    unique: Optional[int] = Field(None, description="Unique values")
    missing: Optional[int] = Field(None, description="Missing values")
    zeros: Optional[int] = Field(None, description="Zero values")
    negative: Optional[int] = Field(None, description="Negative values")
    skewness: Optional[float] = Field(None, description="Skewness")
    outliers: Optional[int] = Field(None, description="Outliers detected")

class CategoricalSummary(BaseModel):
    column: str = Field(..., description="Column name")
    count: int = Field(..., description="Non-null count")
    unique: int = Field(..., description="Unique count")
    top: Optional[str] = Field(None, description="Most frequent value")
    freq: Optional[int] = Field(None, description="Frequency of most frequent value")
    missing: Optional[int] = Field(None, description="Missing values")
    modes: List[str] = Field(default_factory=list, description="Modes")
    mode_freqs: List[int] = Field(default_factory=list, description="Mode frequencies")
    rare_values: List[str] = Field(default_factory=list, description="Rare values")
    rare_freqs: List[int] = Field(default_factory=list, description="Rare value frequencies")

class ColumnExpectation(BaseModel):
    expected_sign: Optional[Literal["positive","negative","any","non-negative","non-positive"]] = None
    allowed_range: Optional[str] = None
    allowed_zero: Optional[bool] = None
    unit: Optional[str] = None
    date_format: Optional[str] = None
    semantic: Optional[Literal["id","amount","count","rate","percentage","balance","delta","misc"]] = None
    notes: Optional[str] = None

class ValidationIssue(BaseModel):
    column: str
    issue_type: Literal[
        "negative_unexpected","out_of_range","type_mismatch",
        "date_inconsistent","high_cardinality","missing_excess","duplicate_rows"
    ]
    count: int
    examples: List[Any] = Field(default_factory=list)
    notes: Optional[str] = None

class DAReport(BaseModel):
    """Full EDA report for Data Understanding phase."""
    # High-level dataset profile
    shape: str = Field(..., description='e.g. "7043 rows x 21 columns"')
    # Column-wise summaries
    numeric_summaries: List[NumericSummary] = Field(default_factory=list)
    categorical_summaries: List[CategoricalSummary] = Field(default_factory=list)
    # Target & relationships
    target_distribution: Optional[Dict[str, float]] = Field(None, description="Target distribution (for classification) or histogram bins (optional)")
    correlations_with_target: Dict[str, float] = Field(default_factory=dict, description="Feature → correlation/association with target")
    key_insights: List[str] = Field(default_factory=list, description="Top insights from EDA")
    # Issues formerly in EDAIssues (now embedded here)
    missing_values: Dict[str, int] = Field(default_factory=dict, description="Missing counts by column")
    outliers: Dict[str, int] = Field(default_factory=dict, description="Outlier counts by column")
    duplicates: int = Field(0, description="Duplicate row count")
    high_cardinality: Dict[str, int] = Field(default_factory=dict, description="High-cardinality categorical columns")
    type_issues: Dict[str, str] = Field(default_factory=dict, description="Type issues by column")
    date_issues: Dict[str, str] = Field(default_factory=dict, description="Date format issues by column")
    column_expectations: Dict[str, ColumnExpectation] = Field(default_factory=dict, description="Expected rules by column")
    validation_issues: List[ValidationIssue] = Field(default_factory=list, description="Validation issues list")
    # Recommendations for DE
    prep_recommendations: List[str] = Field(default_factory=list, description="Data preparation recommendations")
    candidate_features: List[str] = Field(default_factory=list, description="Candidate features to use/engineer")


# -------- 2) DATA ENGINEERING --------

class ProcessingStep(BaseModel):
    step: str = Field(..., description="Processing step")
    columns_affected: List[str] = Field(default_factory=list, description="Affected columns")
    rationale: str = Field(..., description="Why this step is needed")

class PipelineDesign(BaseModel):
    objectives: List[str] = Field(default_factory=list, description="Pipeline objectives")
    steps: List[ProcessingStep] = Field(default_factory=list, description="Processing steps")
    tools: List[str] = Field(default_factory=list, description="Tools & tech")
    storage_format: str = Field("parquet", description="Processed data storage format")
    error_handling: List[str] = Field(default_factory=list, description="Error handling & DQ checks")
    expected_outcomes: List[str] = Field(default_factory=list, description="Expected outcomes")

# -------- 3) MODELING --------

class Metric(BaseModel):
    name: str = Field(..., description="Metric name")
    goal: Literal["maximize", "minimize"] = Field(..., description="Optimization direction")
    threshold: Optional[float] = Field(None, description="Acceptable threshold")
    value: Optional[float] = Field(None, description="Measured value") 
    notes: Optional[str] = Field(None, description="Notes")

class ModelSpec(BaseModel):
    model_type: str = Field(..., description="Model family")
    features: List[str] = Field(default_factory=list, description="Features used")
    target: str = Field(..., description="Target variable")
    training_data: Union[str, Dict[str, Any]] = Field(..., description="Path or descriptor of training data")
    validation_strategy: str = Field(..., description="e.g., k-fold, holdout")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="Hyperparameters")
    assumptions: Optional[str] = None
    limitations: Optional[str] = None
    interpretability: Optional[str] = None

class ModelResult(BaseModel):
    model_spec: ModelSpec
    metrics: List[Metric] = Field(default_factory=list)
    training_time: Optional[float] = None
    analysis: Optional[str] = None
    notes: Optional[str] = None

class DSReport(BaseModel):
    executive_summary: str = Field(..., description="Executive summary of modeling")
    data_understanding: DAReport = Field(..., description="Summary of EDA phase") 
    data_preparation: PipelineDesign = Field(..., description="Summary of data preparation")
    model_results: List[ModelResult] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    business_impact: str = Field(..., description="Potential business impact")
    business_recommendation: str = Field(..., description="Recommendations for business")

# -------- 4) FLOW STATE --------

class FlowState(BaseModel):
    user_request: UserRequest
    ba_report: Optional[BAReport] = None
    eda_issues: Optional[DAReport] = None
    pipeline_design: Optional[PipelineDesign] = None
    ds_report: Optional[DSReport] = None
    need_refine_objective: bool = False
    need_refine_dataset: bool = False
    need_refine_pipeline: bool = False
    need_refine_model: bool = False
