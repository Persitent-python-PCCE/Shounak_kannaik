import java.util.*;

public class RotateListRight {

    public static void rotateRight(List<Integer> list, int k) {
        if (list.isEmpty()) {
            return;
        }
        int n = list.size();
        Collections.rotate(list, k % n);
    }

    public static void main(String[] args) {
        List<Integer> list = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5, 6, 7));
        rotateRight(list, 3);
        System.out.println(list);
    }
}