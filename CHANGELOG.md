# Changelog

All notable changes to SemantiCore will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of SemantiCore
- Ontology-first semantic graph platform
- Multi-format data ingestion (CSV, JSON, text, PDF, DOCX)
- LLM-powered ontology proposal generation (Claude, GPT-4)
- Human-in-the-loop ontology refinement
- Neo4j graph storage with ontology versioning
- Natural language query translation to Cypher
- Streamlit-based interactive UI
- Docker deployment support
- Cloud deployment configs (Railway, Render, Fly.io)

## [0.1.0] - 2024-12-18

### Added
- Core platform architecture
- Data ingestion layer with factory pattern
- Pydantic models for all data structures
- Neo4j integration with ontology-as-graph approach
- LLM integration (Anthropic, OpenAI)
- Streamlit UI with 6 pages
- Comprehensive documentation
- Docker and docker-compose setup
- Example datasets

### Features
- CSV, JSON, Text, PDF, DOCX ingestion
- Canonical data normalization
- Provenance tracking
- Ontology proposal with confidence scores
- Feedback loop for iterative refinement
- Instance graph materialization
- Natural language querying
- Transparent Cypher generation

### Documentation
- README with quick start
- Architecture documentation
- Deployment guide
- Usage guide
- Contributing guidelines

[Unreleased]: https://github.com/yourusername/semantic-mapper/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/semantic-mapper/releases/tag/v0.1.0
