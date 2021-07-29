#include <fstream>
#include <iostream>

int main(int argc, char **argv){
        std::ifstream fileIn1(argv[1]);
        std::ifstream fileIn2(argv[2]);

	fileIn1.seekg(0, std::ios::end);
	fileIn2.seekg(0, std::ios::end);

	unsigned long long fSize1 = fileIn1.tellg();
	unsigned long long fSize2 = fileIn2.tellg();
	//std::cout << "File sizes: " << fileIn1.tellg() << " and " << fileIn2.tellg() << "\n";
	if (fSize1 != fSize2){
		std::cout << "WARNING: File sizes differ (" << fSize1 << " and " << fSize2 << ")" << "\n";
		//exit(1);
	}

	fileIn1.seekg(0, std::ios::beg);
	fileIn2.seekg(0, std::ios::beg);
	
        std::ofstream fileOut(argv[3], std::ios::binary);

        std::ifstream *inStreams[] = {&fileIn1, &fileIn2};

        const unsigned int BLOCK_SIZE = 128;
	const unsigned int BUF_SIZE = 1024 * 1024;
	const unsigned int BLOCKS_IN_BUF = BUF_SIZE / BLOCK_SIZE;
        char *block = new char[BLOCK_SIZE];
	char *buffer = new char[BUF_SIZE];

        //unsigned int fileNumber = 0;
        while (!fileIn1.eof() || !fileIn2.eof()){
		unsigned int bufPtr = 0;
		while (bufPtr < BUF_SIZE && (!fileIn1.eof() || !fileIn2.eof())){		
                	inStreams[0]->read(buffer + bufPtr, BLOCK_SIZE * sizeof(char));
	                inStreams[1]->read(buffer + bufPtr + BLOCK_SIZE, BLOCK_SIZE * sizeof(char));
			bufPtr += 2 * inStreams[0]->gcount();
		}

                //inStreams[fileNumber]->read(buffer, BLOCK_SIZE * sizeof(char));
                if (bufPtr > 0)
	                fileOut.write(buffer, bufPtr * sizeof(char));
                //fileNumber = 1 - fileNumber;
        }
}

