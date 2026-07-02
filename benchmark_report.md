# TalentIQ Candidate Sourcing & Scoring Benchmark Report

## Execution Summary
* **Candidates Processed**: 10
* **Total Pipeline Execution Time**: 22.3725 seconds
* **Average Processing Time per Candidate**: 2.2372 seconds

## Pipeline Stages Timing Detail
| Pipeline Stage | Actual Duration (seconds) | Metric Description |
| :--- | :--- | :--- |
| **Job Description Upload Time** | 0.0006 | Save Job Description PDF metadata to database store |
| **Resume Upload Time** | 0.0031 | Upload and save 10 Resumes metadata to store |
| **PDF Extraction Time** | 0.1175 | PyMuPDF text extraction from all PDFs |
| **Gemini JD Parsing Time** | 0.2131 | Extract structured schema from JD text (AI Model) |
| **Resume Parsing Time** | 1.5673 | Parallelizable parsing of all 10 Resumes (AI Model) |
| **Embedding Generation Time** | 16.4177 | Local SentenceTransformer embedding of profiles |
| **FAISS Index Creation Time** | 0.0004 | Build IndexFlatIP vector database |
| **Candidate Scoring Time** | 2.4438 | Multi-criteria scoring matching algorithms |
| **Ranking Time** | 0.0001 | Sort, index, and organize candidates |
| **Explainability Time** | 1.5705 | Formulate natural language insights per candidate |
| **Analytics Generation Time** | 0.0001 | Run gap analysis and aggregate job metrics |
| **Excel Export Time** | 0.0245 | Generate OpenPyXL candidate matrix |
| **PDF Export Time** | 0.0136 | Render ReportLab recruiter executive report |
| **Total End-to-End Processing Time** | 22.3725 | Complete execution flow |

## Candidate Matching Metrics
* **Average Overall Match Score**: 60.62%
* **Highest Match Score**: 91.02%
* **Lowest Match Score**: 37.72%
* **Average Skill Match**: 40.00%
* **Average Semantic Similarity**: 72.03%
* **Average Experience Match**: 78.00%

## Detailed Rankings
| Rank | Candidate Name | Overall Score | Skill Match | Semantic Match | Experience Match |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | John Smith | 91.02% | 100.0% | 79.35% | 100.0% |
| 2 | Grace Davis | 83.75% | 85.71% | 81.43% | 100.0% |
| 3 | Jane Doe | 77.55% | 57.14% | 82.19% | 100.0% |
| 4 | Charlie Green | 74.59% | 57.14% | 80.18% | 100.0% |
| 5 | Frank Miller | 62.61% | 42.86% | 77.88% | 80.0% |
| 6 | Bob Brown | 57.73% | 28.57% | 74.60% | 80.0% |
| 7 | Eva Black | 43.56% | 0.0% | 66.19% | 100.0% |
| 8 | Alice Johnson | 39.35% | 14.29% | 58.12% | 40.0% |
| 9 | Henry Wilson | 38.32% | 14.29% | 63.61% | 20.0% |
| 10 | David White | 37.72% | 0.0% | 56.74% | 60.0% |
