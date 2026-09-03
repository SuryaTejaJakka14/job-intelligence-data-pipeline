# Job Intelligence Data Pipeline

A scheduled Python pipeline that collects job listings, processes them in parallel, applies filtering and duplicate-detection rules, stores structured results, and produces optional email reports.

This project was built as a practical data-engineering and automation system for turning unstructured job-listing inputs into a searchable, trackable workflow. It demonstrates scheduled orchestration, concurrent processing, data-quality controls, database persistence, and reporting.


## Highlights

- Scheduled pipeline execution through `main_parallel_scheduled.py`
- Parallel job-processing workflow
- Job filtering based on configurable criteria
- Duplicate detection to reduce repeated listings
- Structured persistence through the database layer
- Optional email reporting and preview generation
- Configurable scheduling and runtime behavior
- Test scaffolding for filtering, duplicate detection, and reporting

## Architecture

```text
Job Sources / Input Data
          |
          v
Scraper and Collection Layer
          |
          v
Parallel Processing Workflow
          |
          +--> Validation and Filtering
          |
          +--> Duplicate Detection
          |
          v
Database / Application Tracking
          |
          v
Reports and Optional Email Notifications
```

## Project flow

1. `main_parallel_scheduled.py` starts the scheduled orchestration process.
2. The scheduler reads runtime settings from the configuration modules.
3. The parallel workflow launches the job-collection and processing tasks.
4. Job records are filtered and checked for duplicates.
5. Valid records are written through the database layer.
6. The pipeline can generate summaries and optional email reports.

## Entry point

The current scheduled entry point is:

```bash
python main_parallel_scheduled.py
```

`main_parallel_scheduled.py` is responsible for triggering the scheduled workflow. It coordinates the configured schedule with the parallel processing pipeline.

For a one-time or development run, inspect the available runner scripts before using:

```bash
python main.py
python main_parallel.py
```

## Repository structure

```text
.
├── main_parallel_scheduled.py  # Scheduled orchestration entry point
├── main_parallel.py            # Parallel pipeline runner
├── main.py                     # Standard pipeline runner
├── scraper.py                  # Job collection logic
├── scraper_parallel.py         # Concurrent collection/processing logic
├── database.py                 # Data persistence and tracking layer
├── config.py                   # Application configuration
├── scheduler_config.py         # Scheduling configuration
├── check_duplicates.py         # Duplicate-detection logic
├── email_sender.py             # Optional email reporting
├── test_filtering.py           # Filtering tests
├── test_deduplication.py       # Duplicate-detection tests
├── test_email_send.py          # Email-reporting tests
├── requirements.txt            # Python dependencies
└── data/sample/                # Synthetic sample data only
```

## Setup

### Prerequisites

- Python 3.10 or newer
- `pip`
- A virtual environment is recommended
- Browser driver and browser setup may be required if the configured collector uses browser automation
- A local database or configured database connection, depending on your `database.py` configuration

### 1. Clone the repository

```bash
git clone https://github.com/SuryaTejaJakka14/Job_bot.git
cd Job_bot
```

### 2. Create and activate a virtual environment

macOS and Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure local settings

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Then update only your local `.env` file with any database, scheduler, browser, or notification settings required by your environment.

Never commit `.env`, credentials, real application history, browser-profile data, or personally identifiable information.

### 5. Run the scheduled pipeline

```bash
python main_parallel_scheduled.py
```

For development, use a safe test configuration, small sample input, and notifications disabled.

## Sample data

The public version of this project should include only synthetic data under:

```text
data/sample/
```

The sample records are intended to demonstrate the data model and pipeline flow without exposing real job applications, recruiter contacts, or scraped site content.

## Configuration

Configuration is currently managed through:

- `config.py`
- `scheduler_config.py`

Before publishing or sharing this repository, move secrets and personal configuration values to a local `.env` file. Keep only placeholder values in `.env.example`.

Typical configuration areas include:

- Database connection settings
- Scheduler interval or run time
- Parallel worker count
- Search/filter criteria
- Browser automation settings
- Notification settings
- Email/SMTP credentials

## Testing

Run the test suite with:

```bash
pytest -q
```

The initial test focus should cover:

- Filtering rules
- Duplicate detection
- Database write behavior
- Invalid or incomplete record handling
- Scheduler configuration parsing
- Mocked notification behavior

## Responsible use

This project is intended for personal workflow automation, data engineering practice, and analysis of job-listing data.

- Respect website terms of service, robots.txt directives, rate limits, and applicable laws.
- Prefer approved APIs, feeds, user-provided exports, or synthetic data when available.
- Do not bypass access controls, CAPTCHAs, authentication protections, or anti-bot systems.
- Do not commit personal data, credentials, real application history, recruiter information, or copied web-page captures.
- Use low request rates and clear limits when testing any collection component.

## Current limitations

- Collector behavior may depend on website layout and availability.
- Browser automation can require local driver and browser configuration.
- The public version is designed around synthetic sample data rather than live personal application records.
- Email reporting should be disabled by default and covered with mocked tests.
- The project will benefit from a package-based `src/` layout and a more formal command-line interface.

## Roadmap

- [ ] Move modules into a package-based `src/job_pipeline/` structure
- [ ] Add `.env.example` and environment-based configuration
- [ ] Add synthetic sample data and a data generator
- [ ] Add a repeatable database initialization command
- [ ] Add stronger unit and integration tests
- [ ] Add structured logging
- [ ] Add a command-line interface for one-time and scheduled runs
- [ ] Add Docker support for reproducible local execution
- [ ] Add pipeline metrics and run summaries
- [ ] Add architecture diagrams and sanitized screenshots

## Technologies

- Python
- Parallel processing
- Scheduled automation
- Data filtering and validation
- Duplicate detection
- Database persistence
- Email reporting
- Browser automation and/or HTML parsing, depending on configured collectors

## Author

Surya Teja Jakka  
Data & IoT Engineer | Data Pipelines | Automation | Sensor and Time-Series Data

- LinkedIn: <https://www.linkedin.com/in/teja-j14/>
- GitHub: <https://github.com/SuryaTejaJakka14>
