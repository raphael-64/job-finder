import json
from firecrawl import FirecrawlApp
from pydantic import BaseModel
from typing import List

# Initialize the FirecrawlApp with your API key
app = FirecrawlApp(api_key='INSERT YOUR API KEY')

# Define the schema for extracted job data
class Job(BaseModel):
    title: str
    location: str
    description: str
    requirements: str

class ExtractSchema(BaseModel):
    jobs: List[Job]

def chunk_list(data, chunk_size):
    """Split the list into chunks of specified size."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def map_and_extract_jobs(base_url: str):
    # Step 1: Map URLs
    print("Finding all urls..")
    map_result = app.map_url(base_url, params={
        'includeSubdomains': True,
        'search': 'careers'
    })

    mapped_urls = map_result.get('links', [])
    mapped_urls = mapped_urls[0:10]

    if not mapped_urls:
        print("No URLs found related to careers.")
        return []

    # Step 2: Extract job data in batches of 10
    print("Extracting job data...")
    all_jobs = []

    for batch in chunk_list(mapped_urls, 10):
        extraction_result = app.extract(batch, {
            'prompt': 'Extract a list of jobs including the job title, location, description, and requirements.',
            'schema': ExtractSchema.model_json_schema(),
        })
        jobs = extraction_result.get('data', {}).get('jobs', [])
        all_jobs.extend(jobs)

    return all_jobs

def write_to_file(data, filename="jobs.json"):
    """Write data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Job data written to {filename}")

if __name__ == "__main__":
    input_url = input("Enter the base URL of the company (e.g., https://openai.com): ")
    jobs = map_and_extract_jobs(input_url)

    if jobs:
        print(f"Extracted {len(jobs)} job postings as JSON:")
        
        # Pretty-print JSON to the console
        jobs_json = json.dumps(jobs, ensure_ascii=False, indent=4)
        print(jobs_json)
        
        # Write JSON data to a file
        write_to_file(jobs)
    else:
        print("No job postings found.")
