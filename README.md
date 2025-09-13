# cosmic-django

[![CI](https://github.com/brunodantas/cosmic-django/actions/workflows/ci.yml/badge.svg)](https://github.com/brunodantas/cosmic-django/actions/workflows/ci.yml)
[![Test Matrix](https://github.com/brunodantas/cosmic-django/actions/workflows/test-matrix.yml/badge.svg)](https://github.com/brunodantas/cosmic-django/actions/workflows/test-matrix.yml)
[![Code Quality](https://github.com/brunodantas/cosmic-django/actions/workflows/code-quality.yml/badge.svg)](https://github.com/brunodantas/cosmic-django/actions/workflows/code-quality.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.2+](https://img.shields.io/badge/django-5.2+-green.svg)](https://djangoproject.com/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Example project applying the patterns from [Cosmic Python](https://www.cosmicpython.com/) by Harry Percival and Bob Gregory. This project demonstrates how to build maintainable, testable Django applications using Domain-Driven Design principles while leveraging Django's strengths.

📖 **Read the full post**: [Cosmic Django](https://brunodantas.github.io/blog/2025/09/12/cosmic-django)

## ✨ Features

- **Domain modeling plus helper functions**
- **No Repository Pattern**
- **Service Layer Pattern**
- **Atomic transactions**
- **Design by contract**
- **Event-driven architecture with signals**
- **Command-query responsibility segregation**


## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/brunodantas/cosmic-django.git
cd cosmic-django

# Install dependencies
make install dev-install

# Set up the database (sqlite)
make migrate

# Run tests to verify installation
make test

# Start development server
make runserver
```

## 🛠️ Development

### Commands

The project includes a Makefile for development tasks.

## 📊 Dependency Visualization

Generate and view the project's dependency graph.

Needs to uncomment the imports from this init file beforehand.

```bash
# Generate dependency graph
pydeps cosmic/__init__.py
```

![Dependency Graph](dependency_graph.svg)

## 📚 Learning Resources

- [Cosmic Python Book](https://www.cosmicpython.com/) - The inspiration for this project
- [Django Documentation](https://docs.djangoproject.com/) - Official Django guide
- [Domain-Driven Design](https://martinfowler.com/tags/domain%20driven%20design.html) - Martin Fowler's DDD resources

## 📄 License

This project is licensed under the GPL License - see the [LICENSE](LICENSE) file for details.
