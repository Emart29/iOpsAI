# backend/utils/ai_helpers.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from groq import Groq
from config import settings
import json
import re

# Initialize Groq client
client = Groq(api_key=settings.GROQ_API_KEY)

def get_groq_response(prompt: str, context: str = "", model: str = settings.GROQ_MODEL) -> str:
    """Get response from Groq API"""
    try:
        messages = [
            {"role": "system", "content": "You are Sight, an AI data science assistant built into iOps. You help users understand their datasets through conversation. Be concise, professional, and actionable."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}
        ]
        
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "I'm having trouble connecting to my AI brain right now. Please try again later."

def generate_ai_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Generate AI insights for the dataset"""
    
    # Prepare context
    context = f"""Dataset Information:
- Shape: {df.shape[0]} rows, {df.shape[1]} columns
- Columns: {', '.join(df.columns[:20])}
- Data Types: {df.dtypes.value_counts().to_dict()}
- Missing Values: {df.isnull().sum().sum()} total
- Sample Stats: {df.describe().to_string() if len(df.select_dtypes(include=[np.number]).columns) > 0 else 'No numeric columns'}
"""
    
    prompt = """Analyze this dataset and provide exactly 5 insights in this format:
1. **Data Quality**: [Identify data quality issues]
2. **Feature Engineering**: [Suggest new features to create]
3. **Cleaning Strategy**: [Recommend cleaning steps]
4. **Outlier Detection**: [Highlight potential outliers]
5. **Modeling Approach**: [Suggest appropriate ML techniques]

Be specific, actionable, and concise (max 2-3 sentences per insight)."""
    
    try:
        response = get_groq_response(prompt, context)
        
        # Parse response into structured insights
        insights = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                if '**' in line:
                    parts = line.split('**')
                    if len(parts) >= 3:
                        category = parts[1].replace(':', '').strip()
                        description = parts[2].strip()
                        insights.append({
                            "category": category,
                            "title": category,
                            "description": description
                        })
        
        if len(insights) < 5:
            # Fallback if parsing failed
            insights = [
                {"category": "Data Quality", "title": "Data Quality", "description": "Check for missing values and duplicates"},
                {"category": "Feature Engineering", "title": "Feature Engineering", "description": "Consider creating interaction features"},
                {"category": "Cleaning Strategy", "title": "Cleaning Strategy", "description": "Handle missing values appropriately"},
                {"category": "Outlier Detection", "title": "Outlier Detection", "description": "Use IQR method to detect outliers"},
                {"category": "Modeling Approach", "title": "Modeling Approach", "description": "Start with simple models and iterate"}
            ]
        
        return insights[:5]
    except Exception as e:
        print(f"Error generating insights: {e}")
        return [
            {"category": "Error", "title": "Error", "description": f"Could not generate insights: {str(e)}"}
        ]

def chat_with_data(df: pd.DataFrame, message: str, chat_history: List[Dict], filename: str) -> str:
    """Chat with Sight AI about the dataset (Agentic Mode)"""
    
    # Prepare dataset context
    context = f"""Dataset Context:
- Filename: {filename}
- Shape: {df.shape[0]} rows, {df.shape[1]} columns
- Columns: {', '.join(df.columns)}
- Sample: {df.head(2).to_string()}
"""
    
    # Build conversation history
    conversation = []
    for msg in chat_history[-5:]:
        role = "user" if msg.get("role") == "user" else "assistant"
        conversation.append({"role": role, "content": msg.get("content", "")})
    
    # System Prompt with Tools
    system_prompt = """You are Sight, an AI Data Agent. You help users analyze data.
    
You have access to the following TOOLS. If the user asks for an action, return a JSON object describing the tool call.
TOOLS:
1. `plot_chart`: Visualize a column. Args: {"tool": "plot_chart", "column": "col_name", "type": "histogram|bar|scatter"}
2. `clean_data`: Suggest cleaning. Args: {"tool": "clean_data", "operation": "drop_nulls|fill_mean|drop_duplicates", "column": "col_name (optional)"}

