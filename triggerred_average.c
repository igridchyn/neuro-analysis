#include <fstream>
#include <iostream>
#include <vector>
#include <cmath>
#include <string>

int main(int argc, char* argv[]){
	unsigned int NSAMP = 2400000;
	unsigned int NCHAN;


	if (argc < 7){
		std::cout << "Usage: (1)<dat file> (2)<output file> (3)<light timestamps> (4)<number of channels> (5)<samples before pulse> (6)<samples after pulse>\n";
		exit(0);
	}

	std::cout << "Open " << argv[1] << "\n";
	std::cout.flush();

	std::ifstream fin(argv[1], std::ios::binary);
	std::ofstream fout(argv[2], std::ios::binary);

	NCHAN = std::stoi(std::string(argv[4]), NULL);
	unsigned int LEN = NSAMP * NCHAN;
	std::vector<short> sig;
	sig.resize(LEN);

	std::cout << "Number of channels: " << NCHAN << "\n";

	unsigned int TBEF = std::stoi(std::string(argv[5]), NULL);
	unsigned int TAFT = std::stoi(std::string(argv[6]), NULL);

	std::cout << "Time before / after the pulse: " << TBEF << " / " << TAFT << "\n";

	std::vector<std::vector<long> > triggerred_average;
	triggerred_average.resize(NCHAN);
	for (unsigned int c=0; c < NCHAN; ++c){
		triggerred_average[c].resize(TBEF+TAFT+1, 0);
	}
	std::vector<unsigned int> timestamps;
	std::ifstream fts(argv[3]);
	while (!fts.eof()){
		unsigned int ts;
		fts >> ts;
		timestamps.push_back(ts);
		std::cout << ts << " ";
	}
	std::cout << "\n";

	// current time
	unsigned int t = 0;
	// current timestamp, timestamp index
	unsigned int cts = timestamps[0];
	unsigned int ctsi = 0;
	std::vector<unsigned int> ntps;
	ntps.resize(TBEF+TAFT+1, 0);
	bool ts_over = false;
	while (!fin.eof()){
		if (ts_over){
			break;
		}

		fin.read((char*)&sig[0], sizeof(short) * LEN);
		for (unsigned int s=0; s < NSAMP; ++s, ++t){
			if (t > cts + TAFT){
				if (ctsi < timestamps.size() - 1){
					ctsi ++;
					cts = timestamps[ctsi];
					std::cout << "Next timestamp # " << ctsi << " = " << cts << "\n";
				}
				else {
					ts_over = true;
					std::cout << "Out of timestamps";
					break;
				}
			}
	
			if (t >= cts - TBEF && t <= cts + TAFT){
				for (unsigned int c = 0; c < NCHAN; ++c){
					triggerred_average[c][t - cts + TBEF] += (long)sig[s * NCHAN + c];

					// DEBUG
					//if (c == 28 && t - cts + TBEF == 100){
					//	std::cout << "SUM in chan 28, t = 100: " << triggerred_average[c][t - cts + TBEF] << "\n";
					//}
				}
				ntps[t - cts + TBEF] ++;
			}
		}
	}

	for (unsigned int t=0; t < triggerred_average[0].size(); ++t){
		// std::cout << "Number of samples for " << t << " = " << ntps[t] << "\n";
		for (unsigned int c=0; c < NCHAN; ++c){
			short s = 0;
			if (ntps[t] > 0){
				s = triggerred_average[c][t] / ntps[t];
				//if (c == 28 && t == 100){
				//	std::cout << triggerred_average[c][t] << " / " << ntps[t] << " = " << s << "\n";
				//}
			}
			//fout << s;
			fout.write((char*)&s, sizeof(short));
		}
	}
	fout.close();

	return 0;
}
