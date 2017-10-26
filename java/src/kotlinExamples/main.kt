/**
 * Created by Dmitry on 3/24/2014.
 */
package kotlinExamples

import org.rcdb.createProvider

fun main(args: Array<String>) {
    val provider = createProvider("mysql://rcdb@hallddb.jlab.org")
    provider.connect()


    println("asgmt2 values as table: ")

    // getting constant type by name is possible via
    // provider.conditionTypeByNames
    val beam_current = provider.getCondition(31000, "beam_current")?.toDouble() ?: Double.NaN;
    println("HallD Beam current for the run 31000 is $beam_current")

    // GETTING all existent condition types
    // is possible via provider.conditionTypes property
    // The next example shows how to use them


    // get the maximum length of the "names" column
    val maxNameLength = provider.conditionTypes.maxBy({ a-> a.name.length})?.name?.length ?: 0
    val columnLength = 2 + maxNameLength

    for (cndType in provider.conditionTypes) {

        println("%-${columnLength}s %s".format(cndType.name, cndType.valueType.toString()))
    }

}