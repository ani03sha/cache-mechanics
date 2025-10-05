# Cache Mechanics

Educational implementation of cache data structures and strategies, with focus on understanding cache behavior, inconsistencies, and eviction policies.

## Project Structure

```
cache-mechanics/
├── src/cache_mechanics/     # In-depth cache implementations (future work)
├── examples/                 # Blog post code snippets
│   └── inconsistencies/     # Cache inconsistency demonstrations
├── tests/                    # Test suite
└── pyproject.toml           # Project configuration
```

## Quick Start

### Installation

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Running Examples

Blog post examples are standalone scripts:

```bash
python examples/inconsistencies/your_example.py
```

## Development

### Testing

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy src/
```

## License

MIT License - see LICENSE file for details.
