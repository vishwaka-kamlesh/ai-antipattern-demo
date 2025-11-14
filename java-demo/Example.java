public class Example {
    public static void main(String[] args) {
        String a = "hello";
        String b = new String("hello");
        if (a == b) {
            System.out.println("Equal!");
        }

        if ("a" == "a") {
            System.out.println("Equal!");
        }

        
        if ("a" == "a") {
            System.out.println("Equal!");
        }

        if (1L == 1L) {
            System.out.println("Equal!");
        }

        if (1L == 1L) {
            System.out.println("Equal!");
        }

        String c = "hello";
        String d = new String("hello");
        if (c == d) {
            System.out.println("Equal!");
        }

        String e = "hello";
        String f = new String("hello");
        if (e == f) {
            System.out.println("Equal!");
        }
    }
}
