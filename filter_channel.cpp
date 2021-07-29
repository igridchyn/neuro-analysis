#include <iostream>
#include <vector>
#include <thread>
#include <fstream>

#define FILTINT

int main(int argc, char *argv[]){

    if (argc < 5){
	    std::cout << "USAGEL filter_channel (1)<dat file> (2)<channel number> (3)<filter file path> (4)<out path>\n";
    }

    int chan = atoi(argv[2]);
    char *datpath = argv[1];
    char *outpath = argv[4];
    char *filtpath = argv[3];

    std::ifstream fin(datpath);
    std::ifstream ffilt(filtpath);
    std::ofstream fout(outpath);

    // read filter
    std::vector<float> filter;
    std::vector<long long> filter_short;
    while (!ffilt.eof()){
        float f;
        ffilt >> f;
        filter.push_back(f); 

	filter_short.push_back((long long)(f * 50 * 1000));
    }

    std::cout << "Filter size " << filter.size() << "\n";

    // read batch -> filter -> write -> repeat
    int READSAMP = 240000;
    int NCHAN = 128;
    int BLOCK_SIZE = NCHAN * READSAMP * 2; // 2 = short size
    short *block = new short[READSAMP * NCHAN];

    int filtsize = filter.size();

    //short *chanfilt = new short[READSAMP];
    std::vector<short> chanfilt;
    chanfilt.resize(READSAMP);

    //short *sigtail = new short[filtsize - 1];
    std::vector<short> sigtail;
    sigtail.resize(filtsize - 1);

    time_t t_start = time(NULL);

    while (!fin.eof()){
        fin.read((char*)block, BLOCK_SIZE);
       
        // using end of previous buffer
        for (unsigned int i=0; i < filtsize - 1; ++i){
            float valfilt = .0;
            // tail part
            for (unsigned int j = 0; j < filtsize-i-1; ++j){
                valfilt += filter[j] + sigtail[j+i];
            }
            // new signal part
            for (unsigned int j = 0; j < i+1; ++j){
                valfilt += filter[filtsize - i + j] * block[j * 128 + chan];
            }

            chanfilt[i] = valfilt;
        }

        for (unsigned int i=0; i < READSAMP-filtsize; ++i){
            float valfilt = .0;
	    long long valfiltl = 0;
	    //long long *fptr = &filter_short[0];
	    // short *dptr = block + i*128 + chan // add 128 on every iteration
            for (unsigned int j=0; j < filtsize; ++j){
#ifdef FILTINT
		valfiltl += filter_short[j] * block[(i+j) * 128 + chan];
#else
                valfilt += filter[j] * block[(i+j) * 128 + chan];
#endif
            }
#ifdef FILTINT
            chanfilt[i+filtsize-1] = short(valfiltl >> 16); // was /50000
#else
            chanfilt[i+filtsize-1] = valfilt;
#endif
        }

        // copy tail: filtsize-1
        for (unsigned int i=0; i < filtsize-1; ++i){
            sigtail[i] = block[(READSAMP - filtsize + i + 1) * 128 + chan];
        }

        fout.write((char*)&chanfilt[0], READSAMP * 2);
    }

    long runt = time(NULL) - t_start;

    std::cout << "Copmleted in " << runt << "\n";
}
