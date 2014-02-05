#include "confutils.h"
#include "stdio.h"
#include <string.h>

int iFlag;
int Naddr;
int AllSl;

FADC250_CONF  fa250[Nfa250+1];
board_ti ti_bd;

#define SCAN_TI_SOFT(BKEYWORD,TI_SOFT)  \ 
if(strcmp(keyword,(BKEYWORD)) == 0){  	\
  sscanf (str_tmp, "%*s %d %d %d %d", &ti_soft[0], &ti_soft[1], &ti_soft[2], &ti_soft[3]); \
  printf(" SASCHA I AM HERE =======  %d \n",ti_soft[0]); \
  for(jj=0; jj < 4; jj++)(TI_SOFT)[jj] = ti_soft[jj]; \
}



#define SCAN_MSK \
	args = sscanf (str_tmp, "%*s %d %d %d %d %d %d %d %d   \
                                     %d %d %d %d %d %d %d %d", \
		       &msk[ 0], &msk[ 1], &msk[ 2], &msk[ 3], \
		       &msk[ 4], &msk[ 5], &msk[ 6], &msk[ 7], \
		       &msk[ 8], &msk[ 9], &msk[10], &msk[11], \
		       &msk[12], &msk[13], &msk[14], &msk[15])

#define SCAN_MSK_CH \
  args = sscanf (str_tmp, "%*s %s %s %s %s %s %s %s %s   \                                                                                                                                
                                %s %s %s %s %s %s %s %s \
                                     %s %s %s %s %s", \
                       &msk_ch[ 0], &msk_ch[ 1], &msk_ch[ 2], &msk_ch[ 3], \
                       &msk_ch[ 4], &msk_ch[ 5], &msk_ch[ 6], &msk_ch[ 7], \
                       &msk_ch[ 8], &msk_ch[ 9], &msk_ch[10], &msk_ch[11], \
                       &msk_ch[12], &msk_ch[13], &msk_ch[14], &msk_ch[15], \
                       &msk_ch[16], &msk_ch[17], &msk_ch[18], &msk_ch[19], &msk_ch[20]) 



#define GET_READ_MSK \
	SCAN_MSK; \
	ui1 = 0; \
	for(jj=0; jj<NCHAN; jj++) \
	{ \
	  if((msk[jj] < 0) || (msk[jj] > 1)) \
	  { \
	    printf("\nReadConfigFile: Wrong mask bit value, %d\n\n",msk[jj]); return(-6); \
	  } \
	  if(strcmp(keyword,"FADC250_ADC_MASK") == 0) msk[jj] = ~(msk[jj])&0x1; \
	  ui1 |= (msk[jj]<<jj); \
	}

#define SCAN_B_XSETS(BKEYWORD,BSTRUCT) \
  else if(strcmp(keyword,(BKEYWORD)) == 0) \
      { \
        sscanf (str_tmp, "%*s %x", &i1); \
	for(jj=3; jj<Nfa250; jj++) if(fa250[jj].group == gr) (BSTRUCT) = i1; \
      }

#define SCAN_B_SETS(BKEYWORD,BSTRUCT) \
  else if(strcmp(keyword,(BKEYWORD)) == 0) \
      { \
        sscanf (str_tmp, "%*s %d", &i1); \
	for(jj=3; jj<Nfa250; jj++) if(fa250[jj].group == gr) (BSTRUCT) = i1; \
      }

#define SCAN_B_MSKS(BKEYWORD,BSTRUCT) \
  else if(strcmp(keyword,(BKEYWORD)) == 0) \
      { \
	GET_READ_MSK; \
	for(jj=3; jj<Nfa250; jj++) if(fa250[jj].group == gr) (BSTRUCT) = ui1; \
	printf("\nReadConfigFile: %s = 0x%04x \n",keyword,ui1); \
      }

#define SCAN_TDP(TDP_K,TDP_S) \
  else if(strcmp(keyword,(TDP_K)) == 0)	\
      { \
        sscanf (str_tmp, "%*s %d", &ui1); \
	for(jj=3; jj<Nfa250; jj++)  if(fa250[jj].group == gr) \
	  for(ii=0; ii<NCHAN; ii++)   (TDP_S)[ii] = ui1; \
      }

#define SCAN_TDP_CH(TDP2_K,TDP2_S) \
  else if(strcmp(keyword,(TDP2_K)) == 0) \
      { \
        sscanf (str_tmp, "%*s %d %d", &chan, &ui1); \
        if((chan<3) || (chan>=NCHAN)) \
        { \
	  printf("\nReadConfigFile: Wrong channel number %d, %s\n",slot,str_tmp); \
	  return(-7); \
        } \
	for(jj=3; jj<Nfa250; jj++)  if(fa250[jj].group == gr)  (TDP2_S)[chan] = ui1; \
      }

#define SCAN_TDP_ALLCH(TDP3_K,TDP3_S) \
  else if(strcmp(keyword,(TDP3_K)) == 0) \
      { \
	SCAN_MSK; \
	if(args != 16) \
        { \
	  printf("\nReadConfigFile: Wrong argument's number %d, should be 16\n\n",args); \
          return(-8); \
        } \
	for(jj=3; jj<Nfa250; jj++)  if(fa250[jj].group == gr) \
  for(ii=0; ii<NCHAN; ii++)   (TDP3_S)[ii] = msk[ii]; \
      }

#define SCAN_SN_ALLCH(TDP4_K,TDP4_S) \
   else if(strcmp(keyword,(TDP4_K)) == 0) \
       { \
         SCAN_MSK_CH; \
         if(args != 21) \
         { \
            printf("\nReadConfigFile: Read Serial Number:  Wrong number of slots %d, should be 21   %s\n\n",args,msk_ch[3]); \
            return(-8); \
          } \
         for(jj=3; jj<Nfa250; jj++){ printf("\n SERIAL NUMBER%s\n",msk_ch[jj]); sprintf( TDP4_S,"%s", msk_ch[jj]); } \
       }



int fadc250ReadConfigFile(char *filename)
{
  FILE   *fd;
  char   fname[FNLEN] = { "" };  /* config file name */
  int    ii, jj, ch;
  char   str_tmp[STRLEN], str2[STRLEN], keyword[ROCLEN];
  char   host[ROCLEN], ROC_name[ROCLEN];
  int    args, i1, i2, msk[16];

  char   msk_ch[21][12];

  int    slot, chan, gr = 0;
  unsigned int  ui1, ui2;

  int  ti_soft[4];


  /* Obtain our hostname */
  gethostname(host,ROCLEN);
  AllSl = 0;

  sprintf(fname, "%s", filename);

  /* Open config file */
  if((fd=fopen(fname,"r")) == NULL)
  {
    printf(BOLDRED "\nReadConfigFile: Cannot open config file >%s<\n" RESET,fname);
    return(-2);
  }
  printf("\nReadConfigFile: Using configuration file >%s<\n",fname);


  /* Parsing of config file */
  while ((ch = getc(fd)) != EOF)
  {
    if ( ch == '#' || ch == ' ' || ch == '\t' )
    {
      while (getc(fd) != '\n') {}
    }
    else if( ch == '\n' ) {}
    else
    {
      ungetc(ch,fd);
      fgets(str_tmp, STRLEN, fd);
      sscanf (str_tmp, "%s %s", keyword, ROC_name);


      /* Start parsing real config inputs */
      if(strcmp(keyword,"CRATE") == 0)
      {
	//if(strcmp(ROC_name,host) != 0)
      //  {
	  //printf(BOLDRED "\nReadConfigFile: Wrong crate name in config file, %s\n" RESET, str_tmp);
      //    return(-3);
      //  }
	printf(BOLDBLUE "\nReadConfigFile: conf_CRATE_name = %s  host = %s\n" RESET, ROC_name, host);
      }

      else if(strcmp(keyword,"FADC250_ALLSLOTS") == 0)
      {
	AllSl = 1;
	gr++;
	for(jj=3; jj<Nfa250; jj++)  if(jj!=11 && jj!=12)  fa250[jj].group = gr;
      }

      else if(strcmp(keyword,"FADC250_SLOTS") == 0)
      {
	gr++;
	SCAN_MSK;
	printf("\nReadConfigFile: gr = %d     args = %d \n",gr,args);

	for(jj=0; jj<args; jj++)
	{
	  slot = msk[jj];
	  if(slot<3 || slot==11 || slot==12 || slot>20)
	  {
	    printf("\nReadConfigFile: Wrong slot number %d, %s\n",slot,str_tmp);
	    return(-4);
	  }
	  fa250[slot].group = gr;
	}
      }

      SCAN_B_XSETS("FADC250_F_REV",   fa250[jj].f_rev)

      SCAN_B_XSETS("FADC250_B_REV",   fa250[jj].b_rev)

      SCAN_B_XSETS("FADC250_ID",      fa250[jj].b_ID)

      SCAN_B_SETS("FADC250_MODE",     fa250[jj].mode)

      SCAN_B_SETS("FADC250_W_OFFSET", fa250[jj].winOffset)

      SCAN_B_SETS("FADC250_W_WIDTH",  fa250[jj].winWidth)

      SCAN_B_SETS("FADC250_NSB",      fa250[jj].nsb)

      SCAN_B_SETS("FADC250_NSA",      fa250[jj].nsa)

      SCAN_B_SETS("FADC250_NPEAK",    fa250[jj].npeak)

      SCAN_B_MSKS("FADC250_ADC_MASK", fa250[jj].chDisMask)

      SCAN_B_MSKS("FADC250_TRG_MASK", fa250[jj].trigMask)


      SCAN_TDP("FADC250_TET",fa250[jj].thr)

      SCAN_TDP_CH("FADC250_CH_TET",fa250[jj].thr)

      SCAN_TDP_ALLCH("FADC250_ALLCH_TET",fa250[jj].thr)


      SCAN_TDP("FADC250_DAC",fa250[jj].dac)

      SCAN_TDP_CH("FADC250_CH_DAC",fa250[jj].dac)

      SCAN_TDP_ALLCH("FADC250_ALLCH_DAC",fa250[jj].dac)


      SCAN_TDP("FADC250_PED",fa250[jj].ped)

      SCAN_TDP_CH("FADC250_CH_PED",fa250[jj].ped)

      SCAN_TDP_ALLCH("FADC250_ALLCH_PED",fa250[jj].ped)
	
      SCAN_SN_ALLCH("FADC250_ALLSN",fa250[jj].SerNum)

      SCAN_TI_SOFT("TI_SOFT_TRIG",ti_bd.ti_soft_trig)

    }
  }
  fclose(fd);

  /* fill up fadcAddrList, to init only fadc250 from config file */
  Naddr = 0;
  if(AllSl == 0)   /* fill up only if FADC250_ALLSLOTS was not called */
    for(jj=3; jj<Nfa250; jj++)
      if(fa250[jj].group > 0)
      {
	//fadcAddrList[Naddr] = jj<<19;
	Naddr++;
	//printf("\nReadConfigFile:  ...fadcAddrList[%d] = 0x%08x  group=%d\n",
	       //(Naddr-1),fadcAddrList[Naddr-1], fa250[jj].group);
      }

  gr--;
  return(gr);
}

void
fadc250InitGlobals()
{
  int ii, jj;

  //nfadc = 0;

  for(jj=0; jj<Nfa250; jj++)
  {
    fa250[jj].group     = 0;
    fa250[jj].f_rev     = 0x0216;
    fa250[jj].b_rev     = 0x0908;
    fa250[jj].b_ID      = 0xfadc;
    fa250[jj].mode      = 1;
    fa250[jj].winOffset = 50;
    fa250[jj].winWidth  = 49;
    fa250[jj].nsb       = 3;
    fa250[jj].nsa       = 6;
    fa250[jj].npeak     = 1;
    fa250[jj].chDisMask = 0x0;
    fa250[jj].trigMask  = 0xffff;

    for(ii=0; ii<NCHAN; ii++)
    {
      fa250[jj].thr[ii] = 110;
      fa250[jj].dac[ii] = 3300;
      fa250[jj].ped[ii] = 210;
    }
  }
  /*
  for(jj=0; jj<Nfa250; jj++) printf("ReadConfigFile: ****** fa250[%d].group = %d \n",jj,fa250[jj].group);
  */

  /* Setup the iFlag.. flags for FADC initialization */
  iFlag = 0;
  /* Sync Source */
  iFlag |= (1<<0);    /* VXS */
  /* Trigger Source */
  iFlag |= (1<<2);    /* VXS */
  /* Clock Source */
  /*iFlag |= (1<<5);*/    /* VXS */
  iFlag |= (0<<5);    /* self*/
}

