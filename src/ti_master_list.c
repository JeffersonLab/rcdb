/*************************************************************************
 *
 *  vme_list.c - Library of routines for readout and buffering of 
 *                events using a JLAB Trigger Interface V3 (TI) with 
 *                a Linux VME controller.
 *
 */

/* Event Buffer definitions */
#define MAX_EVENT_POOL     10
#define MAX_EVENT_LENGTH   1024*60      /* Size in Bytes */

/* Define Interrupt source and address */
#define TI_MASTER


#define TI_READOUT TI_READOUT_EXT_POLL  /* Poll for available data, external triggers */
#define TI_ADDR    (21<<19)          /* GEO slot 3 */


#define TI_DATA_READOUT


/* Decision on whether or not to readout the TI for each block 
   - Comment out to disable readout 
*/


#define FIBER_LATENCY_OFFSET 0x40

#include "dmaBankTools.h"
#include "tiprimary_list.c" /* source required for CODA */

#include "fadcLib.h"        /* library of FADC250 routines */


#include  "confutils.h"
#include  "confutils.c"


#define BLOCKLEVEL 1
#define BUFFERLEVEL 10

//#define BUFFERLEVEL 1

unsigned int MAXFADCWORDS = 0;
unsigned int MAXTIWORDS = 0;


extern unsigned int tiTriggerSource;

/* Redefine tsCrate according to TI_MASTER or TI_SLAVE */
#ifdef TI_SLAVE
int tsCrate=0;
#else
#ifdef TI_MASTER
int tsCrate=1;
#endif
#endif



/* FADC Library Variables */
extern int fadcA32Base;
int FA_SLOT;

extern   int fadcID[20];
extern   int nfadc;                 /* Number of FADC250s verified with the library */
extern   int fadcID[FA_MAX_BOARDS]; /* Array of slot numbers, discovered by the library */
int NFADC;                          /* The Maximum number of tries the library will */

unsigned int fadcSlotMask   = 0;    /* bit=slot (starting from 0) */

char  *conf_dir;
char   conf_file[100];
char roc_name[ROCLEN];


/* function prototype */
void rocTrigger(int arg);

/****************************************
 *  DOWNLOAD
 ****************************************/
