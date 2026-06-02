"""
Data sources for AI bias analysis.

This project does not generate original bias measurements. It aggregates
and displays published research.
"""

from dataclasses import dataclass
from typing import Any, List


@dataclass
class DataSource:
    """A citable, auditable data source."""

    name: str
    url: str
    description: str
    license: str
    citation: str
    is_mock: bool  # True if synthetic/demo data


# ---------------------------------------------------------------------------
# Real public datasets (summaries only — we do not reproduce raw data)
# ---------------------------------------------------------------------------

COMPAS_SOURCE = DataSource(
    name="ProPublica COMPAS Recidivism Analysis",
    url="https://github.com/propublica/compas-analysis",
    description=(
        "ProPublica's 2016 investigation into the COMPAS recidivism risk-score "
        "tool used in Broward County, Florida. The analysis examined roughly "
        "7,000 arrestees scored by COMPAS between 2013 and 2014."
    ),
    license="Apache 2.0 (data); see repository for details",
    citation=(
        "Angwin, J., Larson, J., Mattu, S., & Kirchner, L. (2016). "
        '"Machine Bias." ProPublica, May 23, 2016. '
        "https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing"
    ),
    is_mock=False,
)


def get_compas_summary() -> dict[str, Any]:
    """Return a summary of the ProPublica COMPAS recidivism analysis.

    **Important**: This is a SUMMARY of published public research, not our
    own analysis. The numbers below come from ProPublica's publicly released
    methodology and data repository.

    Source
    ------
    ProPublica, "Machine Bias", May 23 2016.
    https://github.com/propublica/compas-analysis
    """
    return {
        "source": COMPAS_SOURCE.name,
        "source_url": COMPAS_SOURCE.url,
        "citation": COMPAS_SOURCE.citation,
        "is_mock": False,
        "methodology_note": (
            "This is a SUMMARY of ProPublica's published research. "
            "We did not perform this analysis ourselves."
        ),
        "key_findings": [
            (
                "Black defendants were roughly twice as likely as white "
                "defendants to be misclassified as higher risk but not "
                "actually re-offend (false positive)."
            ),
            (
                "White defendants were more likely to be misclassified as "
                "lower risk but go on to commit additional crimes "
                "(false negative)."
            ),
            (
                "Overall prediction accuracy was similar across racial "
                "groups (~60%), but error types were distributed unevenly."
            ),
        ],
        "dataset_size_approx": 7_000,
        "time_period": "2013-2014",
        "jurisdiction": "Broward County, Florida, USA",
    }


# ---------------------------------------------------------------------------
# Mock / demo data — clearly labelled as synthetic
# ---------------------------------------------------------------------------

_MOCK_VIOLATIONS: list[dict[str, Any]] = [
    {
        "id": "MOCK-001",
        "system_name": "Demo System Alpha",
        "description": (
            "Synthetic example: demographic parity gap exceeds threshold "
            "in loan-approval demo model."
        ),
        "affected_count": 1_200,
        "severity": "high",
        "source": "MOCK - Not Real Data",
        "created_at": "2026-01-15T00:00:00Z",
    },
    {
        "id": "MOCK-002",
        "system_name": "Test Healthcare AI",
        "description": (
            "Synthetic example: predictive model under-refers patients from "
            "underrepresented group in simulated triage scenario."
        ),
        "affected_count": 340,
        "severity": "medium",
        "source": "MOCK - Not Real Data",
        "created_at": "2026-02-01T00:00:00Z",
    },
    {
        "id": "MOCK-003",
        "system_name": "Example Hiring Screener",
        "description": (
            "Synthetic example: resume-screening model shows statistically "
            "significant score disparity across gender in test dataset."
        ),
        "affected_count": 870,
        "severity": "high",
        "source": "MOCK - Not Real Data",
        "created_at": "2026-03-10T00:00:00Z",
    },
    {
        "id": "MOCK-004",
        "system_name": "Demo Recidivism Scorer",
        "description": (
            "Synthetic example: risk-score calibration differs by more than "
            "5 percentage points between racial groups in test data."
        ),
        "affected_count": 2_100,
        "severity": "critical",
        "source": "MOCK - Not Real Data",
        "created_at": "2026-04-22T00:00:00Z",
    },
]


def get_mock_violations() -> list[dict[str, Any]]:
    """Return clearly-labelled mock violation data for demos and tests.

    Every record has ``source='MOCK - Not Real Data'``. These are synthetic
    examples used for UI development and testing -- they do not represent
    real incidents.
    """
    return [v.copy() for v in _MOCK_VIOLATIONS]


# ---------------------------------------------------------------------------
# Data-loading stub (not yet implemented)
# ---------------------------------------------------------------------------


def load_data_source(source: DataSource) -> list[dict[str, Any]]:
    """Download and cache data from the source URL.

    Not yet implemented -- currently returns mock data with a warning.

    When implemented this function will:
    1. Check a local cache directory for a previously downloaded copy.
    2. If not cached, download the dataset from ``source.url``.
    3. Parse into a list of dicts suitable for analysis.
    4. Cache the result locally for subsequent calls.

    Parameters
    ----------
    source : DataSource
        The data source to load.

    Returns
    -------
    list[dict]
        Parsed records from the source. Until real loading is implemented,
        returns mock data so callers have a consistent return type.
    """
    print(
        f"WARNING: load_data_source() is not yet implemented. "
        f"Returning mock data instead of real data from '{source.name}'. "
        f"See {source.url} to download the dataset manually."
    )
    return get_mock_violations()
