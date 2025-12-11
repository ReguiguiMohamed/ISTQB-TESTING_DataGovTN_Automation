# CAPTCHA Bypass Component

## Overview
This component provides automated CAPTCHA solving capabilities for the Tunisian National Open Data Portal testing framework. It enables automated testing of protected pages by handling security challenges that would otherwise block test execution.

## Purpose in Testing Project
The CAPTCHA bypass functionality is integrated into the testing framework to:
- Enable automated testing of secured pages during continuous integration
- Provide unattended test execution capabilities
- Handle authentication flows that include CAPTCHA challenges
- Support comprehensive end-to-end testing scenarios

## Integration
This component is used by the main test framework through the `utils.captcha_login_helper` module to:
- Solve CAPTCHA challenges during login procedures
- Enable authenticated session establishment for protected page testing
- Support cross-browser testing of secured functionality

## Installation

```bash
pip install -r requirements.txt
```

Additional dependency:
```bash
# Install ffmpeg for audio processing
# Windows: Download from https://ffmpeg.org/download.html
# Linux: sudo apt-get install ffmpeg
```

## Usage
The component is automatically integrated into the main test framework via:
- `utils.captcha_login_helper.py` - Provides test framework integration
- Authentication fixtures in `conftest.py`

Direct usage for testing:
```python
from DrissionPage import ChromiumPage
from RecaptchaSolver import RecaptchaSolver

driver = ChromiumPage()
recaptchaSolver = RecaptchaSolver(driver)
# Use as part of your testing workflow
```

## How It Works
The component uses audio CAPTCHA solving techniques to:
- Automatically detect and respond to CAPTCHA challenges
- Convert audio challenges to text programmatically
- Submit CAPTCHA solutions to enable continued browsing

**Note:** This component is used solely for automated testing of the Tunisian National Open Data Portal in accordance with testing best practices and acceptable use policies.

## Testing Integration
- Used in authentication workflows for test data preparation
- Supports resilient test execution across different browsers
- Integrated with JIRA reporting for automated issue creation