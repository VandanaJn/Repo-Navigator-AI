# Repo-Navigator-AI

<img src="assets/Repo Navigator AI Logo.png" alt="Repo Navigator AI" width="30%"/>


A master agent for analyzing GitHub repositories and answering architecture questions using LLMs and tool-augmented agents.

## Features
- Analyzes public GitHub repositories and summarizes their structure and code flow.
- Delegates architecture questions to specialized sub-agents.
- Uses tool calls to extract owner/repo from URLs and fetch repo/file content.
- Integration tests with deterministic GitHub responses for CI stability.
- Configurable evaluation metrics for response and tool usage matching.
- Uses Google ADK to code multi agent system
- Deploys the agent to Vertex AI
- GitHub CI and CD workflows


## Problem & Solution
- **Problem (The "Why")**: Large, evolving codebases create heavy context-switching and wasted time; LLMs alone struggle to accurately analyze multi-file repositories and often hallucinate or miss execution flow, making onboarding and code review slow and error-prone.
- **Solution (The "What")**: Repo Navigator Agent — an autonomous, deterministic multi-agent system built on Google ADK that layers tool calls and specialized sub-agents to reliably extract repository context, fetch files, and produce concise, deterministic architecture summaries.

## Architecture

<img src="assets/Repo Navigator AI Architecture.png" alt="Repo Navigator AI Architecture" />
  

## Quick Start

### 1. Install dependencies
```powershell
make install
```

### 2. Set up environment variables
Create a `.env` file with your API keys:
```
GOOGLE_API_KEY=your_google_key
GITHUB_TOKEN=your_github_token
```

#### How to get a GitHub Token
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens).
2. Click **Generate new token** (classic or fine-grained).
3. Select scopes: at minimum, choose `repo` (for public repos) and `read:user`.
4. Copy the generated token and paste it as `GITHUB_TOKEN` in your `.env` file.
5. Keep your token secret and never commit `.env` to source control.

#### How to get a Google API Key
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project.
3. Create a api key in google api studio for your project https://aistudio.google.com/app/api-keys
5. Copy the generated key and paste it as `GOOGLE_API_KEY` in your `.env` file.
6. Enable the required APIs (e.g., Gemini, Vertex AI, or other relevant services) for your project.
7. Keep your API key secret and never commit `.env` to source control.


### 3. Run tests
```powershell
make test
```

## Makefile Targets
You can use the provided Makefile to run common tasks:

| Target   | Description                                 |
|----------|---------------------------------------------|
| install  | Create venv and install dependencies        |
| run      | Run the ADK agent (dev)                     |
| web      | Start the ADK web server (dev)              |
| test     | Run all tests with coverage                 |
| clean    | Remove the virtual environment              |

### Usage (Windows PowerShell)
```powershell
# Install dependencies and create venv
make install

# Run the ADK agent
make run

# Start the ADK web server
make web

# Run tests with coverage
make test

# Remove the virtual environment
make clean
```

### Usage (Linux/macOS)
```bash
make install
make run
make web
make test
make clean
```

## Testing & CI
- Integration tests use a `FakeGithub` client (see `tests/integration/conftest.py`) for deterministic repo/file responses.
- LLM calls are live 
- Evaluation thresholds are set in `tests/integration/test_files/*/test_config.json`.


## Project Structure
```
Repo-Navigator-AI/
├── agents/
│   └── repo_navigator/
│       ├── agent.py
│       └── sub_agents/
│           ├── architecture_agent.py
│           ├── file_summarizer_agent.py
│           └── tools/
│               └── githubtools.py
├── tests/
│   ├── integration/
│   │   ├── conftest.py
│   │   └── test_files/
│   └── unit/
├── requirements.txt
├── .env
└── README.md
```

## Customization
- To change evaluation thresholds, edit the relevant `test_config.json` files.
- To add new tools or sub-agents, extend `agent.py` and `sub_agents/`.

## Deployment

### Deploy to Vertex AI

This project uses GitHub Actions to automatically deploy the ADK agent to Google Cloud Vertex AI. The deployment workflow is defined in `.github/workflows/deploy_adk.yml`.

#### Prerequisites
- A Google Cloud project with Vertex AI enabled.
- A GCP service account with appropriate permissions for Vertex AI.
- GitHub secrets configured:
  - `GCP_SA_KEY` — JSON key for the GCP service account.
  - `PROJECT_ID` — Your Google Cloud project ID.

#### Automatic Deployment
Pushing to the `main` branch triggers automatic deployment via GitHub Actions.

## License
See `LICENSE` for details.

## Maintainer
VandanaJn