void
rocDownload()
{

  gethostname(roc_name,ROCLEN);
  
  conf_dir = getenv ("CONF_DIR");
  if (conf_dir == NULL)
    printf ("WRONG PATH TO CONFIG FILES  %s\n", conf_dir);

  printf ("CONFIG FILES TAKEN FROM  host: %s   conf_dir:  %s \n", roc_name, conf_dir);

  sprintf(conf_file,"%s/%s_pulser.cnf",conf_dir,roc_name);


  printf ("OPEN CONFIG FILE   %s\n", conf_dir); 
  printf ("OPEN CONFIG FILE   %s\n", conf_file); 

  fadc250InitGlobals();

  printf(" TEST CONFIG FILE \n");
  printf(" TEST CONFIG FILE \n");


  fadc250ReadConfigFile(conf_file);

  printf(" TI_FOFT_TRIG %d  %d  %d  %d\n", ti_bd.ti_soft_trig[0],
	 ti_bd.ti_soft_trig[1], ti_bd.ti_soft_trig[2], ti_bd.ti_soft_trig[3]);


  fadcA32Base=0x09000000;



  /* Setup Address and data modes for DMA transfers
   *   
   *  vmeDmaConfig(addrType, dataType, sstMode);
   *
   *  addrType = 0 (A16)    1 (A24)    2 (A32)
   *  dataType = 0 (D16)    1 (D32)    2 (BLK32) 3 (MBLK) 4 (2eVME) 5 (2eSST)
   *  sstMode  = 0 (SST160) 1 (SST267) 2 (SST320)
   */
  vmeDmaConfig(2,5,1); 


  /*****************
   *   TI SETUP
   *****************/
  int overall_offset=0x80;

#ifndef TI_DATA_READOUT
  /* Disable data readout */
  tiDisableDataReadout();
  /* Disable A32... where that data would have been stored on the TI */
  tiDisableA32();
#endif

  // Trigger Sources:
  // TI_TRIGGER_PULSER    5
  
  tiSetTriggerSource(TI_TRIGGER_PULSER);
      
  /* Set needed TS input bits */
  //  tiEnableTSInput( TI_TSINPUT_1 | TI_TSINPUT_6  );
  

  /* Load the trigger table that associates 
     pins 21/22 | 23/24 | 25/26 : trigger1
     pins 29/30 | 31/32 | 33/34 : trigger2
  */

  tiLoadTriggerTable(2);
  
  tiSetTriggerHoldoff(1,10,0);
  tiSetTriggerHoldoff(2,10,0);
  
  /* Set the sync delay width to 0x40*32 = 2.048us */
  tiSetSyncDelayWidth(0x54, 0x40, 1);
  
  /* Set the busy source to non-default value (no Switch Slot B busy) */
  tiSetBusySource(TI_BUSY_LOOPBACK,1); 

  /* Set number of events per block */
  tiSetBlockLevel(BLOCKLEVEL);
  
  /* Set timestamp format 48 bits */
  tiSetEventFormat(3);
  
  
  tiSetBlockBufferLevel(BUFFERLEVEL);
  
  tiAddSlave(1);
  tiAddSlave(2);
  tiAddSlave(3);
  tiAddSlave(4);
  tiAddSlave(5);


  tiStatus();


  /***************************************
   * FADC Setup 
   ***************************************/
  /* Here, we assume that the addresses of each board were set according to their
   * geographical address (slot number):
   * Slot  3:  (3<<19) = 0x180000
   * Slot  4:  (4<<19) = 0x200000
   * ...
   * Slot 20: (20<<19) = 0xA00000
   */


  NFADC = 16+2;   /* 16 slots + 2 (for the switch slots) */


  //  NFADC = 1;

  //  MAXFADCWORDS = NFADC * BLOCKLEVEL * (1 + 2 + 200*16 + 1) + 2*32;
  //  MAXFADCWORDS = 2 * BLOCKLEVEL * (1 + 2 + 200*16 + 1) + 2*32;

  MAXFADCWORDS = 8 * BLOCKLEVEL * (1 + 2 + 100*16 + 1) + 2*32;


  /* Setup the iFlag.. flags for FADC initialization */
  int iFlag;
  iFlag = 0;
  /* Sync Source */
  iFlag |= (1<<0);    /* VXS */
  /* Trigger Source */
  iFlag |= (1<<2);    /* VXS */
  /* Clock Source */
  //  iFlag |= (1<<5);    /* VXS */
  iFlag |= (0<<5);    /* self*/


  vmeSetQuietFlag(1); /* skip the errors associated with BUS Errors */
  

  //  faInit((unsigned int)(4<<19),(unsigned int)(1<<19),NFADC,iFlag);
  if(AllSl == 0) {
    iFlag |= (1<<17);   /* activate useing fadcAddrList in faInit */
    /*  faInit((unsigned int)(3<<19),(1<<19),Naddr,iFlag); */
    
    faInit(fadcAddrList[0],0,Naddr,iFlag);
  } else 
    faInit((unsigned int)(3<<19),(unsigned int)(1<<19),18,iFlag);
  

  vmeSetQuietFlag(0); /* Turn the error statements back on */
  

  NFADC=nfadc;        /* Redefine our NFADC with what was found from the driver */
    
  printf("\n");
  printf(" TEST  NUMBER of FADCS INITIALIZED  %d \n",NFADC);
  printf("\n");

  int slot;

  for(slot = 0;slot < NFADC;slot++){

    FA_SLOT = fadcID[slot];
    fadcSlotMask |= (1<<FA_SLOT); /* Add it to the mask */

    /* if token = 0 then send via P2 else via VXS */
    faEnableMultiBlock(1);
  }


  fadc250DownloadAll();
  


  /***************************************
   *   SD SETUP
   ***************************************/
  sdInit();   /* Initialize the SD library */

  printf("TEST 0x%x",fadcSlotMask); 

  sdSetActiveVmeSlots(fadcSlotMask);    /* Use the fadcSlotMask to configure the SD */
  sdStatus();



#if 0
  /***************************************
   *   CTP  SETUP
   ***************************************/

  ctpInit();

  ctpSetFinalSumThreshold(230,0);
  //  ctpSetFinalSumThreshold(1230,0);

  printf(" CTP final sum threshold %d \n",ctpGetFinalSumThreshold());

  unsigned int ctp_vmemask = 1<<9;
  //  unsigned int ctp_vmemask = 1<<5;
  //  ctp_vmemask |= (1 << 5);
  //  ctp_vmemask |= (1 << 13);

  ctpSetVmeSlotEnableMask(ctp_vmemask);


  printf("----------------------------- \n");
  ctpStatus();
  printf("----------------------------- \n");

#endif

#if 0
  int iwait=0;
  int allchanup=0;
  while(allchanup  != (0x7) )
    {
      iwait++;
      allchanup = ctpGetAllChanUp();
      if(iwait>1000)
        {
          printf("iwait timeout   allchup - 0x%x\n",allchanup);
          break;
        }
    }
#endif




  printf("rocDownload: User Download Executed\n");



}

