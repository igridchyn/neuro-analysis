#include <fstream>

int main(int argc, char **argv){
	std::ifstream fileIn(argv[1], std::ios::binary);

	std::string fileInPath(argv[1]);
	std::ofstream fileOut1(fileInPath + ".64.1");
	std::ofstream fileOut2(fileInPath + ".64.2");

	std::ofstream *outStreams[] = {&fileOut1, &fileOut2};

	const unsigned int BLOCK_SIZE = 432;
	char *buffer = new char[BLOCK_SIZE];
	
	unsigned int fileNumber = 0;
	while (!fileIn.eof()){
		fileIn.read(buffer, BLOCK_SIZE * sizeof(char));
		outStreams[fileNumber]->write(buffer, BLOCK_SIZE * sizeof(char));
		fileNumber = 1 - fileNumber;
	}
}
