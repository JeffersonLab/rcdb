/*************************************************************************
 *
 *  fadc_list.c - Library of routines for readout and buffering of 
 *                events using a JLAB Trigger Interface and
 *                Distribution Module (TID) AND one or more FADC250 
 *                with a Linux VME controller.
 *
 */

/* Event Buffer definitions */
#define MAX_EVENT_POOL     100
#define MAX_EVENT_LENGTH   1024*2000      /* Size in Bytes */

/* Define Interrupt source and address */
#define TI_SLAVE   /* Master accepts triggers and distributes them, if needed */
#define TI_READOUT TI_READOUT_TS_POLL  /* Poll for available data, external triggers */
#define TI_ADDR    (21<<19)              /* GEO slot 21 */

/* Decision on whether or not to readout the TI for each block 
   - Comment out to disable readout 
*/
#define TI_DATA_READOUT

#ifdef TI_SLAVE
int tsCrate=0;
#else
#ifdef TI_MASTER
int tsCrate=1;
#endif
#endif

#define FIBER_LATENCY_OFFSET 0x40  /* measured longest fiber length */

#include "dmaBankTools.h"
#include "tiprimary_list.c" /* source required for CODA */
#include "fadcLib.h"         /* Header for FADC250 library */
#include "remexLib.h"

/* FADC250 Global Definitions */
int faMode=1;
#define FADC_WINDOW_LAT      750  /* Trigger Window Latency */
#define FADC_WINDOW_WIDTH    375  /* Trigger Window Width */
#define FADC_DAC_LEVEL      3300  /* Internal DAC Level */
#define FADC_THRESHOLD       300  /* Threshold for data readout */

/* CTP */
#define CTP_THRESHOLD    4000


unsigned int fadcSlotMask   = 0;    /* bit=slot (starting from 0) */
extern   int fadcA32Base;           /* This will need to be reset from it's default
                                     * so that it does not overlap with the TID */
extern   int nfadc;                 /* Number of FADC250s verified with the library */
extern   int fadcID[FA_MAX_BOARDS]; /* Array of slot numbers, discovered by the library */
int NFADC;                          /* The Maximum number of tries the library will
                                     * use before giving up finding FADC250s */
int FA_SLOT;                        /* We'll use this over and over again to provide
				     * us access to the current FADC slot number */ 



/* for the calculation of maximum data words in the block transfer */
unsigned int MAXFADCWORDS = 0;
unsigned int MAXTIWORDS  = 0;

/* Global Blocklevel (Number of events per block) */
#define BLOCKLEVEL  1
#define BUFFERLEVEL 10

/* function prototype */
void rocTrigger(int arg);

/****************************************
 *  DOWNLOAD
 ****************************************/
