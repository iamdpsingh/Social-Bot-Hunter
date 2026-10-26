# Documentation Rules

These rules govern the accuracy, clarity, and maintenance of all documentation in Social Bot Hunter.

## Principles

1. **Synchronized Documentation**: Whenever schema definitions, detection formulas, configuration keys, or architecture change, update the corresponding documentation files in the same commit.
2. **Actionable Instructions**: Ensure setup commands, CLI snippets, and deployment instructions are executable and verified against current code.
3. **Engineering Clarity**: Write in direct, technical, clear English suitable for production engineering. Avoid hyperbolic claims ("100% accurate AI", "foolproof detector") and buzzword filler.
4. **Honest Limitations**: Prominently document missing features, partial access limitations, uncalibrated score thresholds, and platform restrictions alongside capabilities.
5. **Auto-Generated Accuracy**: Tables derived from code (e.g. database schema dictionaries, platform access matrices, feature catalogues) should be verified or refreshed with `python -m sbh docs`.
