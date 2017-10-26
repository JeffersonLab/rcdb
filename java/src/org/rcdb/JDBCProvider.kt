package org.rcdb

import java.util.HashMap
import java.util.Vector

import java.sql.*


open class JDBCProvider(val connectionString: String) {

    var conditionTypes = Vector<ConditionType>()
    var conditionTypeByNames = HashMap<String, ConditionType>()


    protected var connection: Connection? = null
    protected var prsConditionType  : PreparedStatement? = null
    protected var prsCondition      : PreparedStatement? = null
    protected var prsFileNames      : PreparedStatement? = null
    protected var prsFile           : PreparedStatement?=null

    private var stopwatch = Stopwatch()

    /**
     * Collect statistics of getData function
     */
    var statisticsIsCollecting:Boolean = false

    /**
     * Gets statistics of getData function
     */
    val statistics:RequestStatistics = RequestStatistics()


    /**
     * Flag indicating the connection to database is established
     */
    val isConnected:Boolean
        get(){
            return connection?.isClosed == false
        }


    /**
     * Connects to database using connection string
     */
    open fun connect(){}


    /**
     * closes current connection
     */
    fun close(){
        connection?.close()
    }


    /**
     * @warning (!) the function must be called after connect
     */
    protected open fun postConnect(){
        conditionTypeByNames.clear()
        conditionTypes.clear()

        loadConstantTypes()

        //reset stopwatch
        stopwatch.clear()
    }

    private fun loadConstantTypes() {
        try {
            val rs = prsConditionType!!.executeQuery()

            conditionTypeByNames.clear()
            conditionTypes.clear()
            //loop through results
            while (rs.next()) {
                val condType = ConditionType(
                        rs.getLong("id"),
                        rs.getString("name"),
                        ValueTypes.fromDbString(rs.getString("value_type"))
                )
                conditionTypes.add(condType)
                conditionTypeByNames[condType.name] = condType
            }

            // Sort conditionTypes... just for convenience...
            if(conditionTypes.size > 0) conditionTypes.sortBy ({ t->t.name})
        }
        catch(e:SQLException ){
            throw e
        }
        finally {

        }
    }

    /** Gets conditions by name and run (@see GetRun and SetRun) */
    fun getCondition(runNumber:Long, cndTypeName:String): Condition?
    {
        val cndType = this.conditionTypeByNames[cndTypeName]
        return when(cndType){
            null -> null
            else -> getCondition(runNumber, cndType)
        }
    }

    /** Gets conditions by condition type and run (@see GetRun and SetRun) */
    fun getCondition(runNumber:Long, cndType:ConditionType): Condition?
    {
        val ps = prsCondition!!
        // 1 - run_number = ?
        // 2 - condition_type_id = ?
        ps.setLong(1, runNumber)
        ps.setLong(2, cndType.id)

        val rs = ps.executeQuery()!!


        if (rs.next()) {

            // query(and db) has the next return values:
            // id, bool_value, floatValue, int_value, text_value, time_value
            // from the later ones we really need only one, which corresponds to cndType

            var boolValue = false
            var floatValue: Double = Double.NaN
            var longValue: Long = Long.MAX_VALUE
            var textValue = ""
            var timeValue: java.sql.Time = Time(0)

            when(cndType.valueType) {
                ValueTypes.BOOL-> boolValue = rs.getBoolean("bool_value")
                ValueTypes.JSON, ValueTypes.STRING, ValueTypes.BLOB-> textValue = rs.getString("text_value")
                ValueTypes.DOUBLE -> floatValue = rs.getDouble("float_value")
                ValueTypes.LONG-> longValue = rs.getLong("int_value")
                ValueTypes.TIME-> timeValue = rs.getTime("time_value")
            }

            val condition = Condition(
                    cndType,
                    rs.getLong("id"),
                    runNumber,
                    longValue,
                    boolValue,
                    floatValue,
                    textValue,
                    timeValue)
            return condition
        }

        return null //Empty ptr
    }
}