# Document-Lens Batch Processing for Research Workflows

This guide demonstrates how to use document-lens batch processing capabilities for large-scale academic research and document corpus analysis.

## Overview

The batch processing system enables researchers to:
- Process thousands of documents efficiently
- Resume interrupted jobs
- Export results in multiple formats (JSONL, CSV, Parquet)
- Track progress and manage large-scale analysis projects

## Quick Start

### 1. Create a Batch Job

```bash
# Create a new batch job for research
curl -X POST "http://localhost:8002/batch/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Academic Paper Corpus Analysis",
    "description": "Large-scale analysis of academic papers for readability and citation patterns",
    "analysis_type": "full",
    "analysis_options": {
      "citation_style": "apa",
      "check_urls": true,
      "check_doi": true,
      "check_plagiarism": false
    },
    "priority": "normal",
    "max_retries": 3
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Academic Paper Corpus Analysis",
  "status": {
    "current_status": "created",
    "total_items": 0,
    "completed_items": 0,
    "failed_items": 0,
    "progress_percentage": 0.0
  }
}
```

### 2. Add Documents to the Job

```bash
# Add documents to process
curl -X POST "http://localhost:8002/batch/jobs/{job_id}/items" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "text": "Document content here...",
      "filename": "paper1.txt",
      "metadata": {
        "author": "Smith, J.",
        "year": "2023",
        "journal": "Journal of Research"
      }
    },
    {
      "text": "Another document...",
      "filename": "paper2.txt",
      "metadata": {
        "author": "Jones, A.",
        "year": "2024",
        "conference": "Academic Conference 2024"
      }
    }
  ]'
```

### 3. Start Processing

```bash
# Start the batch job
curl -X POST "http://localhost:8002/batch/jobs/{job_id}/start"
```

### 4. Monitor Progress

```bash
# Check job status
curl "http://localhost:8002/batch/jobs/{job_id}"

# Get detailed item status
curl "http://localhost:8002/batch/jobs/{job_id}/items?status=completed&limit=10"
```

### 5. Export Results

```bash
# Export to CSV for statistical analysis
curl -X POST "http://localhost:8002/batch/jobs/{job_id}/export" \
  -H "Content-Type: application/json" \
  -d '{
    "export_format": "csv",
    "include_metadata": true,
    "filter_status": ["completed"]
  }'

# Export to Parquet for big data analysis
curl -X POST "http://localhost:8002/batch/jobs/{job_id}/export" \
  -H "Content-Type: application/json" \
  -d '{
    "export_format": "parquet",
    "include_metadata": false
  }'
```

## Research Use Cases

### 1. Large-Scale Readability Analysis

Process thousands of academic papers to analyze readability trends across disciplines:

```python
import requests
import pandas as pd

# Create job for readability analysis
job_data = {
    "name": "Readability Trends in Academic Writing",
    "description": "Analyze readability scores across 10,000 academic papers",
    "analysis_type": "text",  # Focus on text analysis only
    "analysis_options": {},
    "priority": "high"
}

response = requests.post("http://localhost:8002/batch/jobs", json=job_data)
job_id = response.json()["id"]

# Add documents from your corpus
documents = []
for paper in academic_papers:  # Your document collection
    documents.append({
        "text": paper.content,
        "filename": paper.filename,
        "metadata": {
            "discipline": paper.discipline,
            "year": paper.year,
            "venue": paper.venue
        }
    })

# Add in batches of 1000
for i in range(0, len(documents), 1000):
    batch = documents[i:i+1000]
    requests.post(f"http://localhost:8002/batch/jobs/{job_id}/items", json=batch)

# Start processing
requests.post(f"http://localhost:8002/batch/jobs/{job_id}/start")

# Monitor and export when complete
# ... (monitoring code)

# Export results
export_response = requests.post(f"http://localhost:8002/batch/jobs/{job_id}/export", json={
    "export_format": "csv",
    "include_metadata": true
})

download_url = export_response.json()["download_url"]
# Download and analyze results with pandas/R
```

### 2. Citation Pattern Analysis

Analyze citation patterns and academic integrity across a document corpus:

```python
# Create job for citation analysis
job_data = {
    "name": "Citation Pattern Analysis",
    "description": "Analyze citation patterns and detect anomalies",
    "analysis_type": "academic",  # Focus on academic features
    "analysis_options": {
        "citation_style": "apa",
        "check_urls": True,
        "check_doi": True,
        "check_plagiarism": True,  # Enable cross-document checking
        "check_wayback": True
    },
    "priority": "normal"
}

response = requests.post("http://localhost:8002/batch/jobs", json=job_data)
job_id = response.json()["id"]

# Process your research corpus...
# Export results for citation network analysis
```

### 3. Writing Quality Assessment

Assess writing quality metrics across student submissions:

```python
# Educational research: analyze student writing progression
job_data = {
    "name": "Student Writing Progression Study",
    "description": "Longitudinal analysis of student writing quality",
    "analysis_type": "full",
    "analysis_options": {
        "check_plagiarism": False  # Privacy consideration
    }
}

# Add student papers with temporal metadata
documents = []
for submission in student_submissions:
    documents.append({
        "text": submission.text,
        "filename": f"{submission.student_id}_{submission.assignment}.txt",
        "metadata": {
            "student_id": submission.student_id,
            "assignment_type": submission.assignment_type,
            "semester": submission.semester,
            "year": submission.year,
            "grade_level": submission.grade_level
        }
    })

# Process and export for longitudinal analysis
```

