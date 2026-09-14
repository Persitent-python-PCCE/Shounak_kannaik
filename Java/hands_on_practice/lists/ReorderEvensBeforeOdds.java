import java.util.*;

public class ReorderEvensBeforeOdds {

    public static List<Integer> reorder(List<Integer> nums) {
        List<Integer> evens = new ArrayList<>();
        List<Integer> odds = new ArrayList<>();
        for (int n : nums) {
            if (n % 2 == 0) {
                evens.add(n);
            } else {
                odds.add(n);
            }
        }
        evens.addAll(odds);
        return evens;
    }

    public static void main(String[] args) {
        List<Integer> nums = Arrays.asList(4, 7, 2, 9, 6, 3, 8, 1);
        System.out.println(reorder(nums));
    }
}