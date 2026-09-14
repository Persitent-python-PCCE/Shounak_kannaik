import java.util.*;
import java.util.stream.*;

public class PartitionPrimes {

    static boolean isPrime(int n) {
        if (n < 2) {
            return false;
        }
        for (int i = 2; (long) i * i <= n; i++) {
            if (n % i == 0) {
                return false;
            }
        }
        return true;
    }

    public static void main(String[] args) {
        List<Integer> nums = Arrays.asList(2, 3, 4, 5, 6, 7, 8, 9, 10, 11);

        Map<Boolean, List<Integer>> partitioned = nums.stream().collect(Collectors.partitioningBy(PartitionPrimes::isPrime));

        System.out.println("Primes:" + partitioned.get(true));
        System.out.println("Non-primes:" + partitioned.get(false));
    }
}