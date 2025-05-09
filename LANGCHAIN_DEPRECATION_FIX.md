# LangChain Deprecation Fix

To fix the deprecation warning:

> LangChainDeprecationWarning: The method `Chain.run` was deprecated in langchain 0.1.0 and will be removed in 1.0. Use :meth:`~invoke` instead.

You need to update all instances of `chain.run()` to use the newer `chain.invoke()` method in the `document_service.py` file. Here's what you need to change:

## 1. For the analyze_document method (summary section):
```python
# Change this:
result = chain.run(text=combined_text)

# To this:
result = chain.invoke({"text": combined_text})["text"]
```

## 2. For the analyze_document method (QA section):
```python
# Change this:
result = chain.run(context=relevant_text, question=user_query)

# To this:
result = chain.invoke({"context": relevant_text, "question": user_query})["text"]
```

## 3. For the generate_quiz method:
```python
# Change this:
result = chain.run(
    text=combined_text[:15000],
    num_questions=num_questions,
    difficulty=difficulty
)

# To this:
result = chain.invoke({
    "text": combined_text[:15000],
    "num_questions": num_questions,
    "difficulty": difficulty
})["text"]
```

## 4. For the generate_quiz_multiple method:
```python
# Change this:
result = chain.run(all_text=all_text, num_questions=num_questions, difficulty=difficulty)

# To this:
result = chain.invoke({"all_text": all_text, "num_questions": num_questions, "difficulty": difficulty})["text"]
```

## 5. For the _generate_multi_document_summary method:
```python
# Change this:
result = chain.run(text=doc["content"])

# To this:
result = chain.invoke({"text": doc["content"]})["text"]
```

## 6. For the _generate_multi_document_summary method (multiple documents):
```python
# Change this:
result = chain.run(documents=formatted_docs)

# To this:
result = chain.invoke({"documents": formatted_docs})["text"]
```

## 7. For the _answer_question_from_documents method (single document):
```python
# Change this:
result = chain.run(context=relevant_text, question=user_query)

# To this:
result = chain.invoke({"context": relevant_text, "question": user_query})["text"]
```

## 8. For the _answer_question_from_documents method (multiple documents):
```python
# Change this:
result = chain.run(context=relevant_text, question=user_query)

# To this:
result = chain.invoke({"context": relevant_text, "question": user_query})["text"]
```

These changes will update your code to use the new LangChain API and get rid of the deprecation warnings.