RULES:
- If the user asks to "plot", "show distribution", or "visualize", USE THE `plot_chart` TOOL.
- If the user asks to "clean", "fix", or "remove", USE THE `clean_data` TOOL.
- Otherwise, answer the question normally in text.
- DO NOT wrap JSON in markdown code blocks. Just return the raw JSON string if using a tool.
"""

    try:
        messages = [
            {"role": "system", "content": system_prompt}
        ] + conversation + [
            {"role": "user", "content": f"Context: {context}\n\nUser: {message}"}
        ]
        
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=0.3, # Lower temperature for more deterministic tool use
            max_tokens=512,
        )
        
        response_text = completion.choices[0].message.content
        
        # Try to parse as JSON (Tool Call)
        try:
            tool_call = json.loads(response_text)
            if "tool" in tool_call:
                # We found a tool call!
                if tool_call["tool"] == "plot_chart":
                    return f"📊 **Action:** Generating {tool_call.get('type', 'chart')} for `{tool_call.get('column')}`...\n\n(Chart rendering not yet connected to chat, but I understood your intent!)"
                elif tool_call["tool"] == "clean_data":
                    return f"🧹 **Action:** I recommend applying `{tool_call.get('operation')}` to `{tool_call.get('column', 'dataset')}`."
        except json.JSONDecodeError:
            pass
            
        return response_text

    except Exception as e:
        print(f"Chat error: {e}")
        return f"I encountered an error: {str(e)}"

def generate_recommendations(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Generate AI recommendations for modeling and next steps"""
    
    context = f"""Dataset: {df.shape[0]} rows, {df.shape[1]} columns
Columns: {', '.join(df.columns[:15])}
Numeric columns: {len(df.select_dtypes(include=[np.number]).columns)}
Categorical columns: {len(df.select_dtypes(include=['object']).columns)}
"""
    
    prompt = """Based on this dataset, provide recommendations in these categories:

**Feature Engineering** (3 suggestions):
- Specific transformations or new features to create

**Modeling Strategy** (3 suggestions):
- Appropriate algorithms to try
- Evaluation metrics to use
- Train/test split approach

**Next Steps** (3 suggestions):
- Immediate actions to take
- Tools or techniques to explore
- Potential challenges to address

Format each as: "**Title**: Description" """
    
    try:
        response = get_groq_response(prompt, context)
        
        # Parse response
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if '**' in line and ':' in line:
                parts = line.split('**')
                if len(parts) >= 3:
                    title = parts[1].strip()
                    description = parts[2].replace(':', '').strip()
                    
                    # Categorize
                    category = "Next Steps"
                    if any(word in title.lower() for word in ['feature', 'engineering', 'transform']):
                        category = "Feature Engineering"
                    elif any(word in title.lower() for word in ['model', 'algorithm', 'metric', 'train']):
                        category = "Modeling Strategy"
                    
                    recommendations.append({
                        "category": category,
                        "title": title,
                        "description": description
                    })
        
        return recommendations
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return [
            {"category": "Error", "title": "Error", "description": f"Could not generate recommendations: {str(e)}"}
        ]

def generate_suggestions(df: pd.DataFrame, semantic_types: Dict[str, str]) -> List[Dict[str, str]]:
    """Generate cleaning and transformation suggestions using Groq"""
    
    context = f"Columns: {', '.join(df.columns)}\nTypes: {semantic_types}\nMissing: {df.isnull().sum().to_dict()}"
    prompt = "Suggest 3 specific data cleaning or transformation steps for this dataset. Return ONLY a JSON array of objects with keys 'column', 'issue', 'suggestion'."
    
    try:
        response = get_groq_response(prompt, context)
        # Extract JSON from response if needed
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return []
    except:
        return [
            {"column": "General", "issue": "Data Quality", "suggestion": "Check for duplicates and missing values."}
        ]

def detect_semantic_types(df):
    """Detect semantic types for DataFrame columns"""
    semantic_types = {}
    for col in df.columns:
        dtype = df[col].dtype
        if dtype in ['float64', 'int64', 'int32', 'float32']:
            semantic_types[col] = 'numeric'
        elif dtype == 'bool':
            semantic_types[col] = 'boolean'
        elif 'datetime' in str(dtype):
            semantic_types[col] = 'datetime'
        else:
            unique_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
            if unique_ratio < 0.05:
                semantic_types[col] = 'categorical'
            else:
                semantic_types[col] = 'text'
    return semantic_types