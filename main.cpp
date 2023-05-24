#include <iostream>
#include <fstream>
#include <string>
#include <set>
#include <algorithm>

#include <windows.h>
#include <filesystem>

using namespace std::filesystem;

// Forward declarations
std::string lowerStr(const std::string& str);
void sanityCheck(const directory_entry& dir);
void detectGarbage(const path& dir, std::set<path>& queue);
void deleteGarbage(const path& dir, std::set<path>& queue);

/* Main program */
int main(){
    std::cout << "Raymond's Garbage Remover (5/24/2023 build)\n";
    // Gets the system drive letter
    directory_entry user_dir(std::string(getenv("SystemDrive")) + "\\Users");
    sanityCheck(user_dir);
    // Set of built-in user folders to ignore
    std::set<std::string> ignore{"All Users", "Default", "Default User", "Public"};
    std::string command; std::set<path> possible_trash;
    // Iterates through all user folders
    for (const auto& user_entry: directory_iterator(user_dir)){
        std::string user_name = user_entry.path().filename().string();
        if (!user_entry.is_directory() || ignore.find(user_name) != ignore.end()) continue;
        directory_entry downloads_dir(user_entry.path().string() + "\\Downloads");
        // Quick sanity check
        if (!directory_entry(user_dir).exists()){
            std::cout << "User " << user_name << " has no 'Downloads' folder, skipping...\n";
            continue;
        }
        // Scans the downloads folder for trash
        detectGarbage(downloads_dir, possible_trash);
        // Displays all detected files and prompts the user to manage each one
        deleteGarbage(downloads_dir, possible_trash);
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

void sanityCheck(const directory_entry& dir){
    if (!dir.exists()){
        std::cout << dir.path().filename() << " does not exist, aborting...\n";
        Sleep(5000);
        exit(1);
    }
}

/* Given a path pointing to a directory, iterates through all files within the
directory along with all files within subdirectories. Detects whether each file
is a possible garbage file and adds it to a set if so. Returns the set. */
void detectGarbage(const path& dir, std::set<path>& queue){
    // Extensions used to detect possible trash
    std::set<std::string> key_extensions{".msi", ".exe", ".zip"};
    // Iterates through all files in the directory
    for (const auto& f_entry: recursive_directory_iterator(dir)){
        path f_path(f_entry);
        std::string f_extension = f_path.extension().string();
        if (key_extensions.find(f_extension) == key_extensions.end()) continue;
        queue.insert(f_path);
    }
}

void deleteGarbage(const path& dir, std::set<path>& queue){
    std::string command;
    if (queue.size() == 0){
        std::cout << "\nNo possible trash files detected.\n";
        return;
    }
    std::cout << "\nPossible trash files detected (" << dir.string() << "):\n";
    for (auto& file: queue) std::cout << file.filename() << std::endl;
    std::set<path>::iterator i = queue.begin();
    while (i != queue.end()){
        std::cout << "\nDelete " << i -> filename() << "? (y/n) ";
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