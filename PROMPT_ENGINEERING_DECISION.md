# My Prompt Engineering Decisions

I have considered real life medical scenarios, and experimented across different prompt techniques and chain logics. The results can be seen in the data/results folder.

## Approaches that I Experimented with, Tradeoffs, and Final Approach:

- The various results along with approach tags can be seen in data/results folder

### Everything in Single Prompt and API Call (Approach 1)

This is a quick way to get things done and cost efficient as well. But it lacked the detail and specificity which was expected. Especially for medical accuracy this is an important function.

### Making 4 Parallel Chains One Each for the Evaluation Parameter (Approach 2)

This is a very verbose way to achieve the task. I created 4 parallel running chains one each for medical accuracy, completeness, etc. The results were impressive and consistent, as can be seen. I experimented with a range of bad to medium to good user response. And it was able to evaluate the responses really well consistently.

But this approach lacked extensibility, if in future u add more parameters, you can't be creating separate chains/LLM calls for each one of them. Plus not all scenarios hv equal weightage of each of the params.

But this approach laid a good foundation of how to take things further.

### My Approach (Approach 3)

So instead of making chains for each of the params. I put them into two brackets: medical and communication. I chose a separate bracket for medical because in the healthcare context it is something of utmost importance and need special handling. Rest of the params can be safely put into communication with a good prompt. I also added another chain to support a weight based scoring. I cache the weights for a particular scenario (so as to save on the api calls). For example in an emergency situation clarity and medical accuray are more important than tone and empathy. This approach came out with really good and consistent results along with extensibilty and cost effeciency.

## Prompt Engineering for Medical Accuracy:

I have split the medical accuracy prompt into two steps:
- Establish Medical Standards
- Evaluate Against them

This multi step prompt ensured that most medical accuracy can be ensured.

## For the Communication:

This is split into three categories clarity, empathy and completeness. I ask LLM to always give specific examples of what can be an ideal response to such a situation. Morever I pass the previous feedback the user has received so that they can evaluated on their progress as well. This approach made the evaluation robust and context aware.

## For Response Time:

I am using parallel chains so as to minimise the response time.

## For Structured Output:

I am using langchain's `with_structured_output` method that takes in a Pydantic class of the format I want the response in. Most modern LLMs now support this.

## For Future Use Cases:

### Add Recommended Scenarios Section (or Next Steps)
Based on user's weakness and strengths we can recommend scenarios to practice.

### Integration with Actual Data
Instead of just completely relying on LLM information to evaluate, we can have a store for actual verified medical information plus scenario handling. This can be done using RAG or fine tuning.

### Let the Users Add Scenarios
This can be useful in a real life situation, the scenarios added by workers can be useful data training plus to other people facing similar situations.

### Rate Limiting
We can rate limit the analysis generation to 1 per 30 seconds, so that the system is not overwhelmed and cost can be optimised.