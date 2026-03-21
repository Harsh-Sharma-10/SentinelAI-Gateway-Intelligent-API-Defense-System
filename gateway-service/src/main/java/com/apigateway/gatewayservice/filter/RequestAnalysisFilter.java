package com.apigateway.gatewayservice.filter;



import com.apigateway.gatewayservice.dto.RequestStats;  // ← CHANGED: dto instead of model
import com.apigateway.gatewayservice.service.RequestStatsService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Slf4j
@Component
@RequiredArgsConstructor
public class RequestAnalysisFilter implements GlobalFilter, Ordered {

    private final RequestStatsService requestStatsService;

    private static final String REQUEST_STATS_ATTR = "REQUEST_STATS";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {

        long startTime = System.currentTimeMillis();

        // Build RequestStats DTO from incoming request
        RequestStats stats = requestStatsService.buildRequestStats(exchange);

        // Store DTO in exchange attributes
        exchange.getAttributes().put(REQUEST_STATS_ATTR, stats);

        log.info("📊 Request Analysis: IP={}, Count={}, Path={}",
                stats.getIpAddress(),
                stats.getRequestcount(),
                stats.getEndpoint());

        return chain.filter(exchange).then(
                Mono.fromRunnable(() -> {
                    // Update DTO with response information
                    requestStatsService.updateWithResponse(stats, exchange, startTime);

                    log.info("✓ Request Complete: Status={}, Duration={}ms",
                            stats.getStatusCode(),
                            stats.getResponseTimeMs());

                    // TODO Phase 3: Send DTO to AI service
                    // TODO Phase 6: Convert DTO to Entity and save to MongoDB
                })
        );
    }

    @Override
    public int getOrder() {
        return -2;
    }
}
