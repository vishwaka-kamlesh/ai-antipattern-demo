public class Example {
    public static void main(String[] args) {
        String a = "hello";
        String b = new String("hello");
        if (a == b) {
            System.out.println("Equal!");
        }

        Integer m = 1;
        Integer n = 1;
        if (m == n) {
            System.out.println("Equal!");
        }

        String s1 = "hello";
        String s2 = new String("hello");
        if (s1 == s2) {
            System.out.println("Equal!");
        }

    }
}
