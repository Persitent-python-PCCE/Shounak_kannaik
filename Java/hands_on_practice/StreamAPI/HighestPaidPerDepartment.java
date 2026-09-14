import java.util.*;
import java.util.stream.*;

public class HighestPaidPerDepartment {

    static class Employee {
        String name;
        String dept;
        int salary;

        Employee(String name, String dept, int salary) {
            this.name = name;
            this.dept = dept;
            this.salary = salary;
        }
    }

    public static void main(String[] args) {
        List<Employee> employees = Arrays.asList(new Employee("Asha", "Engineering", 85000), new Employee("Ravi", "Engineering", 92000),
                new Employee("Meera", "Sales", 60000),new Employee("John", "Sales", 72000),new Employee("Priya", "HR", 55000));

        Map<String, Optional<Employee>> topByDept = employees.stream().collect(Collectors.groupingBy(e -> e.dept, Collectors.maxBy(Comparator.comparingInt(e -> e.salary))));

        for (Map.Entry<String, Optional<Employee>> entry : topByDept.entrySet()) {
            Employee e = entry.getValue().get();
            System.out.println(entry.getKey() + " -> " + e.name + " (" + e.salary + ")");
        }
    }
}