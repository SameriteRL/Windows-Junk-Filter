#include <iostream>
#include <string>
#include <set>

#include "utility.h"

/* Given a string, returns a copy of the string with all uppercase letters turned
lowercase, retaining any non-letters. */
std::string lowerStr(const std::string& str){
    std::string result = str;
    std::string::iterator itr = result.begin();
    while (itr != result.end()){
        if (!isdigit(*itr) && !isalpha(*itr)){
            itr = result.erase(itr);
        }
        else{
            if (isalpha(*itr)){
                *itr = tolower(*itr);
            }
            itr++;
        }
    }
    return result;
}