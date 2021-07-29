// calculate channel-wise ripple scores - top percentile of power
// input - dat file format with power in the ripple range

#include <fstream>
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>

int main(int argc, char* argv[]){
	std::vector<short> powers;
	std::vector<short> sig;

	const unsigned int NSAMP = 24000;
	const unsigned int NCHAN=128;
	const unsigned int LEN = NSAMP * NCHAN;

	sig.resize(LEN);

	for (unsigned int c=0; c < 128; ++c){
		powers.clear();
		std::ifstream fin(argv[1], std::ios::binary);
		while (!fin.eof()){
			fin.read((char*)&sig[0], sizeof(short) * LEN);
			for (unsigned int s=0; s < NSAMP; ++s){
				powers.push_back(sig[s*NCHAN + c]);
			}
		}
		std::sort(powers.begin(), powers.end());
		std::cout << "SCORE CHANNEL " << c << ": " << powers[(powers.size() * 999) / 1000] << "\n";
	}
}
