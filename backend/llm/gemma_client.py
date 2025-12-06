import ollama
from typing import List, Dict
import json
import asyncio


class GemmaClient:
    """
    Client for interacting with Gemma 12B LLM via Ollama.

    Handles:
    - Connecting to local Ollama instance
    - Sending analysis prompts
    - Parsing LLM responses
    - Error handling
    """

    def __init__(self):
        self.model = "gemma3:1b"  # Using Gemma 3 1B model for speed
        self.system_prompt = """You are a network security analyst. Analyze network traffic for anomalies.

Focus on: security threats, performance issues, unusual patterns.

For each anomaly provide:
- Severity: CRITICAL, HIGH, MEDIUM, LOW
- Brief description
- Key evidence
- Impact
- 2-3 actions

Return JSON array:
{
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "type": "anomaly_type",
  "title": "Brief title",
  "description": "What was found",
  "evidence": {"key": "value"},
  "why_it_matters": "Impact",
  "recommended_actions": ["action1", "action2"]
}"""

    async def analyze_anomalies(self, suspicious_data: List[Dict], baseline: Dict) -> Dict:
        """
        Send data to LLM for analysis and get structured response.

        Args:
            suspicious_data: List of flagged anomalies from statistical analysis
            baseline: Baseline traffic statistics

        Returns:
            Dictionary containing analysis results and summary
        """
        try:
            # Build optimized prompt
            prompt = self.build_analysis_prompt(suspicious_data, baseline)

            # Call Ollama API with timeout (5 minutes max)
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    ollama.chat,
                    model=self.model,
                    messages=[
                        {'role': 'system', 'content': self.system_prompt},
                        {'role': 'user', 'content': prompt}
                    ],
                    options={
                        'temperature': 0.1,  # Lower temperature for faster, more consistent results
                        'top_p': 0.9,
                        'num_predict': 1000  # Limit output length for speed
                    }
                ),
                timeout=300.0  # 5 minute timeout (increased for smaller models)
            )

            # Parse LLM response
            analysis = self.parse_llm_response(response['message']['content'])

            return analysis

        except asyncio.TimeoutError:
            return {
                'error': "LLM analysis timed out after 5 minutes",
                'summary': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'total_anomalies': 0,
                'anomalies': []
            }
        except Exception as e:
            return {
                'error': f"LLM analysis failed: {str(e)}",
                'summary': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'total_anomalies': 0,
                'anomalies': []
            }

    def build_analysis_prompt(self, suspicious_data: List[Dict], baseline: Dict) -> str:
        """
        Build comprehensive analysis prompt for the LLM.

        Args:
            suspicious_data: Flagged anomalies
            baseline: Baseline statistics

        Returns:
            Formatted prompt string
        """
        prompt = f"""Network Traffic Analysis:

SUMMARY:
- Packets: {baseline.get('total_packets', 0):,}
- Sources: {baseline.get('unique_sources', 0)}
- Destinations: {baseline.get('unique_destinations', 0)}
- Protocols: {dict(baseline.get('protocol_distribution', {}))}

ANOMALIES:
"""

        # Add suspicious activities (limit to top 15 for speed)
        if suspicious_data:
            for i, item in enumerate(suspicious_data[:15], 1):
                # Simplified format for speed
                prompt += f"{i}. {item.get('type', 'unknown')}: {item.get('description', str(item))}\n"
        else:
            prompt += "None detected.\n"

        prompt += """
Analyze and return JSON array of findings. Be concise but accurate.
Format: [{"severity":"LEVEL","type":"type","title":"title","description":"brief","evidence":{},"why_it_matters":"impact","recommended_actions":["action1","action2"]}]

Return only JSON array:"""

        return prompt

    def parse_llm_response(self, response: str) -> Dict:
        """
        Parse LLM response into structured format.

        Args:
            response: Raw LLM response text

        Returns:
            Dictionary with parsed anomalies and summary
        """
        try:
            # Try to extract JSON from response (handling markdown code blocks)
            json_str = None

            # Strategy 1: Look for markdown JSON code blocks
            if '```json' in response:
                parts = response.split('```json')
                if len(parts) > 1:
                    json_str = parts[1].split('```')[0].strip()

            # Strategy 2: Look for generic code blocks
            elif '```' in response:
                parts = response.split('```')
                if len(parts) > 1:
                    json_str = parts[1].strip()

            # Strategy 3: Look for array start and end
            if not json_str:
                json_start = response.find('[')
                json_end = response.rfind(']') + 1
                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]

            if json_str:
                anomalies = json.loads(json_str)

                # Validate that we got a list
                if not isinstance(anomalies, list):
                    anomalies = [anomalies] if isinstance(anomalies, dict) else []

                # Count by severity
                summary = {
                    'critical': sum(1 for a in anomalies if a.get('severity') == 'CRITICAL'),
                    'high': sum(1 for a in anomalies if a.get('severity') == 'HIGH'),
                    'medium': sum(1 for a in anomalies if a.get('severity') == 'MEDIUM'),
                    'low': sum(1 for a in anomalies if a.get('severity') == 'LOW')
                }

                return {
                    'summary': summary,
                    'total_anomalies': len(anomalies),
                    'anomalies': anomalies,
                    'status': 'success'
                }
            else:
                # No JSON found - return empty result with error
                return {
                    'error': 'No JSON array found in LLM response',
                    'summary': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                    'total_anomalies': 0,
                    'anomalies': [],
                    'raw_response': response[:500],  # First 500 chars for debugging
                    'status': 'no_json_found'
                }

        except json.JSONDecodeError as e:
            # JSON parsing failed
            return {
                'error': f'Failed to parse LLM response as JSON: {str(e)}',
                'summary': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'total_anomalies': 0,
                'anomalies': [],
                'raw_response': response[:500],
                'status': 'json_parse_error'
            }
        except Exception as e:
            # Other parsing errors
            return {
                'error': f'Unexpected error parsing response: {str(e)}',
                'summary': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'total_anomalies': 0,
                'anomalies': [],
                'status': 'parse_error'
            }

    async def test_connection(self) -> Dict:
        """
        Test connection to Ollama and verify model availability.

        Returns:
            Dictionary with connection status
        """
        try:
            # Try a simple query
            response = await asyncio.to_thread(
                ollama.chat,
                model=self.model,
                messages=[
                    {'role': 'user', 'content': 'Respond with just "OK" if you can read this.'}
                ]
            )

            return {
                'status': 'connected',
                'model': self.model,
                'response': response['message']['content'][:100]
            }

        except Exception as e:
            return {
                'status': 'error',
                'model': self.model,
                'error': str(e)
            }
