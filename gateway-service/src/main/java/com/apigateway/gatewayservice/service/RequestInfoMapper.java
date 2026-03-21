package com.apigateway.gatewayservice.service;


import com.apigateway.gatewayservice.Model.RequestInfo;
import com.apigateway.gatewayservice.dto.RequestStats;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class RequestInfoMapper {


    /**
     * RequestInfoMapper
     * <p>
     * Purpose: Convert between DTO (RequestStats) and Entity (RequestInfo)
     * Follows the Mapper pattern for clean separation
     */

    @Value("${spring.profiles.activa:dev}")
    private String environment;

    /**
     * Convert DTO to Entity (for saving to database)
     *
     * @param dto - RequestStats from filter
     * @return RequestInfo ready to save to MongoDB
     */

    public RequestInfo toEntity(RequestStats dto) {
        if (dto == null) {
            return null;
        }
        return RequestInfo.builder()
                .ipAddress(dto.getIpAddress())
                .userAgent(dto.getUserAgent())
                .method(dto.getMethod())
                .endpoint(dto.getEndpoint())
                .requestPath(dto.getRequestpath())
                .requestCount(dto.getRequestcount())
                .timestamp(dto.getTimestamp())
                .responseTimeMs(dto.getResponseTimeMs())
                .statusCode(dto.getStatusCode())
                .aiDecision(dto.getAiDecision())
                .aiConfidence(dto.getAiConfidence())
                .aiReason(dto.getAiReason())

                // Add entity-specific fields
                .createdAt(LocalDateTime.now())
                .environment(environment)
                .rateLimited(dto.getStatusCode() != null && dto.getStatusCode() == 429)
                .suspicious(isSuspicious(dto))
                .build();
    }

    public RequestStats toDto(RequestInfo entity) {
        if (entity == null) {
            return null;
        }

        return RequestStats.builder()
                .ipAddress(entity.getIpAddress())
                .userAgent(entity.getUserAgent())
                .method(entity.getMethod())
                .endpoint(entity.getEndpoint())
                .requestpath(entity.getRequestPath())
                .requestcount(entity.getRequestCount())
                .timestamp(entity.getTimestamp())
                .responseTimeMs(entity.getResponseTimeMs())
                .statusCode(entity.getStatusCode())
                .aiDecision(entity.getAiDecision())
                .aiConfidence(entity.getAiConfidence())
                .aiReason(entity.getAiReason())
                .build();
    }

    private boolean isSuspicious(RequestStats dto) {
        // High request count
        if (dto.getRequestcount() != null && dto.getRequestcount()> 50) {
            return true;
        }

        // Bot user agent
        if (dto.getUserAgent() != null) {
            String ua = dto.getUserAgent().toLowerCase();
            if (ua.contains("bot") || ua.contains("python") ||
                    ua.contains("curl") || ua.contains("scrapy")) {
                return true;
            }
        }

        if ("BLOCK".equals(dto.getAiDecision())) {
            return true;
        }

        return false;
    }

    /**
     * Update entity with response information from DTO
     *
     * @param entity - Existing RequestInfo
     * @param dto - Updated RequestStats
     */
    public void updateEntityFromDto(RequestInfo entity, RequestStats dto) {
        if (entity == null || dto == null) {
            return;
        }

        entity.setResponseTimeMs(dto.getResponseTimeMs());
        entity.setStatusCode(dto.getStatusCode());
        entity.setAiDecision(dto.getAiDecision());
        entity.setAiConfidence(dto.getAiConfidence());
        entity.setAiReason(dto.getAiReason());
        entity.setRateLimited(dto.getStatusCode() != null && dto.getStatusCode() == 429);
        entity.setSuspicious(isSuspicious(dto));
    }





}