void
rocDownload()
{
  int islot;

  remexSetCmsgServer("dafarm28");
  remexSetRedirect(1);
  remexInit(NULL,1);


  /* Setup Address and data modes for DMA transfers
   *   
   *  vmeDmaConfig(addrType, dataType, sstMode);
   *
   *  addrType = 0 (A16)    1 (A24)    2 (A32)
   *  dataType = 0 (D16)    1 (D32)    2 (BLK32) 3 (MBLK) 4 (2eVME) 5 (2eSST)
   *  sstMode  = 0 (SST160) 1 (SST267) 2 (SST320)
   */
  vmeDmaConfig(2,5,1); 

  /***************************************
   * TI Setup 
   ***************************************/
#ifndef TI_DATA_READOUT
  /* Disable data readout */
  tiDisableDataReadout();
  /* Disable A32... where that data would have been stored on the TI */
  tiDisableA32();
#endif

  /* Set crate ID */
  tiSetCrateID(0x02); /* ROC 1 */

/*   tiSetTriggerSource(TI_TRIGGER_TSINPUTS); */

  /* Set needed TS input bits */
/*   tiEnableTSInput( TI_TSINPUT_1 ); */

  /* Load the trigger table that associates 
     pins 21/22 | 23/24 | 25/26 : trigger1
     pins 29/30 | 31/32 | 33/34 : trigger2
  */
  tiLoadTriggerTable(0);

  tiSetTriggerHoldoff(1,10,0);
  tiSetTriggerHoldoff(2,10,0);

  /* Set the sync delay width to 0x40*32 = 2.048us */
  tiSetSyncDelayWidth(0x54, 0x40, 1);

  /* Set the busy source to non-default value (no Switch Slot B busy) */
/*   tiSetBusySource(TI_BUSY_LOOPBACK,1); */
/*   tiSetBusySource(0,1); */

  tiSetFiberDelay(0x40,FIBER_LATENCY_OFFSET);

  /* Set number of events per block */
  tiSetBlockLevel(BLOCKLEVEL);

  tiSetEventFormat(1);

  tiSetBlockBufferLevel(BUFFERLEVEL);

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
  fadcA32Base=0x09000000;

  /* Setup the iFlag.. flags for FADC initialization */
  int iFlag=0;
  /* Sync Source */
  iFlag |= (1<<0);    /* VXS */
  /* Trigger Source */
  iFlag |= (1<<2);    /* VXS */
  /* Clock Source */
  iFlag |= (0<<5);    /* Self */

  vmeSetQuietFlag(1); /* skip the errors associated with BUS Errors */
  faInit((unsigned int)(3<<19),(1<<19),NFADC,iFlag);
  NFADC=nfadc;        /* Redefine our NFADC with what was found from the driver */
  vmeSetQuietFlag(0); /* Turn the error statements back on */
  
  /* Calculate the maximum number of words per block transfer (assuming Pulse mode)
   *   MAX = NFADC * BLOCKLEVEL * (EvHeader + TrigTime*2 + Pulse*2*chan) 
   *         + 2*32 (words for byte alignment) 
   */
  if(faMode = 1) /* Raw window Mode */
    MAXFADCWORDS = NFADC * BLOCKLEVEL * (1+2+FADC_WINDOW_WIDTH*16) + 3;
  else /* Pulse mode */
    MAXFADCWORDS = NFADC * BLOCKLEVEL * (1+2+32) + 2*32;
  /* Maximum TID words is easier to calculate, but we can be conservative, since
   * it's first in the readout
   */
/*   MAXTIDWORDS = 8+(3*BLOCKLEVEL); */
  
  printf("**************************************************\n");
  printf("* Calculated MAX FADC words per block = %d\n",MAXFADCWORDS);
/*   printf("* Calculated MAX TID  words per block = %d\n",MAXTIDWORDS); */
  printf("**************************************************\n");
  /* Check these numbers, compared to our buffer size.. */
/*   if( (MAXFADCWORDS+MAXTIDWORDS)*4 > MAX_EVENT_LENGTH ) */
/*     { */
/*       printf("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"); */
/*       printf(" WARNING.  Event buffer size is smaller than the expected data size\n"); */
/*       printf("     Increase the size of MAX_EVENT_LENGTH and recompile!\n"); */
/*       printf("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"); */
/*     } */

  
  if(NFADC>1)
    faEnableMultiBlock(1);

  /* Additional Configuration for each module */
  fadcSlotMask=0;
  for(islot=0;islot<NFADC;islot++) 
    {
      FA_SLOT = fadcID[islot];      /* Grab the current module's slot number */
      fadcSlotMask |= (1<<FA_SLOT); /* Add it to the mask */

      /* Set the internal DAC level */
      faSetDAC(FA_SLOT,FADC_DAC_LEVEL,0);
      /* Set the threshold for data readout */
      faSetThreshold(FA_SLOT,FADC_THRESHOLD,0);
	
      /*  Setup option 1 processing - RAW Window Data     <-- */
      /*        option 2            - RAW Pulse Data */
      /*        option 3            - Integral Pulse Data */
      /*  Setup 200 nsec latency (PL  = 50)  */
      /*  Setup  80 nsec Window  (PTW = 20) */
      /*  Setup Pulse widths of 36ns (NSB(3)+NSA(6) = 9)  */
      /*  Setup up to 1 pulse processed */
      /*  Setup for both ADC banks(0 - all channels 0-15) */
      /* Integral Pulse Data */
      faSetProcMode(FA_SLOT,faMode,FADC_WINDOW_LAT,FADC_WINDOW_WIDTH,3,6,1,0);
	
      /* Bus errors to terminate block transfers (preferred) */
      faEnableBusError(FA_SLOT);
      /* Set the Block level */
      faSetBlockLevel(FA_SLOT,BLOCKLEVEL);

      /* Set the individual channel pedestals for the data that is sent
       * to the CTP
       */
      int ichan;
      for(ichan=0; ichan<16; ichan++)
	{
	  faSetChannelPedestal(FA_SLOT,ichan,0);
	}

    }

  /***************************************
   *   SD SETUP
   ***************************************/
  sdInit();   /* Initialize the SD library */
  sdSetActiveVmeSlots(fadcSlotMask); /* Use the fadcSlotMask to configure the SD */
  sdStatus();

  /*****************
   *   CTP SETUP
   *****************/
  ctpInit();

  ctpSetVmeSlotEnableMask(fadcSlotMask);

  ctpSetFinalSumThreshold(CTP_THRESHOLD, 0);
  ctpStatus();

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

  printf("rocDownload: User Download Executed\n");

}

/****************************************
 *  PRESTART
 ****************************************/
