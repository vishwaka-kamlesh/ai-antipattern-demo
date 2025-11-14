import java.io.*;

public class Example {

    public static void main(String[] args) throws Exception {

        // 1. no-eq-string
        String s1 = "hello";
        String s2 = new String("hello");
        if (s1 == s2) {  
            
        }

        // 2. no system out
        System.out.println("This is a log");

        // 3. no-print-stacktrace
        try {
            int x = 1 / 0;
        } catch (Exception e) {
            e.printStackTrace();
        }

        // 4. hardcoded-credential
        String password = "SuperSecret123!";
        String apiKey = "sk-abc123xyz";

        // 5. no-thread-sleep
        Thread.sleep(1000);

        // 6. resource-not-closed
        FileInputStream fis = new FileInputStream("data.txt");
        BufferedReader br = new BufferedReader(new FileReader("log.txt"));
    }
}