/****************************************
 *  PRESTART
 ****************************************/
void
rocPrestart()
{
  unsigned short iflag;
  int stat;
  int islot;

  /* Unlock the VME Mutex */
  vmeBusUnlock();

 /* FADC Perform some resets, status */
  for(islot=0;islot<NFADC;islot++) 
    {
      FA_SLOT = fadcID[islot];

      printf("Enable FADC in slot %d\n",FA_SLOT);


      faSetClkSource(FA_SLOT,2);
      //      faClear(FA_SLOT);

      faResetToken(FA_SLOT);
      faResetTriggerCount(FA_SLOT);
      
      faEnable(FA_SLOT,0,0);
      faStatus(FA_SLOT,0);

      // Enable Playback mode for fADC250 in slot FA_SLOT
      //      faPPGEnable(FA_SLOT);
    }

#if 0
  
  /*  Enable FADC */
  for(islot=0;islot<NFADC;islot++) 
    {
      FA_SLOT = fadcID[islot];
      //      faChanDisable(FA_SLOT,0xffff);

      faSetMGTTestMode(FA_SLOT,0);

      faEnable(FA_SLOT,0,0);

      faStatus(FA_SLOT,0);

    }
#endif



  tiStatus();

  sdStatus();

  //  ctpStatus();

   printf("rocPrestart: User Prestart Executed\n");
  /* SYNC is issued after this routine is executed */

 
}

/****************************************
 *  GO
 ****************************************/
void
rocGo()
{
   int iwait = 0;
   int allchanup = 0;
   int islot;

  /* Enable modules, if needed, here */
  //tiSoftTrig(int trigger, unsigned int nevents, unsigned int period_inc, int range)  
   //   tiSoftTrig(1, 40, 20000, 1);

   
   printf(" NUMBER OF SOFT TRIGEGRS = 40 \n");


   tiSoftTrig(ti_bd.ti_soft_trig[0], ti_bd.ti_soft_trig[1], ti_bd.ti_soft_trig[2],	      
   	      ti_bd.ti_soft_trig[3]);




#if 0
  /*  Enable FADC */
  for(islot=0;islot<NFADC;islot++) 
    {
      FA_SLOT = fadcID[islot];
      faSetMGTTestMode(FA_SLOT, 1);
    }
#endif  


#if 0
  while(allchanup  != (0x7) )
    {
      iwait++;
      allchanup = ctpGetAllChanUp();
      if(iwait>1000)
        {
          printf("iwait timeout   allchup - 0x%x\n",allchanup);
          break;
        }
    }
#endif



  //  getchar();
  //  tiSyncReset();
  


}

/****************************************
 *  END
 ****************************************/
