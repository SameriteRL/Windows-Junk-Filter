#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <set>
#include <algorithm>

#include <chrono>
#include <windows.h> // only for Sleep()
#include <filesystem>

#include "utility.h"

namespace fs = std::filesystem;
using strSet = std::set<std::string>;

// Forward declarations
void readFile(const std::string& fileName, strSet& ignored_users, strSet& only_scan,
              strSet& key_extensions, strSet& key_words);
void sanityCheck(const fs::directory_entry& dir);
std::pair<const double, const std::string> formatBytes(double bytes);
void detectGarbage(const fs::path& dir, std::set<fs::path>& queue,
                   const strSet& key_extensions, const strSet& key_words);
void reviewGarbage(const fs::path& dir, std::set<fs::path>& queue);

/* Main program */
int main(){
    
    strSet ignored_users, only_scan, key_extensions, key_words;
    readFile("data.txt", ignored_users, only_scan, key_extensions, key_words);

    std::cout << "Garbage File Remover Utility for Windows - 6/24/2023 Build"
              << "\nBy Raymond Chen" << std::endl;
    fs::directory_entry user_dir(std::string(getenv("SystemDrive")) + "\\Users");
    sanityCheck(user_dir);

    std::set<fs::path> possible_trash;
    // Iterates through all user folders
    fs::directory_iterator itr(user_dir), end;
    while (itr != end){
        std::string user_lowname = lowerStr(itr -> path().stem().string());
        // Ignores non-folders and specified folders in ignored_users
        if (!itr -> is_directory() || ignored_users.find(user_lowname) != ignored_users.end()){
            itr++;
            continue;
        }
        // Iterates through the contents of each user folder
        fs::directory_iterator subdir_itr(*itr), subdir_end;
        while (subdir_itr != subdir_end){
            std::string subdir_lowname = lowerStr(subdir_itr -> path().stem().string());
            if (!subdir_itr -> is_directory() || only_scan.find(subdir_lowname) == only_scan.end()){
                subdir_itr++;
                continue;
            }
            // Scans each subdirectory for trash
            detectGarbage(*subdir_itr, possible_trash, key_extensions, key_words);
            // Displays all detected files and prompts the user to manage each one
            reviewGarbage(*subdir_itr, possible_trash);
            subdir_itr++;
        }
        itr++;
    }
    std::cout << "\nScan finished! Exiting shortly...\n";
    Sleep(5000);
    return 0;
}

/* Given a string file name and several string sets, reads the file and appropriately
fills each set with the content in the file. */
void readFile(const std::string& fileName, strSet& ignored_users, strSet& only_scan,
              strSet& key_extensions, strSet& key_words){
    std::ifstream in_str(fileName);
    if (!in_str.good()){
        std::cerr << "Could not open " << fileName << " for reading! Aborting...\n";
        Sleep(5000);
        exit(1);
    }
    std::string command, arg;
    while (in_str >> command >> arg){
        if (command == "i") ignored_users.insert(arg);
        else if (command == "s") only_scan.insert(arg);
        else if (command == "e") key_extensions.insert(arg);
        else if (command == "w") key_words.insert(arg);
        else{
            std::cerr << "Error parsing data file! Aborting...\n";
            Sleep(5000);
            exit(1);
        }
    }
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

/* Given a path pointing to a directory and an empty set, iterates through all
files within the directory along with all files within subdirectories. Detects
whether each file is a possible garbage file and adds it to the set if so. */
void detectGarbage(const fs::path& dir, std::set<fs::path>& queue,
                   const strSet& key_extensions, const strSet& key_words){
    // Iterates through all files in the directory
    fs::directory_iterator itr(dir, fs::directory_options::skip_permission_denied), end;
    while (itr != end){
        fs::path f_path(*itr);
        std::string f_lowname = lowerStr(f_path.stem().string());
        std::string f_extension = f_path.extension().string();
        // Determines if the file is a possible junk file
        if (f_extension == ".msi"){
            queue.insert(f_path);
            itr++;
            continue;
        }
        if (key_extensions.find(f_extension) != key_extensions.end()){
            for (const auto& word: key_words){
                if (f_lowname.find(word) != std::string::npos){
                    queue.insert(f_path);
                    break;
                }
            }
        }
        itr++;
    }
}

/* Given a path pointing to a directory and a set filled with queried files,
iterates through the set and prompts the user to review each file. */
void reviewGarbage(const fs::path& dir, std::set<fs::path>& queue){
    std::string command;
    if (queue.size() == 0) return;
    std::cout << "\nPossible trash files detected (" << dir.string() << "):\n";
    for (auto& file: queue){
        std::cout << file.filename().string() << std::endl;
    }
    std::set<fs::path>::iterator i = queue.begin();
    while (i != queue.end()){
        // Gets the file's last write time as a readable string
        time_t raw_time = to_time_t(last_write_time(*i));
        struct tm* raw_time_tm = localtime(&raw_time);
        char buff[32];
        strftime(buff, 32, "%m/%d/%Y at %H:%M:%S", raw_time_tm);
        // Gets the file's size as a readable string
        std::pair<const double, const std::string> size = formatBytes(file_size(*i));
        // Prints the file info and a prompt asking whether to delete the file
        std::cout << std::endl << std::string(36, '-') << std::endl
                  << i -> filename().string() << "\nSize: " << std::fixed
                  << std::setprecision(1) << size.first << ' ' << size.second
                  << std::endl << "Last write: " << buff << std::endl
                  << std::string(36, '-') << "\n\nDelete file? (y/n) ";
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