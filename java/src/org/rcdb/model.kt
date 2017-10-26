package org.rcdb

val dataSeparator = '|'


/** Types of RCDB condition values
 *
 * In RCDB each condition value is one of the following values:
 * bool, json, string, float, int, time, blob
 *
 * int and float in RCDB DB are 64 bit, corresponding to Long and Double in Java,
 * So, to be less confusing, in Java API these records are named LONG and DOUBLE
 * While if one calls @see toDbString, "int" and "float" are returned for such fields
 */
enum class ValueTypes {
    BOOL,
    JSON,
    STRING,
    DOUBLE,
    LONG,
    TIME,
    BLOB;

    override fun toString(): String {
        return when (this) {
            BOOL -> "Boolean"
            JSON -> "Json"
            STRING -> "String"
            DOUBLE -> "Double"
            LONG -> "Long"
            TIME -> "Time"
            BLOB -> "Blob"
        }
    }


    /** Gets the string with the ValueType name as it defines by RCDB database
     *
     * Each condition of RCDB is one of the following types (as named in RCDB database)
     * bool, json, string, float, int, time, blob
     *
     * Here name 'int' and 'float' in DB are Long and Double in Java
     *
     */
    fun toDbString(): String {
        return when (this) {
            BOOL -> "bool"
            JSON -> "json"
            STRING -> "string"
            DOUBLE -> "float"
            LONG -> "int"
            TIME -> "time"
            BLOB -> "blob"
        }
    }

    companion object {

        /** @see toDbString(), it does the opposite */
        @JvmStatic
        fun fromDbString(str: String): ValueTypes {
            return when (str) {
                "int" -> ValueTypes.LONG
                "float" -> ValueTypes.DOUBLE
                "string" -> ValueTypes.STRING
                "bool" -> ValueTypes.BOOL
                "json" -> ValueTypes.JSON
                "time" -> ValueTypes.TIME
                "blob" -> ValueTypes.BLOB
                else -> throw IllegalArgumentException("ValueTypes string '$str' is something different than one of possible values")
            }
        }
    }
};


class ConditionType(
        val id: Long,                /// DB id
        val name: String,            /// Name of the directory
        val valueType: ValueTypes    /// Type
)


class Condition
(
        val conditionType: ConditionType,
        val id: Long,
        val runNumber: Long,
        private var intValue: Long,
        private var boolValue: Boolean,
        private var floatValue: Double,
        private var textValue: String,
        private var dateTime: java.sql.Time
) {
    /** gets the name of the condition */
    val name: String
        get() {
            return conditionType.name;
        }

    val valueType: ValueTypes
        get() {
            return conditionType.valueType;
        }

    /** Returns value of the condition as int.
     * Throws if ValueType is not int in DB
     * */
    fun toInt(): Int {
        if (conditionType.valueType != ValueTypes.LONG) {
            throw UnsupportedOperationException("Value type of the condition is not int")
        }
        return this.intValue.toInt();
    }

    /** Returns value of the condition as int.
     * Throws if ValueType is not int in DB
     * */
    fun toLong(): Long {
        if (conditionType.valueType != ValueTypes.LONG) {
            throw UnsupportedOperationException("Value type of the condition is not int")
        }
        return this.intValue;
    }


    /** Returns value of the condition as Bool.
     * If ValueType is int it is converted to bool
     *
     * Throws if ValueType is not bool or int in DB
     */
    fun toBoolean(): Boolean {

        if (conditionType.valueType != ValueTypes.LONG && conditionType.valueType != ValueTypes.BOOL) {
            throw UnsupportedOperationException("Value type of the condition is not bool or int")
        }
        if (conditionType.valueType == ValueTypes.LONG) return intValue != 0L

        return boolValue;
    }

    /** Returns value of the condition as Double.
     * If ValueType is int it is converted to Double
     *
     * Throws if ValueType is not Double or int in DB
     */
    fun toDouble(): Double {

        if (conditionType.valueType != ValueTypes.LONG && conditionType.valueType != ValueTypes.DOUBLE) {
            throw UnsupportedOperationException("Value type of the condition is not 'Float'(double in Kotlin or C++) or int")
        }

        if (conditionType.valueType == ValueTypes.LONG) return intValue.toDouble()

        return floatValue
    }

    /** Returns value of the condition as string.
     * Works for ValueTypes Json, String, Blob
     *
     * Throws if ValueType is not Json, String or Blob in DB
     */
    override fun toString(): String {

        if (conditionType.valueType != ValueTypes.JSON &&
                conditionType.valueType != ValueTypes.STRING &&
                conditionType.valueType != ValueTypes.BLOB) {
            throw UnsupportedOperationException("Value type of the condition is not String, Json or Blob")
        }

        return textValue;
    }


    /** Returns value of the condition as time_point.
     *
     * Throws if ValueType is not Time in DB
     */

    fun toTime(): java.sql.Time {
        if (conditionType.valueType != ValueTypes.TIME) {
            throw UnsupportedOperationException("Value type of the condition is not Time")
        }

        return dateTime;
    }
}