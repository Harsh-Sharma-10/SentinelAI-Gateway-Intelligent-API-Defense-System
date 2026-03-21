package com.apigateway.gatewayservice.service;


import com.apigateway.gatewayservice.dto.RequestStats;  // Changed from model to dto
import com.apigateway.gatewayservice.util.IPExtractor;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ServerWebExchange;

import java.time.LocalDateTime;
@Slf4j
@Service
@RequiredArgsConstructor
public class RequestStatsService {


    private final RequestCounterService requestCounterService;


    /**
     * Build RequestStats DTO from ServerWebExchange
     */
    public RequestStats buildRequestStats(ServerWebExchange exchange) {

        // Extract request information
        String ip = IPExtractor.extractClientIP(exchange);
        String userAgent = exchange.getRequest().getHeaders()
                .getFirst("User-Agent");
        String method = exchange.getRequest().getMethod().toString();
        String path = exchange.getRequest().getURI().getPath();
        String fullPath = exchange.getRequest().getURI().toString();

        // Get request count for this IP
        int requestCount = requestCounterService.incrementAndGet(ip);

        // Build RequestStats DTO
                RequestStats stats  =  RequestStats.builder()
                .ipAddress(ip)
                .userAgent(userAgent != null ? userAgent : "Unknown")
                .method(method)
                .endpoint(path)
                .requestpath(fullPath)
                .requestcount(requestCount)
                .timestamp(LocalDateTime.now())
                .build();

        log.debug("Built RequestStats DTO: IP={}, Count={}, Path={}",
                ip, requestCount, path);

        return stats;
    }

    /**
     * Update RequestStats DTO with response information
     */
    public void updateWithResponse(RequestStats stats,
                                   ServerWebExchange exchange,
                                   long startTime) {

        // Calculate response time
        long responseTime = System.currentTimeMillis() - startTime;
        stats.setResponseTimeMs(responseTime);

        // Get status code
        if (exchange.getResponse().getStatusCode() != null) {
            stats.setStatusCode(exchange.getResponse().getStatusCode().value());
        }

        log.debug("Updated RequestStats DTO: Status={}, ResponseTime={}ms",
                stats.getStatusCode(), stats.getResponseTimeMs());
    }


}
