"""Offline sample source.

Returns a small, deterministic set of postings so the pipeline can be demoed
and tested without network access or API keys. Data here is synthetic.
"""

from __future__ import annotations

from typing import Dict, List

from ..models import Job

# A handful of synthetic postings per country, spanning our four regions.
_SAMPLE: Dict[str, List[dict]] = {
    "us": [
        {
            "id": "us-1",
            "title": "Senior Backend Engineer (Python)",
            "company": "Acme Cloud",
            "location": "San Francisco, CA",
            "description": (
                "Build scalable Python microservices and REST APIs on AWS. "
                "Kubernetes, PostgreSQL, CI/CD. We sponsor H1B for the right "
                "candidate."
            ),
            "url": "https://example.com/us-1",
        },
        {
            "id": "us-2",
            "title": "Data Engineer",
            "company": "Northwind Analytics",
            "location": "Austin, TX",
            "description": (
                "ETL pipelines with Airflow and Spark. SQL, Python, dbt, "
                "Snowflake. Visa sponsorship available."
            ),
            "url": "https://example.com/us-2",
        },
    ],
    "gb": [
        {
            "id": "gb-1",
            "title": "Platform Engineer",
            "company": "Thames Fintech",
            "location": "London",
            "description": (
                "Terraform, Kubernetes, AWS and Python tooling for our "
                "platform team. English-speaking team."
            ),
            "url": "https://example.com/gb-1",
        },
    ],
    "nl": [
        {
            "id": "nl-1",
            "title": "Backend Developer (English-speaking)",
            "company": "Amsterdam Labs",
            "location": "Amsterdam",
            "description": (
                "Python, FastAPI, PostgreSQL. Our engineering language is "
                "English. Relocation supported."
            ),
            "url": "https://example.com/nl-1",
        },
    ],
    "sg": [
        {
            "id": "sg-1",
            "title": "Software Engineer, Backend",
            "company": "Marina Pay",
            "location": "Singapore",
            "description": (
                "Golang and Python services, Kubernetes, gRPC. High-growth "
                "payments company."
            ),
            "url": "https://example.com/sg-1",
        },
    ],
    "au": [
        {
            "id": "au-1",
            "title": "Senior Python Engineer",
            "company": "Reef Digital",
            "location": "Sydney",
            "description": (
                "Django, DRF, PostgreSQL and AWS. Visa sponsorship for "
                "skilled migrants considered."
            ),
            "url": "https://example.com/au-1",
        },
    ],
}


class SampleSource:
    name = "sample"

    def search(
        self, query: str, country: str, region: str, limit: int
    ) -> List[Job]:
        rows = _SAMPLE.get(country, [])
        jobs: List[Job] = []
        for row in rows[:limit]:
            jobs.append(
                Job(
                    source="sample",
                    source_id=row["id"],
                    title=row["title"],
                    company=row["company"],
                    location=row["location"],
                    country=country,
                    region=region,
                    description=row["description"],
                    url=row["url"],
                )
            )
        return jobs
