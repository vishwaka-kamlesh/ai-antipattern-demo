package com.example.test;

import java.io.IOException;
import java.util.*;

/**
 * Focused test file for 3 rules:
 * 1. Empty catch block
 * 11. N+1 queries
 * 23. Modify collection while iterating
 */
public class FocusedTest {
    
    private UserRepository userRepository;
    private OrderRepository orderRepository;
    
    // ============================================
    // RULE 1: Empty catch blocks - SHOULD TRIGGER
    // ============================================
    
    public void emptyCatchBlock1() {
        try {
            riskyOperation();
        } catch (Exception e) {
            // SHOULD TRIGGER: Empty catch with only comment
        }
    }
    
    public void emptyCatchBlock2() {
        try {
            riskyOperation();
        } catch (IOException e) {
            // SHOULD TRIGGER: Empty catch
        }
    }
    
    public void emptyCatchBlock3() {
        try {
            riskyOperation();
        } catch (Exception e) {
        }
        // SHOULD TRIGGER: Completely empty
    }
    
    // SHOULD NOT TRIGGER: Has actual code
    public void goodCatchBlock() {
        try {
            riskyOperation();
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
    
    // ============================================
    // RULE 11: N+1 query detection - SHOULD TRIGGER
    // ============================================
    
    public void nPlusOneRepositoryCall(List<User> users) {
        // SHOULD TRIGGER: repository call in loop
        for (User user : users) {
            List<Order> orders = orderRepository.findByUserId(user.getId());
            System.out.println(orders.size());
        }
    }
    
    public void nPlusOneLazyLoading(List<User> users) {
        // SHOULD TRIGGER: lazy loading in loop
        for (User user : users) {
            List<Order> orders = user.getOrders();
            System.out.println(orders.size());
        }
    }
    
    public void nPlusOneMultipleCalls(List<Customer> customers) {
        // SHOULD TRIGGER: multiple repository calls
        for (Customer customer : customers) {
            List<Payment> payments = paymentRepository.findByCustomer(customer.getId());
            List<Invoice> invoices = invoiceRepository.getInvoices(customer.getId());
        }
    }
    
    public void nPlusOneGetterCall(List<Order> orders) {
        // SHOULD TRIGGER: getter call in loop (lazy loading)
        for (Order order : orders) {
            User user = order.getUser();
            String name = user.getName();
        }
    }
    
    // SHOULD NOT TRIGGER: fetch all at once
    public void goodFetchAll() {
        List<User> users = userRepository.findAllWithOrders();
        for (User user : users) {
            System.out.println(user.getOrders().size());
        }
    }
    
    // ============================================
    // RULE 23: Modifying collection while iterating - SHOULD TRIGGER
    // ============================================
    
    public void removeWhileIterating1(List<String> items) {
        // SHOULD TRIGGER: removing during iteration
        for (String item : items) {
            if (item.isEmpty()) {
                items.remove(item);
            }
        }
    }
    
    public void removeWhileIterating2(Set<Integer> numbers) {
        // SHOULD TRIGGER: removing from set
        for (Integer num : numbers) {
            if (num < 0) {
                numbers.remove(num);
            }
        }
    }
    
    public void addWhileIterating1(List<String> items) {
        // SHOULD TRIGGER: adding during iteration
        for (String item : items) {
            if (item.length() > 10) {
                items.add(item + "_copy");
            }
        }
    }
    
    public void addWhileIterating2(List<User> users) {
        // SHOULD TRIGGER: adding objects
        for (User user : users) {
            if (user.isAdmin()) {
                users.add(new User("admin_copy"));
            }
        }
    }
    
    public void modifyMultipleTimes(List<String> data) {
        // SHOULD TRIGGER: both add and remove
        for (String item : data) {
            if (item.startsWith("old_")) {
                data.remove(item);
            }
            if (item.startsWith("new_")) {
                data.add(item.toUpperCase());
            }
        }
    }
    
    // SHOULD NOT TRIGGER: using Iterator.remove()
    public void goodRemovalWithIterator(List<String> items) {
        Iterator<String> it = items.iterator();
        while (it.hasNext()) {
            String item = it.next();
            if (item.isEmpty()) {
                it.remove();
            }
        }
    }
    
    // SHOULD NOT TRIGGER: collecting to new list
    public void goodRemovalWithStream(List<String> items) {
        List<String> filtered = items.stream()
            .filter(item -> !item.isEmpty())
            .collect(Collectors.toList());
    }
    
    // SHOULD NOT TRIGGER: removing from different collection
    public void removingFromDifferentCollection(List<String> items, List<String> toRemove) {
        for (String item : items) {
            toRemove.remove(item);
        }
    }
    
    // ============================================
    // Helper classes and methods
    // ============================================
    
    private void riskyOperation() throws IOException {
        // Simulated risky operation
    }
    
    interface UserRepository {
        List<User> findAllWithOrders();
    }
    
    interface OrderRepository {
        List<Order> findByUserId(Long userId);
    }
    
    interface PaymentRepository {
        List<Payment> findByCustomer(Long customerId);
    }
    
    interface InvoiceRepository {
        List<Invoice> getInvoices(Long customerId);
    }
    
    static class User {
        private Long id;
        private String name;
        private List<Order> orders;
        
        public User(String name) {
            this.name = name;
        }
        
        public Long getId() { return id; }
        public String getName() { return name; }
        public List<Order> getOrders() { return orders; }
        public boolean isAdmin() { return false; }
    }
    
    static class Order {
        private Long id;
        private User user;
        
        public Long getId() { return id; }
        public User getUser() { return user; }
    }
    
    static class Customer {
        private Long id;
        public Long getId() { return id; }
    }
    
    static class Payment {
        private Long id;
    }
    
    static class Invoice {
        private Long id;
    }
    
    private PaymentRepository paymentRepository;
    private InvoiceRepository invoiceRepository;
}