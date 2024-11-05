%module py_t2sdk_api
%include "std_string.i"
%include "std_vector.i"
%include "std_map.i"
%{
#include "t2sdk_interface.h"
#include "t2api.h"
using namespace std;
%}

namespace std {
    %template(StringMap) map<string, string>;
    %template(MapVector) vector<map<string, string>>;
}

%include "t2sdk_interface.h"
%include "t2api.h"