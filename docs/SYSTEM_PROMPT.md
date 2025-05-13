# Global System Prompt Feature

This document explains the global system prompt feature that allows customizing how the AI responds across all features of the application.

## What is a System Prompt?

A system prompt is a set of instructions given to the AI model that influences how it responds to user requests. It helps control the style, tone, and content format in all AI-generated responses throughout the application, including slide generation, document analysis, and quiz generation.

## Features

- **Global Application**: The system prompt is shared across all features of the application
- **Customizable Instructions**: Provide specific guidance to the AI on how to respond to queries
- **Variable Support**: Use variables like `{{topic}}`, `{{date}}`, and `{{time}}` that get automatically replaced
- **Session-Only Prompts**: Try different prompts in a session without changing the global default
- **Example Templates**: Pre-made templates for different interaction types
- **Consistent Language Control**: Enforce responses in specific languages across all features

## How to Use

1. The system prompt can be set from any feature page that uses AI (Slide Generation, Document Analysis, Quiz Generation)
2. Access System Prompt settings in the settings panel of each feature
3. Choose an example prompt or write your own custom prompt
4. Click "Save System Prompt Globally" to use it as the default across all features

## API Endpoints

The system prompt is available through three main API endpoints:

```
GET/POST /api/slides/system-prompt
GET/POST /api/documents/system-prompt
GET/POST /api/ollama/system-prompt
```

Each endpoint supports:
- GET: Retrieve the current system prompt
- POST: Update the system prompt with a new value

## Setting via Script

You can set the global system prompt programmatically using the `set_system_prompt.py` script:

```bash
python set_system_prompt.py
```

This script updates the system prompt across all features by:
1. Making API calls to all system prompt endpoints
2. Updating the configuration file directly as a backup

## Default Vietnamese Prompt

The default system prompt in this application is set to:

```
must answer in vietnamese, phải trả lời bằng tiếng việt
```

This prompt ensures that all AI responses across all features (slide generation, document analysis, quiz generation) are provided in Vietnamese, meeting the language requirements of the application's users.

## Example System Prompts

### Vietnamese Response with Formal Tone
```
must answer in vietnamese with a formal academic tone, phải trả lời bằng tiếng việt với giọng văn học thuật trang trọng
```

### Technical Analysis
```
You are a technical expert. Create responses with precise, technically 
accurate content. Use formal language, include relevant technical terminology, 
and organize complex information hierarchically. All responses must be in Vietnamese.
```

### Educational Focus
```
You are an educational expert focusing on clear explanations.
Create content that simplifies complex topics, provides helpful examples, 
and ensures understanding for students at all levels.
All responses must be in Vietnamese (phải trả lời bằng tiếng việt).
```

## Best Practices

- Be specific about the format you want (bullet points, paragraph length)
- Specify the target audience for the content
- Indicate the level of formality and technical language needed
- Use the session-only option to experiment with different prompts
- When setting a language requirement, be explicit (e.g., "answer in Vietnamese")
- Combine language requirements with other instructions for more specific control
- Test your system prompt with a variety of queries to ensure consistent results

## Troubleshooting

If the system prompt is not being applied correctly:

1. Check that the backend server is running and accessible
2. Verify that all three system prompt endpoints are responding (see `test_api_endpoints.py`) 
3. Restart the application if recent changes were made to system prompt endpoints
4. Check the backend logs for any error messages related to the system prompt
5. Run `set_system_prompt.py` to manually update all endpoints and the configuration file

## Compatible Features

The system prompt is applied in the following application features:

- **Slide Generation**: Controls the content style and language of generated slides
- **Document Analysis**: Affects responses to document-based queries
- **Quiz Generation**: Determines the format and language of generated quiz questions
- **Direct Model Interaction**: Used in any direct API calls to the AI models

## Cross-Platform Compatibility

The system prompt functionality works consistently across different operating systems and environments:

- Windows
- Mac OS
- Linux
- Local development environments
- Deployment environments

For more examples and detailed guidance, see the `docs/system_prompt_guide.md` and `docs/system_prompt_examples.md` files.
