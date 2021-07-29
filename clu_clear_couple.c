#include <vector>
#include <fstream>
#include <iostream>
#include <algorithm>

float ref_frac(std::vector<int> rescut, int ref_ms_1, int ref_ms_2, int& i1, int& i2){
	for (int i= 1; i < rescut.size(); ++i){
		int diff = rescut[i] - rescut[i-1];
		if (diff < 20 * ref_ms_1)
			i1 ++;
		if (diff < 20 * ref_ms_2)
			i2 ++;
	}
	return i2 > 0 ?  i1 / float(i2) : 0;
}

inline void isi_upd(int isi, int ref_ms_1, int ref_ms_2, int& i1, int& i2){
	if (isi < 20 * ref_ms_1)
		i1 += 1;
	if (isi < 20 * ref_ms_2)
		i2 += 1;
}

inline void isi_upd_rem(int isi, int ref_ms_1, int ref_ms_2, int& i1, int& i2){
	if (isi < 20 * ref_ms_1)
		i1 -= 1;
	if (isi < 20 * ref_ms_2)
		i2 -= 1;
}
//=================================================================================================================
template<typename T>
inline int len(const std::vector<T>& vec){
	return vec.size();
}
//=================================================================================================================
std::vector<int> ref_frac_inc(const std::vector<int>& rescut, const std::vector<int>& rescutnew, int ref_ms_1, int ref_ms_2, int& i1, int& i2, float& frac){
	// both res are sorted
	int m = 0;

	// print rescut, rescutnew

	if (len(rescutnew) == 0){
		frac = i2 > 0 ? i1 / float(i2) : 0;
		return rescut;
	}
	std::vector<int> rescutm(rescut.size() + rescutnew.size());

	int i = 1;
	int j = 0;

	// find first between rescut[0] and rescut[1]
	while (j < len(rescutnew) and rescutnew[j] < rescut[0]){
		// 2 new ISIs:
		isi_upd(rescut[0] - rescutnew[j], ref_ms_1, ref_ms_2, i1, i2);
		rescutm[m] = rescutnew[j];
		m += 1;
		j += 1;
	}

	rescutm[m] = rescut[0];
	m += 1;

	while (i < len(rescut) and j < len(rescutnew)){
		while (i < len(rescut) and rescut[i] < rescutnew[j]){
			rescutm[m] = rescut[i];
			m += 1;
			i += 1;
		}

		if (i == len(rescut))
			break;

		// 2 new ISIs:
		isi_upd(rescutnew[j] - rescut[i-1], ref_ms_1, ref_ms_2, i1, i2);
		isi_upd(rescut[i] - rescutnew[j], ref_ms_1, ref_ms_2, i1, i2);

		rescutm[m] = rescutnew[j];
		m += 1;

		j += 1;
	}

	// assigne the rest
	if (i >= len(rescut))
		while (j < len(rescut))
			rescutm[m++] = rescutnew[j++];
	else
		while (i < len(rescut))
			rescutm[m++] = rescut[i++];

	frac = i2 > 0 ? i1 / float(i2) : 0;
	return rescutm;
}
//=================================================================================================================
std::vector<int> ref_frac_inc_rem(const std::vector<int>& rescut, const std::vector<int>& rescutrem, int ref_ms_1, int ref_ms_2, int& i1, int& i2, float& frac){
	// both res are sorted
	// print rescut, rescutrem

	if (rescut.size() <= rescutrem.size()){
		i1 = 0;
		i2 = 0;
		frac = 0;
		std::cout << "WARNING: remove array larger than target array\n";
		return std::vector<int>();
	}

	std::vector<int>rescutm(rescut.size() -rescutrem.size());
	int m = 0;

	if (rescutrem.size() == 0){
		frac = i2 > 0 ? i1 / float(i2) : 0;
		return rescut;
	}

	int i = 0;
	int j = 0;
	// find first not excluded
	while (rescut[i] == rescutrem[j] && i+1 < rescut.size()){
		isi_upd_rem(rescut[i+1] - rescut[i], ref_ms_1, ref_ms_2, i1, i2);
		i ++;
		j ++;
	}
	
	while (i < rescut.size() && j < rescutrem.size()){
		while (i < rescut.size() && rescut[i] < rescutrem[j]){
			// if m == len(rescutm):
			// 	print m, len(rescutm), i, rescut[i]
			rescutm[m] = rescut[i];
			m ++;
			i ++;
		}

		if (i == rescut.size())
			break;

		// 2 new ISIs, now rescut[i] == rescutrem[j]
		// if previous has not been removed (and isi already discarded)
		if (j == 0 || rescutrem[j-1] != rescut[i-1])
			isi_upd_rem(rescut[i] - rescut[i-1], ref_ms_1, ref_ms_2, i1, i2);

		// TODO: update for case when >1 in a row have been removed (keep last non-removed and check if next has not been removed)
		if (i+1 < rescut.size()){
			isi_upd_rem(rescut[i+1] - rescut[i], ref_ms_1, ref_ms_2, i1, i2);

			//find previous not-removed and udpate if next is not removed
			int k = i - 1;
			int l = j - 1;
			while (k >=0 && l >= 0 && rescut[k] == rescutrem[l]){
				k --;
				l --;
			}

			if (k >= 0 && (j + 1 == rescutrem.size() || rescutrem[j+1] != rescut[i+1])){
				isi_upd(rescut[i+1] - rescut[k], ref_ms_1, ref_ms_2, i1, i2);
			}
		}
		j ++;
		i ++;
	}

	// print m,len(rescutm), i, len(rescut)
	// append the rest of the res
	while (i < rescut.size())
		rescutm[m++] = rescut[i++];

	frac = i2 > 0 ? i1 / float(i2) : 0;
	return rescutm;
}
//=================================================================================================================
int main(int argc, char** argv){
	std::vector<float> ref_fracs, ref_fracs2;
	std::vector<int> res_cut_2, res_ext_1, res2, imsort;
	
	// read ...

	std::ifstream clu_clean(argv[1]);
	int n1, n2;

	clu_clean >> n1;
	res_ext_1.resize(n1);
	for (int i=0; i < n1; ++i)
		clu_clean >> res_ext_1[i];

	clu_clean >> n2;
	res_cut_2.resize(n2);
	imsort.resize(n2);
	for (int i=0; i < n2; ++i)
		clu_clean >> res_cut_2[i];
	for (int i=0; i < n2; ++i)
		clu_clean >> imsort[i];

	res2 = res_cut_2;

	int step = n2 / 400;
	int calc_limit = n2 / step;

	int i1_1 = 0, i1_2 = 0, i2_1 = 0, i2_2 = 0;
	float frac2, frac1;

	int refr_ms_1 = atoi(argv[2]);
	frac1 = ref_frac(res_ext_1, refr_ms_1, 10, i1_1, i2_1);
	frac2 = ref_frac(res_cut_2, refr_ms_1, 10, i1_2, i2_2);

	ref_fracs.push_back(frac1);
	ref_fracs2.push_back(frac2);

	std::cout << frac1 << " " << frac2 << "\n";
	for (int i = 1; i < calc_limit; ++i){
		std::cout << "Iter " << i << "\n";
		std::vector<int> res_cut;
		for (int j=(i-1)*step; j < i*step; ++j){
			res_cut.push_back(res2[imsort[j]]);
		}
		std::sort(res_cut.begin(), res_cut.end());

		res_cut_2 = ref_frac_inc_rem(res_cut_2, res_cut, refr_ms_1, 10, i1_2, i2_2, frac2);
		ref_fracs.push_back(frac1);

		res_ext_1 = ref_frac_inc(res_ext_1, res_cut, refr_ms_1, 10, i1_1, i2_1, frac1);
		ref_fracs2.push_back(frac2);

		std::cout << frac1 << " " << frac2 << "\n";
	}

	// write results
	std::ofstream fracs(std::string(argv[1]) + ".frac");
	for (int i=0; i < ref_fracs.size(); ++i){
		fracs << ref_fracs[i] << " " << ref_fracs2[i] << " ";
	}
	fracs.close();
}

