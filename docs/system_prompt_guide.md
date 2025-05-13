## System Prompt Usage Guide

The system prompt is a powerful way to control how the AI generates slides for your presentations. By customizing the system prompt, you can influence:

- **Style and tone**: Make slides more formal, casual, technical, or simplified
- **Content organization**: Control how information is structured on slides
- **Visual suggestions**: Provide guidance on visual elements and layout
- **Domain-specific instructions**: Add specific rules for certain topics

### Effective System Prompt Examples

#### For Technical Presentations
```
You are a technical presentation expert. Create slides with precise, technically accurate content. 
Use formal language, include relevant technical terminology, and organize complex information 
hierarchically. Each slide should focus on a single technical concept with supporting details.
Limit each slide to 5 bullet points maximum, each with 7-10 words.
```

#### For Educational Presentations
```
You are an education specialist creating slides for students. Present information in a 
clear, engaging way with simple explanations of complex concepts. Include thought-provoking 
questions on some slides, and organize content in a logical learning progression from 
basic to advanced concepts. Use friendly, accessible language.
```

#### For Business Presentations
```
You are a business presentation expert focusing on persuasive, action-oriented slides.
Create content that highlights key business metrics, strategic insights, and clear 
recommendations. Use professional language, emphasize benefits and impacts, and 
ensure each slide contributes to a compelling business narrative. Include a clear 
call to action in the conclusion.
```

### Tips for Writing Effective System Prompts

1. **Be specific about format**: Mention how many bullet points per slide or words per bullet point if you have preferences
2. **Define the audience**: Specify who the presentation is for (executives, students, technical experts, general public)
3. **Set the tone**: Indicate if you want formal, casual, technical, or simplified language
4. **Provide structure guidance**: Suggest how information should be organized across slides
5. **Include domain expertise**: Add specific rules or frameworks relevant to your topic

### Variables You Can Use

The system supports the following variables that will be replaced automatically:
- `{{topic}}`: Will be replaced with "presentation" to remind the AI it's creating slides

### Best Practices

- Test different system prompts to see what works best for your needs
- Start with a basic prompt and refine it based on results
- Keep prompts focused on presentation style and structure, not specific content
- Balance between being specific and allowing the AI creative freedom
