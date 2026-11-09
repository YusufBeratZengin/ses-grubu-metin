# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them privately through GitHub's private vulnerability reporting: open the repository's **Security** tab and choose **Report a vulnerability** (https://github.com/YusufBeratZengin/ses-grubu-metin/security/advisories/new).

You should receive a response within 48 hours. If for some reason you do not, please follow up on the same security advisory to ensure we received your report.

Please include the following information:
- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Security Considerations

### Data Handling
- This is a **local CLI tool** — no network requests, no data upload
- Word lists and profanity filters are local files in `veri/`
- No user data is collected, stored, or transmitted

### Dependencies
- Minimal runtime dependencies: `syllabreak` (MIT), `PyYAML`, `regex`
- Dependencies are scanned via GitHub Dependabot
- Run `pip-audit` or `safety check` locally for vulnerability scanning

### Input Validation
- Letter set input is normalized and validated (alphabetic only)
- File paths are resolved safely (no directory traversal)
- Output files are written with explicit user consent

### Profanity Filter
- Community-sourced blacklist (`veri/profanity.txt`, CC-BY-SA 4.0)
- Not guaranteed to catch all inappropriate content
- **Teacher review recommended** before classroom use
- False positives/negatives possible

### Not an Official Educational Tool
- This software is **not affiliated with or endorsed by MEB** (Turkish Ministry of National Education)
- Use at your own discretion in educational settings
- Verify all generated content before distributing to students

## Disclosure Policy

When a vulnerability is reported:
1. We acknowledge receipt within 48 hours
2. We investigate and validate the issue
3. We develop and test a fix
4. We release a patch version (e.g., 0.1.1)
5. We publish a security advisory on GitHub

We appreciate responsible disclosure and will credit reporters (unless anonymity is requested).