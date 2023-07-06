#ifndef __UTILITY_H__
#define __UTILITY_H__

#include <chrono>

std::string lowerStr(const std::string& str);
template <typename TP> std::time_t to_time_t(const TP tp);

/* Takes in a type that has all elements of TrivialClock implemented. Copied
from Stack Overflow because there's no easy way to convert from
filesystem::file_time_type to time_t. */
template <typename TP>
std::time_t to_time_t(const TP tp){
    using namespace std::chrono;
    auto sctp = time_point_cast<system_clock::duration>
                (tp - TP::clock::now() + system_clock::now());
    return system_clock::to_time_t(sctp);
}

#endif