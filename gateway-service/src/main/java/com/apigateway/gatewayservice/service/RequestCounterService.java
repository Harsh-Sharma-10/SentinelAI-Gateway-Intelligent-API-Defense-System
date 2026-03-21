package com.apigateway.gatewayservice.service;



import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Queue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * RequestCounterService
 * Tracks request frequency per IP using sliding window algorithm
 *
 * Thread-safe: Uses ConcurrentHashMap and ConcurrentLinkedQueue
 */
@Slf4j
@Service
public class RequestCounterService {

    // Maps IP address -> Queue of request timestamps
    private final ConcurrentHashMap<String, Queue<LocalDateTime>> requestTimestamps;

    // Sliding window size (in seconds)
    private static final int WINDOW_SIZE_SECONDS = 60;

    public RequestCounterService() {
        this.requestTimestamps = new ConcurrentHashMap<>();
    }

    /**
     * Increment request count for an IP and return current count
     *
     * @param ipAddress - Client IP
     * @return Number of requests in the last 60 seconds
     */
    public int incrementAndGet(String ipAddress) {
        LocalDateTime now = LocalDateTime.now();

        // Get or create queue for this IP
        Queue<LocalDateTime> timestamps = requestTimestamps
                .computeIfAbsent(ipAddress, k -> new ConcurrentLinkedQueue<>());

        // Add current timestamp
        timestamps.offer(now);

        // Remove old timestamps (outside sliding window)
        cleanupOldTimestamps(timestamps, now);

        int currentCount = timestamps.size();

        log.debug("IP: {} | Request count in last {}s: {}",
                ipAddress, WINDOW_SIZE_SECONDS, currentCount);

        return currentCount;
    }

    /**
     * Get current request count without incrementing
     */
    public int getRequestCount(String ipAddress) {
        Queue<LocalDateTime> timestamps = requestTimestamps.get(ipAddress);

        if (timestamps == null || timestamps.isEmpty()) {
            return 0;
        }

        LocalDateTime now = LocalDateTime.now();
        cleanupOldTimestamps(timestamps, now);

        return timestamps.size();
    }

    /**
     * Remove timestamps older than the sliding window
     */
    private void cleanupOldTimestamps(Queue<LocalDateTime> timestamps,
                                      LocalDateTime now) {
        LocalDateTime cutoffTime = now.minus(WINDOW_SIZE_SECONDS, ChronoUnit.SECONDS);

        // Remove old timestamps from the front of the queue
        while (!timestamps.isEmpty() &&
                timestamps.peek().isBefore(cutoffTime)) {
            timestamps.poll();
        }
    }

    /**
     * Clear all data for an IP (called when IP is blocked)
     */
    public void clearIP(String ipAddress) {
        requestTimestamps.remove(ipAddress);
        log.info("Cleared request history for IP: {}", ipAddress);
    }

    /**
     * Get total number of tracked IPs
     */
    public int getTrackedIPCount() {
        return requestTimestamps.size();
    }

    /**
     * Periodic cleanup (remove IPs with no recent requests)
     * Call this from a scheduled task
     */
    public void performPeriodicCleanup() {
        LocalDateTime now = LocalDateTime.now();
        AtomicInteger removedCount = new AtomicInteger();

        requestTimestamps.entrySet().removeIf(entry -> {
            cleanupOldTimestamps(entry.getValue(), now);
            boolean shouldRemove = entry.getValue().isEmpty();
            if (shouldRemove) removedCount.getAndIncrement();
            return shouldRemove;
        });

        if (removedCount.get() > 0) {
            log.info("Periodic cleanup: Removed {} inactive IPs", removedCount);
        }
    }
}