#include <iostream>
#include <string>

#include "confutils.h"

using namespace std;


FADC250_CONF getFadc250Config(unsigned int i);
unsigned int getFadc250Length();
void fadc250InitGlobals();
int fadc250ReadConfigFile(char *filename);

int main()
{

    fadc250InitGlobals();     // init array
    fadc250ReadConfigFile("fadc250_example.cnf");
    for(int i=0; i< getFadc250Length(); i++)
    {
        FADC250_CONF board_conf = getFadc250Config(i);
        cout<<"slot="<<i<<"    group="<<board_conf.group<<endl;
    }
}