void
rocEnd()
{

  int islot;


  faPPGDisable(FA_SLOT);


  /* FADC Disable */
  for(islot=0;islot<NFADC;islot++) 
    {
      FA_SLOT = fadcID[islot];
      faDisable(FA_SLOT,0);
      faStatus(FA_SLOT,0);

      //      faReset(FA_SLOT,0);

    }


  sdStatus();
  tiStatus();



  printf("rocEnd: Ended after %d blocks\n",tiGetIntCount());
  



}

/****************************************
 *  TRIGGER
 ****************************************/
void
rocTrigger(int arg)
{
  int ii, islot;
  int stat=0, dCnt, len=0, idata;

  int  itime,  gbready;

  int roflag=1;

  static unsigned int roEventNumber=0;

  tiSetOutputPort(1,0,0,0);

  printf(" Inside rocTrigger \n");


#ifdef TI_DATA_READOUT
  /*  BANKOPEN(4,BT_UI4,0); */

  vmeDmaConfig(2,3,0); 
  //  dCnt = tiReadBlock(dma_dabufp,8+(3*BLOCKLEVEL),1);
  dCnt = tiReadTriggerBlock(dma_dabufp,8+(3*BLOCKLEVEL),1);

  printf(" tiReadTriggerBlock %d \n",dCnt);

  if(dCnt<=0)
    {
      printf("No data or error.  dCnt = %d\n",dCnt);
    }
  else
    {
      dma_dabufp += dCnt;
      printf(" Add to buffer \n",dCnt);
    }

  /*  BANKCLOSE; */
#endif


  printf(" Before reading out bank 5 \n");

#if 0
  BANKOPEN(5,BT_UI4,BLOCKLEVEL);
  *dma_dabufp++ = LSWAP(tiGetIntCount());
  *dma_dabufp++ = LSWAP(0xdead);
  *dma_dabufp++ = LSWAP(0xcebaf111);
  *dma_dabufp++ = 0xcebaf222;
  BANKCLOSE;
#endif


  printf(" Read out TI record \n");


  // READOUT FADC

  BANKOPEN(6,BT_UI4,BLOCKLEVEL);

    /* Readout FADC */
  /* Configure Block Type... temp fix for 2eSST trouble with token passing */
  if(NFADC!=0)
    {
      FA_SLOT = fadcID[0];
      for(itime=0;itime<100;itime++) 
	{
	  gbready = faGBready();
	  stat = (gbready == fadcSlotMask);
	  if (stat>0) 
	    {
	      break;
	    }
	}
      if(stat>0) 
	{
	  if(NFADC>1) roflag=2; /* Use token passing scheme to readout all modules */

          printf("Read out FADC250 \n");

	  dCnt = faReadBlock(FA_SLOT,dma_dabufp,MAXFADCWORDS,roflag);
	  if(dCnt<=0)
	    {
	      printf("FADC%d: No data or error.  dCnt = %d\n",FA_SLOT,dCnt);
	    }
	  else
	    {
	      dma_dabufp += dCnt;
	    }
	} 
      else 
	{
	  printf ("FADC%d: no events   stat=%d  intcount = %d   gbready = 0x%08x  fadcSlotMask = 0x%08x\n",
		  FA_SLOT,stat,tiGetIntCount(),gbready,fadcSlotMask);
	}

      /* Reset the Token */
      if(roflag==2)
	{
	  for(islot=0; islot<NFADC; islot++)
	    {
	      FA_SLOT = fadcID[islot];
	      faResetToken(FA_SLOT);
	    }
	}
    }

  /* Add some addition data here, as necessary 
   * Use LSWAP here to be sure they are added with the correct byte-ordering 
   */
  //  *dma_dabufp++ = LSWAP(0x1234);

  BANKCLOSE;


  tiSetOutputPort(0,0,0,0);

}

void rocCleanup()
{
  int islot=0;
  
  /*
   * Perform a RESET on all FADC250s.
   *   - Turn off all A32 (block transfer) addresses
   */
  /*   printf("%s: Reset all FADCs\n",__FUNCTION__); */
  
  for(islot=0; islot<NFADC; islot++)
    {
      FA_SLOT = fadcID[islot];
      faReset(FA_SLOT,1); /* Reset, and DO NOT restore A32 settings (1) */
    }
    
}
