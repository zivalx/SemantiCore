# Contributing to Semantic Mapper

Thank you for your interest in contributing to Semantic Mapper!

## Development Setup

```bash
# Clone repository
git clone <repository-url>
cd semantic_mapper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Start Neo4j (Docker)
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.15-community

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run application
./scripts/start.sh  # or start.bat on Windows
```

## Code Standards

### Python Style
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Format with `black`
- Lint with `ruff`

```bash
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

### Documentation
- Clear, concise docstrings
- Update README.md for new features
- Add examples for new functionality

### Testing
```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=semantic_mapper tests/
```

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/your-feature`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Ensure** all tests pass
6. **Format** code with `black`
7. **Commit** with clear messages
8. **Push** to your fork
9. **Submit** a pull request

### Commit Messages
```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Example:**
```
feat: add PDF ingestion support

- Implement PDFIngester class
- Add PyPDF dependency
- Update documentation

Closes #42
```

## Areas for Contribution

### High Priority
- [ ] Automatic instance materialization (LLM-based mapping)
- [ ] Relationship extraction from text
- [ ] Visual ontology editor
- [ ] Query result visualization

### Medium Priority
- [ ] Additional data format support (Excel, XML)
- [ ] Entity resolution and deduplication
- [ ] Batch import with progress tracking
- [ ] Export to OWL/RDF

### Low Priority
- [ ] Multi-language support
- [ ] Custom themes
- [ ] Advanced caching
- [ ] Plugin system

## Questions or Issues?

- **Bugs:** Open an issue with steps to reproduce
- **Features:** Open an issue describing the use case
- **Questions:** Check existing issues or open a discussion

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
