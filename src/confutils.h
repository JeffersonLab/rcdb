#define RESET   "\033[0m"
#define BLACK   "\033[30m"      /* Black */
#define RED     "\033[31m"      /* Red */
#define GREEN   "\033[32m"      /* Green */
#define YELLOW  "\033[33m"      /* Yellow */
#define BLUE    "\033[34m"      /* Blue */
#define MAGENTA "\033[35m"      /* Magenta */
#define CYAN    "\033[36m"      /* Cyan */
#define WHITE   "\033[37m"      /* White */
#define BOLDBLACK   "\033[1m\033[30m"      /* Bold Black */
#define BOLDRED     "\033[1m\033[31m"      /* Bold Red */
#define BOLDGREEN   "\033[1m\033[32m"      /* Bold Green */
#define BOLDYELLOW  "\033[1m\033[33m"      /* Bold Yellow */
#define BOLDBLUE    "\033[1m\033[34m"      /* Bold Blue */
#define BOLDMAGENTA "\033[1m\033[35m"      /* Bold Magenta */
#define BOLDCYAN    "\033[1m\033[36m"      /* Bold Cyan */
#define BOLDWHITE   "\033[1m\033[37m"      /* Bold White */

#define FNLEN     128       /* length of config. file name */
#define STRLEN    250       /* length of str_tmp */
#define ROCLEN     80       /* length of ROC_name */
#define Nfa250     21


#define MAX_FADC250 16
#define MAX_FADC125 16
#define MAX_F1TDC   16
#define MAX_FADC250_CH 16
#define NCHAN      16


#define MAX_FADC_PB_SAMPLES   32

/** FADC configuration parameters **/
typedef struct {
  unsigned int slot;
  int soft_rev;
  int soft_adc;

  unsigned int mode;
  unsigned int pl;
  unsigned int ptw;
  unsigned int nb;
  unsigned int na;
  unsigned int npeak;

  unsigned int mask;
  unsigned int trig_mask;
  unsigned int thr[MAX_FADC250_CH];
  unsigned int dac[MAX_FADC250_CH];
  unsigned int ped[MAX_FADC250_CH];

} board_fadc250;

/** FADC configuration parameters **/
/** Modified by Sergei  **/

typedef struct {
  int  group;
  int  f_rev;
  int  b_rev;
  int  b_ID;
  char SerNum[80];

  int          mode;
  unsigned int winOffset;
  unsigned int winWidth;
  unsigned int nsb;
  unsigned int nsa;
  unsigned int npeak;

  unsigned int chDisMask;
  unsigned int trigMask;
  unsigned int thr[MAX_FADC250_CH];
  unsigned int dac[MAX_FADC250_CH];
  unsigned int ped[MAX_FADC250_CH];

} FADC250_CONF;




/** FADC PLAYBACK parameters **/
typedef struct {
  unsigned int slot;
  unsigned short ch_mask;
  unsigned short pb_data[512];
} pb_fadc250;

/** TI configuration parameters **/
typedef struct {
  unsigned int slot;
  unsigned int ver;         /* version */
  unsigned int rev;         /* revision */
  unsigned int crate_id;    /* crate_id: 1-15 */
  unsigned int trig_src;    /* trigger source: 0-5 */
  unsigned int en_input;    /* select trigger source input: bitmask: bit5 bit4 bit3 bit2 bit1 bit0 (inp6, inp5, inp4, inp3, inp2, inp1) */
  unsigned int holdoff_rule;     /* trigger holdoff rule: 1-5 */
  unsigned int holdoff_interval; /* trigger holdoff time interval (in time_step): 1-63 */
  unsigned int holdoff_step;     /* trigger holdoff time step: 0 = 16ns, 1 = 500ns */
  unsigned int sync_src;              /* sync source: 0-4 */
  unsigned int sync_delay;            /* sync delay: 1-127 */
  unsigned int sync_width;            /* sync width: 1-127 */
  unsigned int sync_units;            /* sync units: 0 = 4ns, 1 = 32ns */
  unsigned int fiber_delay;           /* fiber delay */
  unsigned int fiber_offset;          /* fiber offset */
  unsigned int busy_src;              /* busy source mask: bitmask: bits: 16-0 */
  unsigned int busy_flag;             /* busy source flag: 0-1 */
  unsigned int block_level;           /* block level: 1-15 */
  unsigned int event_format;          /* event format: 0-3 */
  unsigned int block_bflevel;         /* block buffer level: 0-65535 */
  unsigned int out_port_mask;         /* output port mask: bits: 3-0 (p4,p3,p2,p1) */ 
  unsigned int clk_src;               /* clock source: 0 = internal, 1 = external */
  unsigned int ti_soft_trig[4]     /* enable software trigger: [0] - trigger type 1 or 2 (playback)
                                                                  [1] - number of events to trigger
                                                                  [2] - period multiplier, depends on range (0-0x7FFF)
                                                                  [3] - small (0) or large (1)
								        small: minimum of 120ns, increments of 30ns up to 983.13us
                                                                        large: minimum of 120ns, increments of 30.72us up to 1.007s */
} board_ti;

/** CTP configuration parameters **/
typedef struct {
  unsigned int slot;
  unsigned int ver;         /* version */
  unsigned int rev;         /* revision */
  unsigned int sum_thr;         /* final sum threshold (32bit)*/
  unsigned int vme_slot_mask;   /* VME slot enable mask: bitmask: 31-0 */
  unsigned int pb_mask;         /* Payload enable mask: bitmask: 15-0 */
} board_ctp;
