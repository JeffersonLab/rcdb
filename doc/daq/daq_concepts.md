1. ***Automation and Minimal Human Intervention***: RCDB is designed to be an automated database, striving to gather
   data with as little human intervention as possible. While there are certain types of data typically provided by human
   operators (such as run comments), the goal is to minimize the number of interactions with
   biological organisms.

2. ***Continuous Updates***: RCDB is designed to be updated continuously throughout its runtime, without maintaining a
   historical record by default (though logs are present, they serve a different purpose). The latest data is generally
   assumed to be the most accurate, hence any new data will replace existing values. In cases where a complete record of
   all values during a run is required, the data can be stored in an array or collection, which is then saved as JSON.
   For instance, run statistics are updated every 10 seconds. This approach ensures that some data is preserved in the
   event of a system crash before completion.

3. ***Modularity and Extensibility***: RCDB goes beyond providing an API for data addition; it also offers a suite of
   tools and modules that are as isolated as possible to provide ready-to-use DAQ writing functionality, such as CODA
   integration. It further allows users to introduce their own methods, promoting a more customizable and extensible
   system.

4. ***Fault Isolation and Notification***: In the event of a module failure during an update, the issue should be logged
   and human operators should be alerted. However, it's crucial that such failures do not impact the functionality of
   other modules. This principle ensures that individual module failures do not cascade into system-wide disruptions,
   thereby maintaining overall system stability.
