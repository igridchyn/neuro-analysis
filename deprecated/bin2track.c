// PS 110923: Program reads Axona .BIN file, extracts and saves all 64 channels and writes them as binary file. Furthermore, it extracts the Axona tracking. Tracking data contains sample number when tracking was written for alignment with e-phys recordings. Tracking data is saved in text file (.axtrk).

//Program is not cleaed up, outputs tracking data but does not write to file. It also contains some obsolete options that refer to the origian Axona2dat2 program extracting tracking data from .trk file.

#define _LARGEFILE_SOURCE
#define _FILE_OFFSET_BITS 64

#define TITLE_STRING "Axona2dat3_xx v 2.x: 08 March 2012 (PS). Based in original program by JRH."

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <sys/types.h> /* must be included for directory reading */
#include <sys/stat.h> /* must be included for directory reading */

#define MAXLINELEN 10000
#define BLOCKSIZE 1000

main (int argc, char *argv[]) {

  /* general and file type variables */
  struct stat fileinfo; /* stat structure to hold file info */
  FILE *fpin,*fpout,*fpouttrk,*fpoutdigbin;
  char temp_str[256],path_prog[256],path_data[256],rcfile[256],basename[256],outfile[256],*perror,outtrack[256],outdigbin[256];
  int w,x,y,z,skip,fail,col,systemtype=0,allfiletot=0;
  unsigned long int i,j,k,n,n_extended;
  unsigned int dig_counter,bit_counter,block_counter,sc,dc;
  unsigned long int first_packet_no;
  short int l;
  float a,b,c;
  double aa,bb,cc;

  int *test; //???
  unsigned int end2=0;
  int extpos;

  /* per-line temporary variables */
  char line[MAXLINELEN],templine[MAXLINELEN],*pline,*pcol,*tempcol;
  int tempprobe=-1,tempcell=-1, tempspikes=-1;
  float tempx=-1.0,tempy=-1.0, temprate=0.0,tempcoh=0.0,tempspars=0.0,tempsize=0.0;

  /* command line arguments */
  int setpause=0, outdat=1, diindat =0, outwhd=1, syncpin=2, set_align=1, maxinv=0, setled=0;
  float  samprate=24000.0, camrate=25.0, whdrate=50.0, whdres=0.5;

  /* program-specific variable */
  char binfile[256],trackfile[256];
  short int  *syncval;
  unsigned long int *frametime,*whdtime,start,end,prev,frametot=0,framevalid=0,synctot=0,whdtot=0,whdvalid=0,lostframes=0;
  int binfiletot=0, trackfiletot=0,align=0,minutes=0;
  float seconds=0;
  int framesamps,camxmax=768, camymax=576;  /* maximum possible x/y coordinates for camera used (typically 768/576)  */
  int size_packet, size_tracking, size_out, size_out_extended, size_syncval, size_di, size_digData, blocksread,bitshift,bitmask;
  int tracking_counter,di_channel_counter;
  int remap[192]={ /* initialize array defining order in which Axona reads 3x64 channels  - first block of 64 only */
    32,33,34,35, 36,37,38,39, 0,1,2,3, 4,5,6,7,
    40,41,42,43, 44,45,46,47, 8,9,10,11, 12,13,14,15,
    48,49,50,51, 52,53,54,55, 16,17,18,19, 20,21,22,23,
    56,57,58,59, 60,61,62,63, 24,25,26,27, 28,29,30,31};
  float *framex,*framey,*framed, *whdx,*whdy,*whdd;
  float sampint,syncrate,syncint,camint,whdint,whdratio; // interval between samples for raw data, sync-signals, and framegrabber card
  float gapstart=0.0,gapend=0.0;

  
  struct digitalInputs {
    unsigned di_01:1,di_02:1,di_03:1,di_04:1,di_05:1,di_06:1,di_07:1,di_08:1,di_09:1,
      di_10:1,di_11:1,di_12:1,di_13:1,di_14:1,di_15:1,di_16:1,di_17:1,di_18:1,di_19:1,
      di_20:1,di_21:1,di_22:1,di_23:1,di_24:1,di_25:1,di_26:1,di_27:1,di_28:1,di_29:1,
      di_30:1,di_31:1,di_32:1;
  }; /*Actually, there are 16 digital inputs followed by 2 bytes sync inputs.*/


  /* Axona data packet structure */
  struct AxonaRawPacket {
    char id[4];	// Record ID - "ADU1" = standard packet, "ADU2" = tracker data present
    unsigned int n;	// The number of the packet (4 bytes)
    struct digitalInputs digio;	// Digital inputs and sync inputs (4 bytes, 32 bits). First 16 bits are digital inputs.
    //char track[20];	// Tracking info - 20 bytes
    //short int track[10];	// Tracking info - 20 bytes
    unsigned int frame_counter;
    short int track[8];
    short int data[192];// Data: 3 sequential 2-byte samples from 64 channels (1-64, 1-64, 1-64)
    char funkey;	// Keystroke record - function key code
    char keycode;	// Keystroke record - key code
    char pad[14];	// Unused bytes
  } axraw[BLOCKSIZE];
  size_packet=sizeof(struct AxonaRawPacket); /* define size of data packet */
 
  /* Tracking system data packet structure */
  struct trackPacket {
    int n;
    int redx ; int redy ; int redpix;
    int greenx ; int greeny ; int greenpix;
    int bluex ; int bluey ; int bluepix;
    int hd ; int x ; int y;
    int start; int end; 
    // the following are extra diagnostic values not to be used for tracking per se1
    int pad[6];
  } tracking;
  size_tracking=sizeof(struct trackPacket); /* define size of tracking packet */

  /* csicsvari data structure: 3 sequential 2-byte samples from 64 channels (1-64, 1-64, 1-64), i.e., 192 samples per output packet*/
  struct CsicsvariDat { short int data[192]; } datblock[BLOCKSIZE];   /*sizeof(short int) is 2 bytes*/
  size_out=sizeof(struct CsicsvariDat); /* define size of output packet */

  /* data array for digital inputs to be added to .dat file as 'normal' channels */
  short int digData[16];    //i.e. 32 bytes
  size_digData=sizeof(digData);

  struct digitalInputs digitalInputBlock[BLOCKSIZE];
  size_di=sizeof(struct digitalInputs);

  size_syncval=sizeof(short int);

  /* extended csicsvari data structure: 3 sequential blocks of 2-byte samples. Each block consists of 64 channels followed by 16 digital input channels. Data arrangement: 1-64 + 16, 1-64 + 16, 1-64 + 16, i.e., 240 samples per output packet*/
  struct extendedCsicsvariDat { short int ext_data[240]; } extended_datblock[BLOCKSIZE];   /*sizeof(short int) is 2 bytes*/
  size_out_extended=sizeof(struct extendedCsicsvariDat); /* define size of output packet */
	
  /* fill remap array with same remapping values for next 2 blocks of 64 */
  for(i=0;i<64;i++) {remap[i+64]=remap[i]+64 ; remap[i+128]=remap[i]+128; }


  /*********************************************************************************************************/
  /* Determine program path */
  /*********************************************************************************************************/
  printf("\n");
  strcpy(path_prog,*argv);

  /* read full-path filename from 1st argument, i.e. program path */
  i=0;
  while(path_prog[i]!=0) {if(path_prog[i]=='/') end2=i; i++;}
  path_prog[end2+1]=0; /* terminate input string after last "\" or "/" */
	

  /*********************************************************************************************************/
  /* Print instructions if only one argument */
  /*********************************************************************************************************/
  if(argc==1) {
    fprintf(stderr,"\n******************************************************************************\n");
    fprintf(stderr,"%s\n",TITLE_STRING);
    fprintf(stderr,"******************************************************************************\n");
    fprintf(stderr,"1. Create a .dat (Csicsvari raw data file) from an Axona .bin file\n");
    fprintf(stderr,"2. Creates an .axtrak text file containing tracking\n");
    fprintf(stderr,"3. Creates a binary .digbin file containing digital input channels and sync inputs.\n");
    fprintf(stderr,"   .digbin file contains four byes for every data packet. First two bytes are digital inputs.\n");
    fprintf(stderr,"\n");
    fprintf(stderr,"Valid arguments - defaults in []\n");
    fprintf(stderr,"	-outdat: output dat file? 0=no, 1=yes [%d]\n",outdat);
    fprintf(stderr,"	-diindat: digital inputs in dat file? 0=no, 1=yes [%d]\n",diindat);
    fprintf(stderr,"\n");
    fprintf(stderr,"Useage: Axona2dat3_xx.exe [axonafile] [OPTIONS]\n");
    fprintf(stderr,"\n");
    if(systemtype==1) printf("Error\n");
    exit(0);
  }

  /*********************************************************************************************************/
  /* read file names: arguments up to the first argument beginning with "-" */
  /*********************************************************************************************************/
  allfiletot=0;
  for (i=1;i<argc;i++) {
    if( *(argv[i]+0) == '-' ) break;
    else {
      stat(argv[i],&fileinfo);
      if((fileinfo.st_mode & S_IFMT) == S_IFDIR) printf("Error\n");
      allfiletot++;
      //printf("%s\n",argv[i]);

      binfiletot++;
      strcpy(binfile,argv[i]);			
    }}

  if(binfiletot!=1) printf("ERROR:exactly one raw Axona file (.bin) must be specified\n");

  printf("\n");

  strcpy(path_data,binfile);
  /* read .BIN file path */
  i=0; end2=0;
  while(path_data[i]!=0) {if(path_data[i]=='/') end2=i; i++;}
  path_data[end2+1]=0; /* terminate input string after last "/" */


  /*********************************************************************************************************/
  /* read remaining command line arguments: identifier starting with "-" followed by a value */
  /*********************************************************************************************************/
  for(i=0;i<argc;i++)
    {
      if( *(argv[i]+0) == '-' && i < argc-1) {
	if(strcmp(argv[i],"-outdat")==0) 	{ outdat=atoi(argv[i+1]);i++;}
	else if(strcmp(argv[i],"-diindat")==0) 	{ diindat=atoi(argv[i+1]);i++;}
	else printf("error\n");
      }
  }


  /*********************************************************************************************************/
  /* define basename for building other filenames */ 
  /*********************************************************************************************************/
  i=0;
  extpos =-1;
  while(binfile[i]!=0) {
	  if(binfile[i]=='.') {extpos=i;} /* zero-offset index of "." character - cannot actually be zero for valid filenames! */ 
		i++; /* at end of loop, this will be the index to the final null character */
	}
  //extpos++;  /* this now indicates first character after last "." */  
	if(extpos==0) {printf("ERROR: No file extesion found.\n");} /* result if "." is not found */
	i=extpos;

  for(j=0;j<i;j++) basename[j]=binfile[j]; basename[j]='\0';


  /*********************************************************************************************************/
  /* READ AXONA FILE */
  /*********************************************************************************************************/
  if(stat(binfile,&fileinfo)==-1) printf("error\n");
  else if((fileinfo.st_mode & S_IFMT) == S_IFDIR) printf("error\n");
  else if(fileinfo.st_size % size_packet != 0) {
    sprintf(temp_str,"input appears to be corrupt (byte-count %d suggests %.3f records)\0",fileinfo.st_size, ((float)fileinfo.st_size/(float)size_packet));}
  else {
    /* reserve memory for n+1 sync records (1 byte each) and frame capture times (unsigned int) */
    n= fileinfo.st_size/size_packet ;
    if((syncval=(short int *) malloc((n+1)*sizeof(short int)))==NULL) printf("insufficient memory\n");
  }
  /* create output filename, open binfile & outfile, as well as .axtrk and .digbin files */
  sprintf(outfile,"%s.dat\0",basename);

  if((fpin=fopen(binfile,"rb"))==NULL) printf("error\n");

  sprintf(outtrack,"%s.axtrk\0",basename); // should create output file name for tracking
  fpouttrk=fopen(outtrack,"w");
  if(fpouttrk!=NULL) {printf("output .axtrk file: %s\n",outtrack);}
  else {printf("Output .axtrk file %s could not be opened.\n", outtrack);}

  /* Read Axona file */
  n=0; // record counter, incriments by the number of blocks read each read-iteration
  blocksread=0; // counter for the number of data blocks read (BLOCKSIZE determines the number of blocks attempted to be read)
  tracking_counter=0;
  /*printf("%-10s%-10s%-10s%-10s%-10s%-10s%-10s%-10s%-15s%-15s%-15s\n",
    "Sample#","Packet#","Frame#","big_x","big_y","small_x","small_y","pix_big","pix_sml","tot_px","unused");*/
  fprintf(fpouttrk,"%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n",
	  "Sample#","Packet#","Frame#","big_x","big_y","small_x","small_y","pix_big","pix_sml","tot_px","unused");

  while((blocksread = fread(&axraw,size_packet,BLOCKSIZE,fpin)) == BLOCKSIZE) {
    /* the following will only happen if a full BLOCKSIZE number of data packets were read */ 
    for(i=0;i<BLOCKSIZE;i++) { /* loop thru all *packets* read into memory, i is packet counter*/
      if(n==0 && i==0) /* With the very first packet*/
	{
	  first_packet_no = axraw[i].n;
	}

      if(axraw[i].id[3] == 'B' || axraw[i].id[3] == 'F' || axraw[i].id[3] == '2') // If the current block contains tracking data
	{
	  tracking_counter++;

	  fprintf(fpouttrk,"%u\t%u\t%u\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\n",
		 ((axraw[i].n-first_packet_no)*3+1),
		 axraw[i].n,
		 axraw[i].frame_counter,
		 axraw[i].track[0],
		 axraw[i].track[1],
		 axraw[i].track[2],
		 axraw[i].track[3],
		 axraw[i].track[4],
		 axraw[i].track[5],
		 axraw[i].track[6],
		 axraw[i].track[7]);
	}
    } 
  }
  n+=blocksread;

  fclose(fpin); 
  fclose(fpouttrk);
  //fclose(fpoutdigbin);
	
  minutes=(int)((n*3)/samprate/60.0);
  seconds=((n*3)/samprate-(minutes*60));

  printf("Duration: %d minutes %f seconds\n",minutes,seconds);
  printf("\n");
}


