#include <iostream>
#include <iomanip>
#include <string>
#include <set>
#include <algorithm>

#include <chrono>
#include <windows.h> // only for Sleep()
#include <filesystem>

namespace fs = std::filesystem;

// Forward declarations
std::string lowerStr(const std::string& str);
void sanityCheck(const fs::directory_entry& dir);
std::pair<const double, const std::string> formatBytes(double bytes);
template <typename TP> std::time_t to_time_t(TP tp);
void detectGarbage(const fs::path& dir, std::set<fs::path>& queue);
void reviewGarbage(const fs::path& dir, std::set<fs::path>& queue);

/* Main program */
int main(){

    // Built-in user folders to ignore, might move to external file later
    std::set<std::string> ignore{"All Users", "Default", "Default User", "Public"};

    // Program header output
    std::cout << "Raymond's Garbage Remover (5/24/2023 build)\n";
    // Gets the system drive letter
    fs::directory_entry user_dir(std::string(getenv("SystemDrive")) + "\\Users");
    sanityCheck(user_dir);
    std::string command;
    std::set<fs::path> possible_trash;
    // Iterates through all user folders
    for (const auto& user_entry: fs::directory_iterator(user_dir)){
        std::string user_name = user_entry.path().filename().string();
        if (!user_entry.is_directory() || ignore.find(user_name) != ignore.end())
            continue;
        fs::directory_entry downloads_dir(user_entry.path().string() + "\\Downloads");
        // Quick sanity check
        if (!fs::directory_entry(user_dir).exists()){
            std::cout << downloads_dir.path().string() << " doesn't exist, skipping...\n";
            continue;
        }
        // Scans the downloads folder for trash
        detectGarbage(downloads_dir, possible_trash);
        // Displays all detected files and prompts the user to manage each one
        reviewGarbage(downloads_dir, possible_trash);
    }
    std::cout << "\nScan finished! Exiting shortly...\n";
    Sleep(5000);
    return 0;
}

/* Given a string, returns a copy of the string with all uppercase letters turned
lowercase, retaining any non-letters. */
std::string lowerStr(const std::string& str){
    std::string result = str;
    for (auto& c: result){
        c = tolower(c);
    }
    return result;
}

/* Given a directory_entry pointing to a directory, checks if it is valid and
terminates the program if not. */
void sanityCheck(const fs::directory_entry& dir){
    if (!dir.exists()){
        std::cout << dir.path().filename() << " does not exist, aborting...\n";
        Sleep(5000);
        exit(1);
    }
}

/* Given a double value of bytes, returns a pair containing a double and string,
representing the bytes in it's appropriate unit of measurement. */
std::pair<const double, const std::string> formatBytes(double bytes){
    if (bytes >= 1099511627776){
        return std::make_pair(bytes / 1099511627776, "TB");
    }
    else if (bytes >= 1073741824){
        return std::make_pair(bytes / 1073741824, "GB");
    }
    else if (bytes >= 1048576){
        return std::make_pair(bytes / 1048576, "MB");
    }
    else if (bytes >= 1024){
        return std::make_pair(bytes / 1024, "KB");
    }
    return std::make_pair(bytes, "bytes");
}

/* Takes in a type that has all elements of TrivialClock implemented. Copied
from Stack Overflow because there's no easy way to convert from
std::filesystem::file_time_type to time_t. */
template <typename TP>
std::time_t to_time_t(TP tp){
    using namespace std::chrono;
    auto sctp = time_point_cast<system_clock::duration>
                (tp - TP::clock::now() + system_clock::now());
    return system_clock::to_time_t(sctp);
}

/* Given a path pointing to a directory and an empty set, iterates through all
files within the directory along with all files within subdirectories. Detects
whether each file is a possible garbage file and adds it to the set if so. */
void detectGarbage(const fs::path& dir, std::set<fs::path>& queue){

    // Extensions/words used to detect possible trash
    std::set<std::string> key_extensions{".msi", ".exe", ".jar", ".zip"};
    std::set<std::string> key_words{"setup", "install", "wizard",
                                    "betterdiscord", "jdk", "jre"};

    // Iterates through all files in the directory
    for (const auto& f_entry: fs::recursive_directory_iterator(dir)){
        fs::path f_path(f_entry);
        std::string f_name = lowerStr(f_path.stem().string());
        std::string f_extension = f_path.extension().string();
        // Determines if the file is a possible junk file
        if (key_extensions.find(f_extension) == key_extensions.end()) continue;
        for (const auto& word: key_words){
            if (f_name.find(word) != std::string::npos){
                queue.insert(f_path);
                break;
            }
        }
    }
}

/* Given a path pointing to a directory and a set filled with queried files,
iterates through the set and prompts the user to review each file within. */
void reviewGarbage(const fs::path& dir, std::set<fs::path>& queue){
    std::string command;
    if (queue.size() == 0){
        std::cout << "\nNo possible trash files detected.\n";
        return;
    }
    std::cout << "\nPossible trash files detected (" << dir.string() << "):\n";
    for (auto& file: queue) std::cout << file.filename().string() << std::endl;
    std::set<fs::path>::iterator i = queue.begin();
    while (i != queue.end()){
        // Gets the file's last write time as a readable string
        time_t raw_time = to_time_t(last_write_time(*i));
        struct tm* raw_time_tm = localtime(&raw_time);
        char buff[32];
        strftime(buff, 32, "%m/%d/%Y at %H:%M:%S", raw_time_tm);
        // Gets the file's size as a readable string
        std::pair<const double, const std::string> size = formatBytes(file_size(*i));
        // Prints the file info and a deletion prompt
        std::cout << std::endl << std::string(30, '-') << std::endl
                  << i -> filename().string() << "\nSize: " << std::fixed
                  << std::setprecision(1) << size.first << ' ' << size.second
                  << std::endl << "Last write: " << buff << std::endl
                  << std::string(30, '-') << "\n\nDelete file? (y/n) ";
        // Handles yes/no response
        std::cin >> command;
        if (lowerStr(command) == "y"){
            remove(*i);
            std::cout << "File deleted.\n";
        }
        else{
            std::cout << "File skipped.\n";
        }
        i = queue.erase(i);
    }
}