## Python Research Library

Here's a convenient Python wrapper for research workflows:

```python
import requests
import time
from typing import List, Dict, Optional

class DocumentLensResearch:
    """Python wrapper for document-lens batch processing research workflows"""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url

    def create_research_job(self,
                          name: str,
                          description: str = None,
                          analysis_type: str = "full",
                          citation_style: str = "apa",
                          check_plagiarism: bool = False) -> str:
        """Create a new batch job for research"""

        job_data = {
            "name": name,
            "description": description,
            "analysis_type": analysis_type,
            "analysis_options": {
                "citation_style": citation_style,
                "check_urls": True,
                "check_doi": True,
                "check_plagiarism": check_plagiarism,
                "check_wayback": True
            },
            "priority": "normal",
            "max_retries": 3
        }

        response = requests.post(f"{self.base_url}/batch/jobs", json=job_data)
        response.raise_for_status()
        return response.json()["id"]

    def add_documents(self, job_id: str, documents: List[Dict]) -> None:
        """Add documents to a batch job"""

        # Process in chunks of 1000
        for i in range(0, len(documents), 1000):
            chunk = documents[i:i+1000]
            response = requests.post(
                f"{self.base_url}/batch/jobs/{job_id}/items",
                json=chunk
            )
            response.raise_for_status()
            print(f"Added documents {i+1} to {min(i+1000, len(documents))}")

    def start_job(self, job_id: str) -> None:
        """Start processing a batch job"""
        response = requests.post(f"{self.base_url}/batch/jobs/{job_id}/start")
        response.raise_for_status()
        print(f"Job {job_id} started")

    def wait_for_completion(self, job_id: str, check_interval: int = 30) -> Dict:
        """Wait for job completion with progress updates"""

        while True:
            response = requests.get(f"{self.base_url}/batch/jobs/{job_id}")
            response.raise_for_status()
            job_info = response.json()

            status = job_info["status"]["current_status"]
            progress = job_info["status"]["progress_percentage"]

            print(f"Job {job_id}: {status} - {progress:.1f}% complete")

            if status in ["completed", "failed", "cancelled"]:
                return job_info

            time.sleep(check_interval)

    def export_results(self, job_id: str, format: str = "csv", include_metadata: bool = True) -> str:
        """Export job results and return download URL"""

        export_data = {
            "export_format": format,
            "include_metadata": include_metadata,
            "filter_status": ["completed"]
        }

        response = requests.post(
            f"{self.base_url}/batch/jobs/{job_id}/export",
            json=export_data
        )
        response.raise_for_status()

        return response.json()["download_url"]

# Usage example
researcher = DocumentLensResearch()

# Create and run a research job
job_id = researcher.create_research_job(
    "Large Scale Academic Analysis",
    "Analyzing 10,000 academic papers for citation patterns"
)

# Add your documents
documents = [
    {
        "text": paper.content,
        "filename": paper.filename,
        "metadata": paper.metadata
    }
    for paper in your_document_corpus
]

researcher.add_documents(job_id, documents)
researcher.start_job(job_id)
final_status = researcher.wait_for_completion(job_id)

# Export results
download_url = researcher.export_results(job_id, format="parquet")
print(f"Results available at: {download_url}")
```

## Performance and Scaling

### Recommended Batch Sizes

- **Small jobs**: 1-100 documents
- **Medium jobs**: 100-1,000 documents
- **Large jobs**: 1,000-10,000 documents
- **Research corpus**: 10,000+ documents

### Processing Time Estimates

- **Text analysis only**: ~0.1-0.5 seconds per document
- **Academic analysis**: ~0.5-2 seconds per document
- **Full analysis**: ~1-3 seconds per document

### Memory and Storage

- **Memory usage**: ~50-100MB per concurrent job
- **Export files**: CSV (~1KB per document), Parquet (~500B per document)
- **Export retention**: 7 days

## Integration with Analysis Tools

### Pandas Integration

```python
import pandas as pd

# Load batch results
df = pd.read_csv(download_url)

# Analyze readability trends
readability_by_year = df.groupby('metadata_year')['result_flesch_reading_ease'].mean()

# Citation analysis
citation_stats = df['result_citations_count'].describe()
```

### R Integration

```r
library(readr)
library(dplyr)

# Load batch results
data <- read_csv(download_url)

# Statistical analysis
readability_model <- lm(flesch_reading_ease ~ year + discipline, data = data)
summary(readability_model)
```

### Jupyter Notebook Example

See the complete research workflow example in `docs/examples/research-workflow.ipynb`.

## Error Handling and Recovery

### Resume Failed Jobs

```python
# Check for failed items
failed_items = researcher.get_job_items(job_id, status="failed")

# Retry failed items
researcher.retry_failed_items(job_id)
```

### Monitoring and Alerts

```python
# Set up monitoring
def monitor_job(job_id, alert_email=None):
    job_info = researcher.wait_for_completion(job_id)

    if job_info["status"]["current_status"] == "completed":
        success_rate = job_info["status"]["completed_items"] / job_info["status"]["total_items"]
        if success_rate < 0.95:  # Alert if success rate < 95%
            send_alert(f"Job {job_id} completed with {success_rate:.1%} success rate")
```

This batch processing system enables large-scale document analysis for academic research, providing robust, scalable, and resumable processing of document corpora with comprehensive export capabilities.