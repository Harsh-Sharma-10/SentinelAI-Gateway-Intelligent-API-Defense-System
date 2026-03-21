package com.apigateway.gatewayservice.config;



import org.springframework.context.annotation.Configuration;
import org.springframework.beans.factory.annotation.Value;
import lombok.Getter;

/**
 * Gateway Configuration
 * Centralized place for all gateway settings
 */
@Configuration
@Getter
public class GatewayConfig {

    // Rate Limiting Settings
    @Value("${gateway.ratelimit.requests-per-minute:60}")
    private int requestsPerMinute;

    @Value("${gateway.ratelimit.burst-threshold:100}")
    private int burstThreshold;

    @Value("${gateway.ratelimit.window-size-seconds:60}")
    private int windowSizeSeconds;

    // Request Analysis Settings
    @Value("${gateway.analysis.enabled:true}")
    private boolean analysisEnabled;

    @Value("${gateway.analysis.suspicious-user-agents}")
    private String[] suspiciousUserAgents = {
            "python-requests",
            "curl",
            "wget",
            "scrapy",
            "bot",
            "spider"
    };

    // Logging
    @Value("${gateway.logging.verbose:false}")
    private boolean verboseLogging;
}