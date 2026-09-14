import java.util.*;

public class GenerateBinaryNumbers {

    public static List<String> generateBinary(int n) {
        List<String> result = new ArrayList<>();
        Queue<String> queue = new LinkedList<>();
        queue.add("1");

        for (int i = 0; i < n; i++) {
            String s = queue.poll();
            result.add(s);
            queue.add(s + "0");
            queue.add(s + "1");
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(String.join(", ", generateBinary(6)));
    }
}