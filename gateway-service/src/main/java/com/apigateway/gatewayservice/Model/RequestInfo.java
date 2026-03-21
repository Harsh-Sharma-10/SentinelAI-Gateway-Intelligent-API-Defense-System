package com.apigateway.gatewayservice.Model;



import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.index.Indexed;

import java.time.LocalDateTime;

/**
 * RequestInfo - MongoDB Entity
 *
 * Purpose: Stores request information in the database
 * Used for: Analytics, auditing, AI model training
 *
 * @Document - Marks this as a MongoDB collection
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "request_logs")  // MongoDB collection name
public class RequestInfo {



    /**
     * MongoDB auto-generated ID
     */
    @Id
    private String id;

    // ═══════════════════════════════════════════════════════════
    // CLIENT IDENTIFICATION
    // ═══════════════════════════════════════════════════════════

    /**
     * Client IP address
     * @Indexed - Creates database index for faster queries
     */
    @Indexed
    private String ipAddress;

    /**
     * User agent string
     */
    private String userAgent;

    // ═══════════════════════════════════════════════════════════
    // REQUEST DETAILS
    // ═══════════════════════════════════════════════════════════

    /**
     * HTTP method (GET, POST, etc.)
     */
    private String method;

    /**
     * API endpoint
     * @Indexed - For endpoint-based queries
     */
    @Indexed
    private String endpoint;

    /**
     * Full request path with query parameters
     */
    private String requestPath;

    // ═══════════════════════════════════════════════════════════
    // FREQUENCY & TIMING
    // ═══════════════════════════════════════════════════════════

    /**
     * Number of requests from this IP in the last minute
     */
    private Integer requestCount;

    /**
     * Request timestamp
     * @Indexed - For time-based queries
     */
    @Indexed
    private LocalDateTime timestamp;

    /**
     * Response time in milliseconds
     */
    private Long responseTimeMs;

    // ═══════════════════════════════════════════════════════════
    // RESPONSE INFORMATION
    // ═══════════════════════════════════════════════════════════

    /**
     * HTTP status code
     */
    private Integer statusCode;

    // ═══════════════════════════════════════════════════════════
    // AI DECISION
    // ═══════════════════════════════════════════════════════════

    /**
     * AI decision: ALLOW or BLOCK
     * @Indexed - For filtering by decision
     */
    @Indexed
    private String aiDecision;

    /**
     * AI confidence score (0.0 to 1.0)
     */
    private Double aiConfidence;

    /**
     * Reason for AI decision
     */
    private String aiReason;

    /**
     * Was this blocked by rate limiting?
     */
    private Boolean rateLimited;

    /**
     * Was this flagged as suspicious?
     */
    private Boolean suspicious;

    // ═══════════════════════════════════════════════════════════
    // METADATA
    // ═══════════════════════════════════════════════════════════

    /**
     * When this record was created in DB
     */
    private LocalDateTime createdAt;

    /**
     * Environment (dev, staging, production)
     */
    private String environment;
}