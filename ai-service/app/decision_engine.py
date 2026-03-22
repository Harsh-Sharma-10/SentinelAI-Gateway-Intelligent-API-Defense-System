from app.models import RequestStats, AIDecision
from app.config import settings
from typing import Tuple
import re

class DecisionEngine:
    """
    AI Decision Engine
    Analyzes request patterns and makes ALLOW/BLOCK decisions

    Phase 3: Rule-based logic
    Phase 4: Machine learning model
    """

    def __init__(self):
        self.bot_pattern = re.compile(
            '|'.join(settings.bot_keywords),
            re.IGNORECASE
        )

    def analyze(self, stats: RequestStats) -> AIDecision:
        """
        Main analysis method
        Checks multiple factors and returns decision
        """

        # Collect all checks
        checks = [
            self._check_frequency(stats),
            self._check_user_agent(stats),
            self._check_burst_pattern(stats),
            self._check_endpoint_pattern(stats)
        ]

        # Find the highest severity check that failed
        blocking_check = None
        max_confidence = 0.0

        for check in checks:
            action, confidence, reason, threat = check
            if action == "BLOCK" and confidence > max_confidence:
                blocking_check = check
                max_confidence = confidence

        # If any check recommends blocking with high confidence
        if blocking_check and max_confidence >= settings.block_confidence_threshold:
            action, confidence, reason, threat = blocking_check

            return AIDecision(
                action="BLOCK",
                confidence=confidence,
                reason=reason,
                threat_level=threat,
                analysis_details={
                    "request_count": stats.request_count,
                    "user_agent": stats.user_agent[:50],
                    "endpoint": stats.endpoint,
                    "all_checks": [
                        {"check": check[2], "confidence": check[1]}
                        for check in checks
                    ]
                },
                recommended_action=self._get_recommended_action(threat)
            )

        # Default: Allow
        return AIDecision(
            action="ALLOW",
            confidence=0.95,
            reason="Normal behavior detected - all checks passed",
            threat_level="LOW",
            analysis_details={
                "request_count": stats.request_count,
                "checks_passed": len(checks)
            }
        )

    def _check_frequency(self, stats: RequestStats) -> Tuple[str, float, str, str]:
        """
        Check request frequency
        Returns: (action, confidence, reason, threat_level)
        """

        count = stats.request_count

        # Critical: Very high frequency
        if count >= settings.very_high_frequency_threshold:
            return (
                "BLOCK",
                0.98,
                f"Very high request frequency: {count} requests/min (threshold: {settings.very_high_frequency_threshold})",
                "CRITICAL"
            )

        # High: Suspicious frequency
        if count >= settings.suspicious_request_count:
            return (
                "BLOCK",
                0.85,
                f"Suspicious request frequency: {count} requests/min (threshold: {settings.suspicious_request_count})",
                "HIGH"
            )

        # Medium: Elevated frequency
        if count >= settings.high_frequency_threshold:
            return (
                "ALLOW",  # Still allow, but flag it
                0.6,
                f"Elevated request frequency: {count} requests/min",
                "MEDIUM"
            )

        # Low: Normal frequency
        return (
            "ALLOW",
            0.95,
            f"Normal request frequency: {count} requests/min",
            "LOW"
        )

    def _check_user_agent(self, stats: RequestStats) -> Tuple[str, float, str, str]:
        """
        Check user agent for bot patterns
        """

        user_agent = stats.user_agent.lower()

        # Check for bot patterns
        if self.bot_pattern.search(user_agent):
            matched_keyword = self.bot_pattern.search(user_agent).group()
            return (
                "BLOCK",
                0.90,
                f"Bot user agent detected: '{matched_keyword}' in '{stats.user_agent[:50]}'",
                "HIGH"
            )

        # Check for missing or suspicious user agent
        if not user_agent or user_agent == "unknown" or len(user_agent) < 10:
            return (
                "BLOCK",
                0.75,
                f"Missing or invalid user agent: '{stats.user_agent}'",
                "MEDIUM"
            )

        # Normal user agent
        return (
            "ALLOW",
            0.95,
            "Legitimate user agent detected",
            "LOW"
        )

    def _check_burst_pattern(self, stats: RequestStats) -> Tuple[str, float, str, str]:
        """
        Check for burst patterns (future enhancement)
        Currently uses request count as proxy
        """

        # If very high count in short window, likely automated
        if stats.request_count > 60:  # More than 1 per second
            return (
                "BLOCK",
                0.80,
                f"Burst pattern detected: {stats.request_count} requests in {settings.burst_window_seconds}s",
                "HIGH"
            )

        return (
            "ALLOW",
            0.90,
            "No burst pattern detected",
            "LOW"
        )

    def _check_endpoint_pattern(self, stats: RequestStats) -> Tuple[str, float, str, str]:
        """
        Check endpoint access patterns
        """

        endpoint = stats.endpoint.lower()

        # Sensitive endpoints
        if any(sensitive in endpoint for sensitive in ['/admin', '/api/admin', '/system']):
            if stats.request_count > 5:
                return (
                    "BLOCK",
                    0.95,
                    f"High frequency access to sensitive endpoint: {stats.endpoint}",
                    "CRITICAL"
                )

        # Sequential access pattern (scraping)
        if re.search(r'page=\d+|id=\d+|\d+$', stats.request_path):
            if stats.request_count > 20:
                return (
                    "BLOCK",
                    0.75,
                    "Sequential access pattern detected (possible scraping)",
                    "MEDIUM"
                )

        return (
            "ALLOW",
            0.95,
            "Normal endpoint access pattern",
            "LOW"
        )

    def _get_recommended_action(self, threat_level: str) -> str:
        """
        Get recommended mitigation action based on threat level
        """

        recommendations = {
            "CRITICAL": "Immediate IP ban for 24 hours + alert security team",
            "HIGH": "Block IP for 1 hour + rate limit to 5 req/min",
            "MEDIUM": "Temporary block for 15 minutes + CAPTCHA challenge",
            "LOW": "Monitor closely + apply standard rate limits"
        }

        return recommendations.get(threat_level, "Monitor activity")


# Global instance
decision_engine = DecisionEngine()