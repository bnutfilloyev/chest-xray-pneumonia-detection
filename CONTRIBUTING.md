# Contributing to Pneumonia AI Detector

Thank you for your interest in contributing to our medical AI project! 🏥

## 🎯 Ways to Contribute

### 🐛 Bug Reports
- Use GitHub Issues with detailed reproduction steps
- Include screenshots for UI issues
- Provide system information (OS, browser, Python version)

### 🚀 Feature Requests
- Describe the medical use case
- Explain how it improves patient care
- Consider HIPAA compliance implications

### 🔧 Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Follow our coding standards
4. Add tests for new functionality
5. Ensure medical accuracy
6. Submit a Pull Request

## 📋 Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/pneumonia-ai-detector.git
cd pneumonia-ai-detector

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up frontend
cd ../frontend
npm install

# Run tests
cd ../backend && python -m pytest
cd ../frontend && npm test
```

## ✅ Code Standards

### Python (Backend)
- Follow PEP 8
- Use Black for formatting: `black .`
- Type hints required: `mypy .`
- Docstrings for public functions

### TypeScript (Frontend)
- Use Prettier: `prettier --write src/`
- ESLint compliance
- Proper TypeScript types
- JSDoc for complex functions

## 🧪 Testing Requirements

- Unit tests for all new features
- Integration tests for API endpoints
- Medical accuracy validation
- Performance benchmarks

## 🏥 Medical Guidelines

- Ensure HIPAA compliance
- Validate medical accuracy
- Include proper disclaimers
- Consider clinical workflows

## 📝 Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

## 🤝 Code of Conduct

Be respectful and professional, especially when dealing with medical applications that impact patient care.

## 📞 Questions?

Open a GitHub Discussion or contact the maintainers.
