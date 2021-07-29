#include <math.h>

#include <iostream>
#include <vector>
#include <thread>
#include <fstream>

#include <cmath>

double **sztable = nullptr;
int *it_table = nullptr;
double *sin_table = nullptr;
double *t_table = nullptr;
int mul = 4;
short rec_tmp_[4][128];

void construct_lookup_table(){
    unsigned int nosm = 32;

    unsigned int k = 0, i = 0, j = 0, l = 0;
    double t,di,ns;
    sin_table= (double *) calloc(nosm*mul,sizeof(double));
    t_table= (double *) calloc(nosm*mul,sizeof(double));
    it_table= (int *) calloc(nosm*mul,sizeof(int));
    sztable = (double **) calloc(nosm*mul,sizeof(double *));
    for (i=0;i<nosm*mul;i++) { 
        if (!(*(sztable + i) = (double *) calloc(nosm,sizeof(double)))) {
            fprintf(stderr,"Memory allocation error!! \n");
            exit(12);
        };
    }

    ns = (double)nosm;

    for(i=0,j=0;i<nosm;i++) {
        for(k=0;k<mul;k++,j++) {
            t=i+(double)k/mul;
            *(sin_table+j) = sin(t*M_PI);
            *(t_table+j) = t;
            *(it_table+j) = (int)t;

            for (l=0;l<nosm;) {
                di = t-l;
                /* even side */
                *(*(sztable+j)+l) =  1.0/(di+ns) + 1.0/di + 1.0/(di-ns);
                /* odd side */
                di = ++l-t;
                *(*(sztable+j)+l++) =  1.0/(di+ns) + 1.0/di + 1.0/(di-ns);
            }
        }
    }
}


short optimized_value(int num_sampl, short* sampl,int h){
    /* assumes even num_sampl */
    int i,it;
    double sz1,sina,t;
//    ns = num_sampl; /* make it double! */

    t = t_table[h];
    // only to see if t==it (integer time point)
    it = it_table[h];

    // if time point is at a sample, also, Sin_table is 0 here
    if (t-it==0.0) {
        return sampl[it];
    }

    sina=sin_table[h];

    for(i=0,sz1=0.0;i<num_sampl;i++) {
        sz1+=sampl[i] * sztable[h][i]; // sz - weight of i-th sample in computing value at the h-th time point
    }
    return (int)(sina*sz1/M_PI);
}

void load_restore_one_spike(short waveshape[4][32], std::ofstream& out, int chno){

    // reconstruct using interpolation of mul-1 values in-between sampled ones
    for(int i=0,h=0;i<32;i++) {
        for(unsigned int k=0;k<mul;k++,h++) {
            for(int j=0;j<chno;j++) {
                rec_tmp_[j][i*mul+k]=optimized_value(32, waveshape[j], h);
            }
        }
    }

    // copy from temporary array to spike object array
//    for(int chan = 0; chan < spike->num_channels_; ++chan){
//        memcpy(spike->waveshape[chan], rec_tmp_[chan], 128*sizeof(ws_type));
//    }
//

    // WRITE TO FILE!
    for(int j=0;j<chno;j++) {
        out.write((char*)rec_tmp_[j], 128*sizeof(short));
    }
}

int main(int argc, char** argv)
{
// 1-by-1: load ws, interpolate, write
	std::ifstream spk_stream(argv[2]);
	std::ofstream out("test.out");

	int chno = atoi(argv[1]);
	short waveshape[4][32];

	construct_lookup_table();

	while (!spk_stream.eof()){
//              spike->waveshape = new int*[chno];

                for (int c=0; c < chno; ++c){
		    spk_stream.read((char*)waveshape[c], 32 * sizeof(short));
                }

		load_restore_one_spike(waveshape, out, chno);
	}
}
