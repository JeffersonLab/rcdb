package org.rcdb

import java.util.ArrayList

/**
 * Gets statistics of ccdb requests
 */
class RequestStatistics{

    /**
     * A list of requests
     */
    val requests = ArrayList<RequestParseResult>()
    var totalTime:Double = 0.0
    var lastRequestTime:Double = 0.0

    /**
     * First data read after connection takes longer. So it is separated
     */
    var firstTime:Double = 0.0

    /**
     * Average request time
     */
    val averageTime:Double
        get(){
            if(requests.size == 0) return 0.0
            if(requests.size == 1) return firstTime
            return (totalTime-firstTime)/(requests.size -1)
        }

}
