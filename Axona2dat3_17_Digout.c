// PS 110923: Program reads Axona .BIN file, extracts and saves all 64 channels and writes them as binary file. Furthermore, it extracts the Axona tracking. Tracking data contains sample number when tracking was written for alignment with e-phys recordings. Tracking data is saved in text file (.axtrk).

//Program is not cleaed up, outputs tracking data but does not write to file. It also contains some obsolete options that refer to the origian Axona2dat2 program extracting tracking data from .trk file.

// Program also extracts digital inputs (DI) from .bin file and puts them into .digbin file. Optionally, DI channes can be included into the .dat file to make up channels 64 - 79.

// Version _17: - Also extracts digital output channels.


#define _LARGEFILE_SOURCE
#define _FILE_OFFSET_BITS 64

#define TITLE_STRING "Axona2dat3_xx v 2.x: 11 November 2015 (PS). Based in original program by JRH."

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
  FILE *fpin,*fpout,*fpouttrk,*fpoutdigbin,*fpoutdigbout;
  char temp_str[256],path_prog[256],path_data[256],rcfile[256],basename[256],outfile[256],*perror,outtrack[256],outdigbin[256],outdigbout[256];
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
  int setpause=0, outdat=1, diindat =0, doindat =0, outwhd=1, syncpin=2, set_align=1, maxinv=0, setled=0;
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

 
  union digitalInputs { 
  struct {
    unsigned di_01:1,di_02:1,di_03:1,di_04:1,di_05:1,di_06:1,di_07:1,di_08:1,di_09:1,
      di_10:1,di_11:1,di_12:1,di_13:1,di_14:1,di_15:1,di_16:1,di_17:1,di_18:1,di_19:1,
      di_20:1,di_21:1,di_22:1,di_23:1,di_24:1,di_25:1,di_26:1,di_27:1,di_28:1,di_29:1,
      di_30:1,di_31:1,di_32:1;
  } fields; /*Actually, there are 16 digital inputs followed by 2 bytes sync inputs.*/
  unsigned int bits; 
  };


  /* Axona data packet structure */
  struct AxonaRawPacket {
    char id[4];	// Record ID - "ADU1" = standard packet, "ADU2" = tracker data present
    unsigned int n;	// The number of the packet (4 bytes)
    union digitalInputs digio;	// Digital inputs and sync inputs (4 bytes, 32 bits). First 16 bits are digital inputs.
    //char track[20];	// Tracking info - 20 bytes
    //short int track[10];	// Tracking info - 20 bytes
    unsigned int frame_counter;
    short int track[8];
    short int data[192];// Data: 3 sequential 2-byte samples from 64 channels (1-64, 1-64, 1-64)
    union digitalInputs digo;	// Keystroke record - function key code
    // char keycode;	// Keystroke record - key code
    char pad[12];	// Unused bytes
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
  short int digoData[16];    //i.e. 32 bytes
  size_digData=sizeof(digData);

  union digitalInputs digitalInputBlock[BLOCKSIZE], digitalOutputBlock[BLOCKSIZE];
  size_di=sizeof(union digitalInputs);

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
    fprintf(stderr,"4. Creates a binary .digbout file containing digital output channels.\n");
    fprintf(stderr,"   .digbout file contains two byes for every data packet that contain the digital outputs.\n");
    fprintf(stderr,"Valid arguments - defaults in []\n");
    fprintf(stderr,"	-outdat: output dat file? 0=no, 1=yes [%d]\n",outdat);
    fprintf(stderr,"	-diindat: digital inputs in dat file? 0=no, 1=yes [%d]\n",diindat);
    fprintf(stderr,"	-doindat: digital outputs in dat file? 0=no, 1=yes [%d]\n",doindat);
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
  if(outdat==1) {
    if((fpout=fopen(outfile,"wb"))==NULL) printf("error\n");
    printf("output .dat file: %s\n",outfile);
  }

  sprintf(outtrack,"%s.axtrk\0",basename); // should create output file name for tracking
  fpouttrk=fopen(outtrack,"w");
  if(fpouttrk!=NULL) {printf("output .axtrk file: %s\n",outtrack);}
  else {printf("Output .axtrk file %s could not be opened.\n", outtrack);}

  sprintf(outdigbin,"%s.digbin\0",basename); // should create output file name for digital input and output channels
  sprintf(outdigbout,"%s.digbout\0",basename); // should create output file name for digital input and output channels
  fpoutdigbin=fopen(outdigbin,"wb");
  fpoutdigbout=fopen(outdigbout,"wb");
  if(fpoutdigbin!=NULL) {printf("\n",outdigbin);}
  else {printf("Output digbin file %s could not be opened.\n", outdigbin);}


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

      if(axraw[i].id[3] == '2') // If the current block contains tracking data
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

      if(outdat==1)    // prepare digital input structures
	{
	  digitalInputBlock[i] = axraw[i].digio;        // Fill array of bitfields with digital inputs

	  /* Convert bitfields into short int array to treat digital inputs like normal channels */
	  for (di_channel_counter=0;di_channel_counter<16;di_channel_counter++) digData[di_channel_counter] = 0;    //fill entire array with zeros
	  // find those digital input channels that are at 1 and fill them into the output array
	  if((axraw[i].digio.fields.di_01 & 1)==1) digData[0] = 10000;
	  else if((axraw[i].digio.fields.di_02 & 1)==1) digData[1] = 10000;
	  else if((axraw[i].digio.fields.di_03 & 1)==1) digData[2] = 10000;
	  else if((axraw[i].digio.fields.di_04 & 1)==1) digData[3] = 10000;
	  else if((axraw[i].digio.fields.di_05 & 1)==1) digData[4] = 10000;
	  else if((axraw[i].digio.fields.di_06 & 1)==1) digData[5] = 10000;
	  else if((axraw[i].digio.fields.di_07 & 1)==1) digData[6] = 10000;
	  else if((axraw[i].digio.fields.di_08 & 1)==1) digData[7] = 10000;
	  else if((axraw[i].digio.fields.di_09 & 1)==1) digData[8] = 10000;
	  else if((axraw[i].digio.fields.di_10 & 1)==1) digData[9] = 10000;
	  else if((axraw[i].digio.fields.di_11 & 1)==1) digData[10] = 10000;
	  else if((axraw[i].digio.fields.di_12 & 1)==1) digData[11] = 10000;
	  else if((axraw[i].digio.fields.di_13 & 1)==1) digData[12] = 10000;
	  else if((axraw[i].digio.fields.di_14 & 1)==1) digData[13] = 10000;
	  else if((axraw[i].digio.fields.di_15 & 1)==1) digData[14] = 10000;
	  else if((axraw[i].digio.fields.di_16 & 1)==1) digData[15] = 10000;

	  digitalOutputBlock[i] = axraw[i].digo;        // Fill array of bitfields with digital outputs

	  if (axraw[i].digo.bits > 0){
		//digitalOutputBlock[i].fields.di_04 = 1;
		//digitalOutputBlock[i].fields.di_05 = 1;
		//digitalOutputBlock[i].fields.di_16 = 1;
//		digitalOutputBlock[i].fields.di_15 = 1;
//		digitalOutputBlock[i].fields.di_14 = 1;
//		digitalOutputBlock[i].fields.di_13 = 1;
//		digitalOutputBlock[i].fields.di_12 = 1;
//		digitalOutputBlock[i].fields.di_11 = 1;
//		digitalOutputBlock[i].fields.di_10 = 1;
//		digitalOutputBlock[i].fields.di_09 = 1;
//		digitalOutputBlock[i].fields.di_08 = 1;
//		digitalOutputBlock[i].fields.di_07 = 1;
//		digitalOutputBlock[i].fields.di_06 = 1;
//		digitalOutputBlock[i].fields.di_01 = 1;
//		digitalOutputBlock[i].fields.di_02 = 1;
//		digitalOutputBlock[i].fields.di_03 = 1;
	  }

	}

      // fill datblock array with sample packets:
      if(outdat==1)
	for (j=0;j<192;j++) /*sort samples in *current packet**/
	  {
	    datblock[i].data[j] = axraw[i].data[remap[j]]+1; // sort original data into correct probe sequence
	  }


      // Now, axraw[i].data[0 through 191] contains 3 blocks of 62 samples. digData[0 through 15] contains 16 DI channels.
      // printf("i: %d\n",i);
      if(diindat==1)
	{
	  //printf("writing new extended_data_array\n");
	  n_extended=0;
	  for(block_counter=1;block_counter<=3;block_counter++)
	    {
	      //printf("Block: %d\n",block_counter);
	      for(sc=0;sc<64;sc++)      //loop thru set of 64 samples
		{
		  //printf("sample no.: %d\n",sc);
		  //printf("sample: %d\n",sc+64*(block_counter-1));
		  // Fill in one block of 64 samples
		  extended_datblock[i].ext_data[n_extended] = datblock[i].data[sc+64*(block_counter-1)];
		  n_extended+=1;
		}
	      for(dc=0;dc<16;dc++)      //loop thru digital channels
		{
		  //printf("digital channel: %d\n",dc);
		  //printf("DI: %d\n",dc);
		  // Fill in one block of 16 DI channels
		  extended_datblock[i].ext_data[n_extended] = digData[dc];
		  n_extended+=1;
		}
	    }
	}
      
    }

    if(outdat==1)
      {
	if(diindat==0) fwrite(datblock,size_out,BLOCKSIZE,fpout);  //write datblock array
	else fwrite(extended_datblock,size_out_extended,BLOCKSIZE,fpout);
	fwrite(digitalInputBlock,size_di,BLOCKSIZE,fpoutdigbin);
	fwrite(digitalOutputBlock,size_di,BLOCKSIZE,fpoutdigbout);
      }
    n+=BLOCKSIZE;
    //printf("Cumulated bin samples: %d\n", n*3);
  }


  /* Now output remaining records (<BLOCKSIZE) which were read in the final (unassigned) iteration in the above loop */  
  for(i=0;i<blocksread;i++) { /* loop thru all packets read into memory*/
    if(axraw[i].id[3] == '2')   // If the current block contains tracking data
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

    if(outdat==1)   // prepare digital input structures
      {
	digitalInputBlock[i] = axraw[i].digio;      // Fill array of bitfields with digital inputs
	digitalOutputBlock[i] = axraw[i].digo;      // Fill array of bitfields with digital inputs

	/* Convert bitfields into short int array to treat digital inputs like normal channels */
	for (di_channel_counter=0;di_channel_counter<16;di_channel_counter++) digData[di_channel_counter] = 0;    //fill entire array with zeros
	// find those digital input channels that are at 1 and fill them into the output array
	if((axraw[i].digio.fields.di_01 & 1)==1) digData[1] = 10000;
	else if((axraw[i].digio.fields.di_02 & 1)==1) digData[2] = 10000;
	else if((axraw[i].digio.fields.di_03 & 1)==1) digData[3] = 10000;
	else if((axraw[i].digio.fields.di_04 & 1)==1) digData[4] = 10000;
	else if((axraw[i].digio.fields.di_05 & 1)==1) digData[5] = 10000;
	else if((axraw[i].digio.fields.di_06 & 1)==1) digData[6] = 10000;
	else if((axraw[i].digio.fields.di_07 & 1)==1) digData[7] = 10000;
	else if((axraw[i].digio.fields.di_08 & 1)==1) digData[8] = 10000;
	else if((axraw[i].digio.fields.di_09 & 1)==1) digData[9] = 10000;
	else if((axraw[i].digio.fields.di_10 & 1)==1) digData[10] = 10000;
	else if((axraw[i].digio.fields.di_11 & 1)==1) digData[11] = 10000;
	else if((axraw[i].digio.fields.di_12 & 1)==1) digData[12] = 10000;
	else if((axraw[i].digio.fields.di_13 & 1)==1) digData[13] = 10000;
	else if((axraw[i].digio.fields.di_14 & 1)==1) digData[14] = 10000;
	else if((axraw[i].digio.fields.di_15 & 1)==1) digData[15] = 10000;
	else if((axraw[i].digio.fields.di_16 & 1)==1) digData[16] = 10000;
      }


    if(outdat==1)
      for (j=0;j<192;j++)
	{
	  datblock[i].data[j] = axraw[i].data[remap[j]]+1; // sort original data into correct probe sequence
	}


    // Now, axraw[i].data[0 through 191] contains 3 blocks of 62 samples. digData[0 through 15] contains 16 DI channels.
    //printf("i: %d\n",i);
    if(diindat==1)
      {
	//printf("writing new extended_data_array\n");
	n_extended=0;
	for(block_counter=1;block_counter<=3;block_counter++)
	  {
	    //printf("Block: %d\n",block_counter);
	    for(sc=0;sc<64;sc++)      //loop thru set of 64 samples
	      {
		//printf("sample no.: %d\n",sc);
		//printf("sample: %d\n",sc+64*(block_counter-1));
		// Fill in one block of 64 samples
		extended_datblock[i].ext_data[n_extended] = datblock[i].data[sc+64*(block_counter-1)];
		n_extended+=1;
	      }
	    for(dc=0;dc<16;dc++)      //loop thru digital channels
	      {
		//printf("digital channel: %d\n",dc);
		//printf("DI: %d\n",dc);
		// Fill in one block of 16 DI channels
		extended_datblock[i].ext_data[n_extended] = digData[dc];
		n_extended+=1;
	      }
	  }
      }
   

  }
  n+=blocksread;

  if(outdat==1)
    {
      if(diindat==0) fwrite(datblock,size_out,blocksread,fpout);  //write datblock array
      else fwrite(extended_datblock,size_out_extended,blocksread,fpout);
      fwrite(digitalInputBlock,size_di,blocksread,fpoutdigbin);
      fwrite(digitalOutputBlock,size_di,blocksread,fpoutdigbout);

      fclose(fpout);
    }

  fclose(fpin); 
  fclose(fpouttrk);
  fclose(fpoutdigbin);
  fclose(fpoutdigbout);
	
  minutes=(int)((n*3)/samprate/60.0);
  seconds=((n*3)/samprate-(minutes*60));

  printf("Duration: %d minutes %f seconds\n",minutes,seconds);
  printf("\n");
}


