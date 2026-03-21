package com.apigateway.backendservice.Controller;


import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * REST API Controller for backend service
 * Provides sample endpoints for testing the gateway
 */
@Slf4j
@RestController
@RequestMapping("/api")
public class ApiController {

    /**
     * GET /api/products - Returns list of products
     */
    @GetMapping("/products")
    public ResponseEntity<?> getProducts() {
        log.info("📦 Products endpoint called");

        // Simulate some processing time
        simulateProcessing(100);

        var products = List.of(
                Map.of(
                        "id", 1,
                        "name", "MacBook Pro M3 Max",
                        "price", 2499,
                        "stock", 15,
                        "category", "Laptops"
                ),
                Map.of(
                        "id", 2,
                        "name", "iPhone 15 Pro Max",
                        "price", 1199,
                        "stock", 50,
                        "category", "Smartphones"
                ),
                Map.of(
                        "id", 3,
                        "name", "AirPods Pro (2nd Gen)",
                        "price", 249,
                        "stock", 100,
                        "category", "Audio"
                ),
                Map.of(
                        "id", 4,
                        "name", "Apple Watch Ultra 2",
                        "price", 799,
                        "stock", 30,
                        "category", "Wearables"
                ),
                Map.of(
                        "id", 5,
                        "name", "iPad Pro 13-inch",
                        "price", 1299,
                        "stock", 25,
                        "category", "Tablets"
                )
        );

        return ResponseEntity.ok(Map.of(
                "success", true,
                "data", products,
                "count", products.size(),
                "timestamp", LocalDateTime.now(),
                "source", "backend-service"
        ));
    }

    /**
     * GET /api/users - Returns list of users
     */
    @GetMapping("/users")
    public ResponseEntity<?> getUsers() {
        log.info("👥 Users endpoint called");

        simulateProcessing(80);

        var users = List.of(
                Map.of(
                        "id", 1,
                        "name", "Alice Johnson",
                        "email", "alice.johnson@example.com",
                        "role", "Admin",
                        "active", true
                ),
                Map.of(
                        "id", 2,
                        "name", "Bob Smith",
                        "email", "bob.smith@example.com",
                        "role", "User",
                        "active", true
                ),
                Map.of(
                        "id", 3,
                        "name", "Charlie Brown",
                        "email", "charlie.brown@example.com",
                        "role", "User",
                        "active", true
                ),
                Map.of(
                        "id", 4,
                        "name", "Diana Prince",
                        "email", "diana.prince@example.com",
                        "role", "Moderator",
                        "active", true
                )
        );

        return ResponseEntity.ok(Map.of(
                "success", true,
                "data", users,
                "count", users.size(),
                "timestamp", LocalDateTime.now(),
                "source", "backend-service"
        ));
    }

    /**
     * GET /health - Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<?> health() {
        log.info("💚 Health check called");

        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "backend-service",
                "timestamp", LocalDateTime.now(),
                "uptime", "Running smoothly ✓"
        ));
    }

    /**
     * Simulate processing time
     */
    private void simulateProcessing(int milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            log.error("Processing interrupted", e);
        }
    }
}