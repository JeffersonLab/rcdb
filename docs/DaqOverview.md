## General concepts
This chapter overviews of how run data is to be added to RCDB. 
There are several ideological ideas behind of how RCDB works:


1. ***Minimum human interaction and alteration.*** RCDB should be automated database, which shell collect data as automatically as possible. There are still several types of data usually provided by homo sapiens or similar (run comments as example). Still, number of interactions with biological organisms should be minimized.  


2. ***Many updates during the run***. RCDB is updated continuously during the run. RCDB has no history by default (have logs but they serve another role). So usually the latest data means it is the rightest data, so the later data overwrites existing values for the run. If one need to save all values during the run, some array/collection should hold it and hole the array is saved as JSon. For example run statistics is updated each 10 seconds. This behavior saves at least some data if system is crashed before the end. 

3. ***Modularity***

4. ***Modular responsibility***

