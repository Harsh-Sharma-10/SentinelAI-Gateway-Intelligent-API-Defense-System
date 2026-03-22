package com.apigateway.gatewayservice.filter;


import com.apigateway.gatewayservice.config.GatewayConfig;
import com.apigateway.gatewayservice.dto.RequestStats;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;

/**
 * RateLimitingFilter
 * Applies basic rate limiting rules
 * Blocks requests that exceed configured thresholds
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RateLimitingFilter implements GlobalFilter, Ordered {

    private final GatewayConfig gatewayConfig;

    private static final String REQUEST_STATS_ATTR = "REQUEST_STATS";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {

        // Get RequestStats from exchange (set by RequestAnalysisFilter)
        RequestStats stats = exchange.getAttribute(REQUEST_STATS_ATTR);

        if (stats == null) {
            log.warn("RequestStats not found in exchange attributes");
            return chain.filter(exchange);
        }

        // Check if request count exceeds burst threshold
        if (stats.getRequestcount() > gatewayConfig.getBurstThreshold()) {
            log.warn(" RATE LIMIT EXCEEDED: IP={}, Count={}, Threshold={}",
                    stats.getIpAddress(),
                    stats.getRequestcount(),
                    gatewayConfig.getBurstThreshold());

            return blockRequest(exchange, stats, "Rate limit exceeded");
        }

        // Check for suspicious patterns
        if (isSuspiciousUserAgent(stats.getUserAgent())) {
            log.warn(" SUSPICIOUS USER AGENT: IP={}, UserAgent={}",
                    stats.getIpAddress(),
                    stats.getUserAgent());

            return blockRequest(exchange, stats, "Suspicious user agent detected");
        }

        // All checks passed, continue
        return chain.filter(exchange);
    }

    /**
     * Block the request with 429 Too Many Requests
     */
    private Mono<Void> blockRequest(ServerWebExchange exchange,
                                    RequestStats stats,
                                    String reason) {

        // Update stats
        stats.setAiDecision("BLOCK");
        stats.setAiReason(reason);
        stats.setStatusCode(429);

        // Set response status
        exchange.getResponse().setStatusCode(HttpStatus.TOO_MANY_REQUESTS);
        exchange.getResponse().getHeaders().setContentType(MediaType.APPLICATION_JSON);

        // Create JSON response
        String jsonResponse = String.format(
                """
                        {
                          "error": "Rate Limit Exceeded",
                          "message": "%s",
                          "ip": "%s",
                          "requestCount": %d,
                          "limit": %d,
                          "retryAfter": 60
                        }
                        """,
                reason,
                stats.getIpAddress(),
                stats.getRequestcount(),
                gatewayConfig.getBurstThreshold()
        );

        // Write response
        DataBuffer buffer = exchange.getResponse().bufferFactory()
                .wrap(jsonResponse.getBytes(StandardCharsets.UTF_8));

        return exchange.getResponse().writeWith(Mono.just(buffer));
    }

    /**
     * Check if user agent matches suspicious patterns
     */
    private boolean isSuspiciousUserAgent(String userAgent) {
        if (userAgent == null || userAgent.isEmpty()) {
            return true; // No user agent is suspicious
        }

        String lowerUserAgent = userAgent.toLowerCase();

        for (String suspicious : gatewayConfig.getSuspiciousUserAgents()) {
            if (lowerUserAgent.contains(suspicious.toLowerCase())) {
                return true;
            }
        }

        return false;
    }

    @Override
    public int getOrder() {
        return 0; // Run after RequestAnalysisFilter (-2)
    }

}