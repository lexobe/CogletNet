# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Testing
- Run tests: `pytest tests/`
- Run specific test: `python run_test.py` (configured for debugging)
- Run with coverage: `pytest tests/ --cov=cogletnet --cov-report=term-missing`
- Test specific modules:
  - `pytest tests/core/` - Core functionality tests
  - `pytest tests/utils/` - Utility function tests

### Code Quality
- Format code: `black src/ tests/`
- Sort imports: `isort src/ tests/`
- Type checking: `mypy src/`
- Run pre-commit hooks: `pre-commit run --all-files`

### Package Management
- Install for development: `pip install -e ".[dev]"`
- Install dependencies: `pip install -r requirements.txt`

## High-Level Architecture

CogletNet is a cognitive network implementation using vector storage and memory anchor mechanisms for AI reasoning.

### Core Components

**CogletNet (`src/cogletnet/core/cogletnet.py`)**: Main orchestrator that coordinates thinking processes
- Manages LLM interactions with configurable prompts and parameters
- Implements multi-cycle thinking loops with `think()` and `think_loop()` methods
- Integrates vector storage, memory mechanisms, and cognitive elements

**Coglets (`src/cogletnet/core/coglets.py`)**: Memory management layer
- Integrates VectorStore and MAM (Memory Anchor Mechanism)
- Handles cognitive element (coglet) lifecycle: add, recall, update weights, delete
- Manages coglet sets and batch operations

**VectorStore (`src/cogletnet/core/vector_store.py`)**: Upstash Vector backend interface
- Implements CRUD operations for cognitive elements
- Handles similarity search with configurable thresholds
- Manages metadata serialization and batch operations

**MAM (`src/cogletnet/core/mam.py`)**: Memory Anchor Mechanism calculations
- Computes memory weights using time decay and access patterns
- Implements golden ratio-based memory activation selection
- Provides mathematical foundation for memory prioritization

### Key Architectural Patterns

1. **Layered Architecture**: CogletNet → Coglets → VectorStore/MAM
2. **Configuration-Driven**: Extensive configuration objects for all components
3. **Memory Management**: Time-based weight decay with access frequency boosting
4. **LLM Integration**: Structured JSON responses with retry mechanisms
5. **Batch Operations**: Optimized for bulk cognitive element operations

### Configuration Structure

The system uses nested configuration dictionaries:
- `storage_config`: Upstash connection details and set management
- `llm_config`: Model selection, retries, temperature settings
- `memory_config`: MAM parameters (beta, gamma, golden ratio, etc.)
- `thinking_config`: Cognitive loop limits and behavior
- `prompts_config`: Customizable system prompts for different roles

### Data Flow

1. **Input** → CogletNet.think() → **Memory Recall** via Coglets
2. **Similar Memories** → **MAM Selection** → **Activated Memories**
3. **Prompt Construction** → **LLM Call** → **JSON Response**
4. **Memory Weight Updates** → **New Coglet Generation** (optional)

### Testing Strategy

- Unit tests for individual components in `tests/core/`
- Integration tests with real vector storage operations
- Utility function tests in `tests/utils/`
- Real-world scenario testing with actual LLM interactions

### Environment Setup

Required environment variables:
- `UPSTASH_URL`: Vector database endpoint
- `UPSTASH_TOKEN`: Authentication token

The system uses `python-dotenv` for environment variable management.

### Code Quality Standards

- Type hints required (mypy enforcement)
- Black code formatting (88 character line length)
- Import sorting with isort (black profile)
- Pre-commit hooks for automated quality checks
- Comprehensive test coverage requirements