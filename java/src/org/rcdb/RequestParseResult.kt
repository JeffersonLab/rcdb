package org.rcdb

//Set default parameters
// result
import java.util.Date

class RequestParseResult(
        public val originalRequest:String
) {
    /** Run number */
    var runNumber:Int=0

    /** true if Run number was non empty */
    var wasParsedRunNumber:Boolean=false

    /** true if was an error parsing run number */
    var isInvalidRunNumber:Boolean=false

    /** Object path **/
    var path:String = ""

    /** true if Path was nonempty */
    var wasParsedPath:Boolean=false

    /** Variation name */
    var variation:String=""

    /** true if variation was not empty */
    var wasParsedVariation:Boolean=false

    /** Time stamp */
    var time:Date = Date(0)

    /** true if time stamp was not empty */
    var wasParsedTime:Boolean=false

    /** Original string with time */
    var timeString:String=""
}
