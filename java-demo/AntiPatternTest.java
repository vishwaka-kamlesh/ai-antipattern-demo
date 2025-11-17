// 1. Empty catch block
public class AntiPatternTest {

    void rule1() {
        try {
            int a = 10 / 0;
        } catch (Exception e) {}
        // ❌ Rule 1 violation: Empty catch
    }

    // 2. printStackTrace()
    void rule2(Exception e) {
        e.printStackTrace();
        // ❌ Rule 2
    }

    // 3. System.out.println()
    void rule3() {
        System.out.println("oops");
        // ❌ Rule 3
    }

    // 4. Logging sensitive data (fake logger)
    Logger logger = new Logger();
    void rule4() {
        logger.info("password leaked");
        // ❌ Rule 4
    }

    // 5. Hardcoded secret
    String pwd = "superSecret123";
    // ❌ Rule 5

    // 6. Hardcoded URL
    String api = "https://example.com/pay";
    // ❌ Rule 6

    // 7. SQL concatenation
    String user = "hacker";
    String query = "SELECT * FROM users WHERE name='" + user + "'";
    // ❌ Rule 7

    // 8. Thread.sleep()
    void rule8() throws Exception {
        Thread.sleep(999);
        // ❌ Rule 8
    }

    // 9. String concat in loop
    void rule9() {
        String s = "";
        for (int i = 0; i < 10; i++) s = s + i;
        // ❌ Rule 9
    }

    // 10. New object in loop
    void rule10() {
        for (int i = 0; i < 10; i++) new String("x");
        // ❌ Rule 10
    }

    // 11. N+1 Query (fake DB)
    DB db = new DB();
    void rule11() {
        for (int i = 0; i < 5; i++) db.fetch(i);
        // ❌ Rule 11
    }

    // 12. String == comparison
    String a = "hi", b = "bye";
    void rule12() {
        if (a == b) {}
        // ❌ Rule 12
    }

    // 13. DTO field must be private (making it public on purpose)
    public String fullName; // ❌ Rule 13

    // 14. Unused import
    // Just pretend we imported something useless above
    // ❌ Rule 14 implicit

    // 15. Magic number
    int status = 99;
    // ❌ Rule 15

    // 16. Method > 200 lines
    void rule16() {
        // ❌ Rule 16 (spammy enough for Semgrep to cry)
        for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }


                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }


                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }
                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }

                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }

                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }        for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }

                for (int i = 0; i < 210; i++) {
            System.out.println(i);
        }

        
    }

    // 17. Field injection
    @Autowired
    private Repo repo;
    // ❌ Rule 17

    // Fake Logger + DB classes so file compiles
    class Logger {
        void info(String msg) {}
    }

    class DB {
        void fetch(int id) {}
    }

    class Repo {}
}

