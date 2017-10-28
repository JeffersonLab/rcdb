import org.rcdb.*;

import java.util.HashMap;
import java.util.Vector;

public class SimpleExample {
    public static void main(String[] args) {
        JDBCProvider provider = RCDB.createProvider("mysql://rcdb@hallddb.jlab.org/rcdb");
        provider.connect();

        // The real database is going to be used for the example
        // Run 31000 is used everywhere:
        long runNumber = 31000;

        // get long value
        long eventCount = provider.getCondition(runNumber, "event_count").toLong();
        System.out.println("event_count = " + eventCount);

        // get bool value
        boolean isValidRunEnd = provider.getCondition(runNumber, "is_valid_run_end").toBoolean();
        System.out.println("is_valid_run_end = " + isValidRunEnd);

        // get double
        double beamCurrent = provider.getCondition(runNumber, "beam_current").toDouble();
        System.out.println("beam_current = " + beamCurrent);

        // getCondition(...) function returns a Condition object which provides
        // information about its type and holds the value of the right type
        Condition polarizationCondition = provider.getCondition(runNumber, "polarization_direction");
        long dbId = polarizationCondition.getId();                      // Database ID of the condition record
        long runFromDb = polarizationCondition.getRunNumber();          // Run number for the condition
        String name = polarizationCondition.getName();                  // Name of the condition
        ValueTypes valueType = polarizationCondition.getValueType();    // value type of the condition.
        System.out.println();
        System.out.println("polarization_direction = " + polarizationCondition.toString());
        System.out.println(" Condition object introspection: ");
        System.out.println("    db ID      : " + dbId);
        System.out.println("    name       : " + name);
        System.out.println("    run num    : " + runFromDb);
        System.out.println("    valueType  : " + valueType.toString());
        System.out.println();


        // ConditionType holds information about condition name and value type
        // One can get access to all available conditionTyes (i.e. condition names)
        Vector<ConditionType> cndTypes = provider.getConditionTypes();
        HashMap<String, ConditionType> cndTypeByNames = provider.getConditionTypeByNames();

        // one can use ConditionType to get Condition for a given run
        double beamCurrent2 = provider.getCondition(runNumber, cndTypeByNames.get("beam_current")).toDouble();
        System.out.println("beam_current = " + beamCurrent2);

        // List all available condition names
        System.out.println("All conditions in the DB:");
        for(ConditionType cndType : cndTypes){
            String row = String.format("   %-30s %s", cndType.getName(), cndType.getValueType().toString());
            System.out.println(row);
        }
    }
}