void
rocPrestart()
{
  unsigned short iflag;
  int stat,islot;

/*   tiSetup(21); */

// 03Apr2013, moved this into ctpInit()
/*   ctpFiberReset(); */

  /* FADC Perform some resets, status */
  for(islot=0;islot<NFADC;islot++) 
    {
      FA_SLOT = fadcID[islot];
      faSetClockSource(FA_SLOT,2);
      faClear(FA_SLOT);
      faResetToken(FA_SLOT);
      faResetTriggerCount(FA_SLOT);
      faStatus(FA_SLOT,0);
    }

  /* TI Status */
  tiStatus();

  /*  Enable FADC */
  for(islot=0;islot<NFADC;islot++) 
    {
      FA_SLOT = fadcID[islot];
      faChanDisable(FA_SLOT,0xffff);
      faSetMGTTestMode(FA_SLOT,0);
      faEnable(FA_SLOT,0,0);
    }

  sdStatus();
  ctpStatus();

  printf("rocPrestart: User Prestart Executed\n");
  /* SYNC is issued after this routine is executed */
}

/****************************************
 *  GO
 ****************************************/
void
rocGo()
{
  /* Enable modules, if needed, here */
  int iwait=0;
  int islot, allchanup=0;


  for(islot=0;islot<NFADC;islot++)
    {
      FA_SLOT = fadcID[islot];
      faChanDisable(FA_SLOT,0x0);
      faSetMGTTestMode(FA_SLOT,1);
    }

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

  /* Enable modules, if needed, here */

  /* Interrupts/Polling enabled after conclusion of rocGo() */
}

/****************************************
 *  END
 ****************************************/
void
rocEnd()
{
  int islot;

  /* FADC Disable */
  for(islot=0;islot<NFADC;islot++) 
    {
      FA_SLOT = fadcID[islot];
      faDisable(FA_SLOT,0);
      faStatus(FA_SLOT,0);
    }

  tiStatus();
  sdStatus();

  printf("rocEnd: Ended after %d blocks\n",tiGetIntCount());
  
}

/****************************************
 *  READOUT TRIGGER
 ****************************************/
void
rocTrigger(int arg)
{
  int islot;
  int dCnt, len=0, idata;
  int stat, itime, gbready;
  int roflag=1;
  int syncFlag=0;
  static unsigned int roEventNumber=0;


  roEventNumber++;
  syncFlag = tiGetSyncEventFlag();

  if(tiGetSyncEventReceived())
    {
      printf("%s: Sync Event received at readout event %d\n",
	     __FUNCTION__,roEventNumber);
    }

  if(syncFlag)
    {
      printf("%s: Sync Flag Received at readout event %d\n",
	     __FUNCTION__,roEventNumber);
/*       printf("  Sleeping for 10 seconds... \n"); */
/*       sleep(10); */
/*       printf("  ... Done\n"); */
    }

  /* Set high, the first output port */
  tiSetOutputPort(1,0,0,0);

  BANKOPEN(5,BT_UI4,0);
  *dma_dabufp++ = LSWAP(tiGetIntCount());
  *dma_dabufp++ = LSWAP(0xdead);
  *dma_dabufp++ = LSWAP(0xcebaf111);
  BANKCLOSE;

#ifdef TI_DATA_READOUT
  BANKOPEN(4,BT_UI4,0);

  vmeDmaConfig(2,5,1); 
  dCnt = tiReadBlock(dma_dabufp,8+(3*BLOCKLEVEL),1);
  if(dCnt<=0)
    {
      printf("No data or error.  dCnt = %d\n",dCnt);
    }
  else
    {
      dma_dabufp += dCnt;
    }

  BANKCLOSE;
#endif

  /* Readout FADC */
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
	  BANKOPEN(3,BT_UI4,0);
	  dCnt = faReadBlock(FA_SLOT,dma_dabufp,MAXFADCWORDS,roflag);
	  if(dCnt<=0)
	    {
	      printf("FADC%d: No data or error.  dCnt = %d\n",FA_SLOT,dCnt);
	    }
	  else
	    {
	      if(dCnt>=MAXFADCWORDS)
		{
		  printf("%s: WARNING.. faReadBlock returned dCnt >= MAXFADCWORDS (%d >= %d)\n",
			 __FUNCTION__,dCnt, MAXFADCWORDS);
		}
	      else 
		dma_dabufp += dCnt;
	    }
	  BANKCLOSE;
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


  /* Turn off all output ports */
  tiSetOutputPort(0,0,0,0);

}

/*
 * rocCleanup
 *  - Routine called just before the library is unloaded.
 */

void
rocCleanup()
{
  int islot=0;

  /*
   * Perform a RESET on all FADC250s.
   *   - Turn off all A32 (block transfer) addresses
   */
  printf("%s: Reset all FADCs\n",__FUNCTION__);
  
  for(islot=0; islot<NFADC; islot++)
    {
      FA_SLOT = fadcID[islot];
      faReset(FA_SLOT,1); /* Reset, and DO NOT restore A32 settings (1) */
    }
  
  remexClose();

}
