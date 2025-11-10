# Contributing to HalalScanner

Thank you for your interest in contributing to HalalScanner! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - System information (OS, browser, etc.)

### Suggesting Features

1. Check if the feature has been suggested
2. Create an issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach

### Code Contributions

#### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/your-username/HalalScanner.git
cd HalalScanner

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Mobile app setup
cd ../mobile
npm install

# Admin console setup
cd ../admin
npm install
```

#### Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards

3. Write/update tests:
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd mobile
   npm test
   ```

4. Run linters:
   ```bash
   # Python
   black app/
   flake8 app/

   # TypeScript/JavaScript
   npm run lint
   ```

5. Commit your changes:
   ```bash
   git commit -m "feat: add new feature"
   ```

   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring
   - `style:` Formatting changes
   - `chore:` Build/config changes

6. Push and create a Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

#### Pull Request Guidelines

- Link related issues
- Provide clear description of changes
- Include screenshots for UI changes
- Ensure all tests pass
- Update documentation if needed
- Keep PRs focused and atomic

### Ingredient Data Contributions

Help improve our ingredient database:

1. Fork the repository
2. Update `backend/app/seed_data.py` with new ingredients
3. Follow the existing format:
   ```python
   {
       "canonical_name": "INGREDIENT_NAME",
       "aliases": ["alias1", "alias2"],
       "halal_status": HalalStatus.HALAL,  # or HARAM, AMBIGUOUS, UNKNOWN
       "category": "Category",
       "e_number": "E123",  # if applicable
       "notes": "Description and source info"
   }
   ```
4. Submit a pull request with sources/references

### Classification Rules Contributions

Improve halal classification rules:

1. Edit `backend/app/seed_data.py`
2. Add new rules following the format:
   ```python
   {
       "rule_name": "RULE_NAME",
       "rule_type": "blacklist",  # or whitelist, pattern
       "pattern": r"\bpattern\b",  # regex pattern
       "verdict": VerdictLabel.HARAM,
       "confidence": 0.99,
       "reason": "Clear explanation",
       "priority": 100  # Higher = checked first
   }
   ```
3. Test thoroughly
4. Submit PR with explanation

## Development Guidelines

### Backend (Python/FastAPI)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions/classes
- Keep functions focused and testable
- Use async/await for I/O operations

### Mobile App (React Native/TypeScript)

- Use TypeScript for type safety
- Follow React best practices
- Use functional components and hooks
- Keep components small and reusable
- Handle errors gracefully

### Admin Console (React/TypeScript)

- Follow Material-UI guidelines
- Keep pages modular
- Use proper loading states
- Handle API errors

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest --cov=app tests/  # With coverage
```

### Mobile Tests

```bash
cd mobile
npm test
npm test -- --coverage
```

## Documentation

- Update README.md for major changes
- Add inline code comments for complex logic
- Update API documentation
- Keep DEPLOYMENT.md current

## Questions?

- Open a Discussion on GitHub
- Email: dev@halalscanner.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to HalalScanner! 🙏
