## RCDB Java API overview

Java API allows one to read RCDB condition values for the run. It doesn't provide possibility of run selection queries at this point.


## Installation
Java API comes as sources (in Kotlin) and as ready to use Java precompiled .jar file

* Java API is located in [$RCDB_HOME/java](https://github.com/JeffersonLab/rcdb/tree/master/java) directory. 
* Precompiled jar is located in [$RCDB_HOME/java/out/artifacts](https://github.com/JeffersonLab/rcdb/tree/master/java/out/artifacts/rcdb_jar/)

---


## Getting values

The example shows how to get values from RCDB:

```java
import org.rcdb.*;
//...
        // Connect to the database 
        // The real HallD database is going to be used for the example
        JDBCProvider provider = RCDB.createProvider("mysql://rcdb@hallddb.jlab.org/rcdb");
        provider.connect();

        // get event count as a long value for run number 31000
        long eventCount = provider.getCondition(31000, "event_count").toLong();
        System.out.println("event_count = " + eventCount);
```

Here is the list of condition to[Type] functions and what values they are for:

```java
Long toLong();                         /// For int values
Bool toBool();                         /// For bool or int in DB
Double toDouble();                     /// For Double or int in DB
String toString();                     /// For Json, String or Blob
Date   toDate();                       /// For time value

org.rcdb.ValueTypes                    /// type enum
```

## Examples

Examples are located in [$RCDB_HOME/java/src/javaExamples](https://github.com/JeffersonLab/rcdb/tree/master/java/src/javaExamples) folder. 

<br>

#### List of examples:

Simple example - shows how to read values from database and lists all condition types from DB

[$RCDB_HOME/java/src/javaExamples/SimpleExample.java](https://github.com/JeffersonLab/rcdb/blob/master/java/src/javaExamples/SimpleExample.java)

<br>

#### Kotlin

There are also an example written in [$RCDB_HOME/java/src/kotlinExamples/main.kt](https://github.com/JeffersonLab/rcdb/blob/master/java/src/kotlinExamples/main.kt)





