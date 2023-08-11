#include <cstdlib>
#include "termcolor.hpp"

int main(int argc, char* argv[])
{
    if (argc < 2) {
        std::cout << termcolor::bold << termcolor::bright_red <<
            "Provide path to directory with YAML files" <<
            termcolor::reset << std::endl;
        return EXIT_FAILURE;
    }

    const char* dirname = argv[1];
    std::cout << termcolor::yellow <<
        "Check YAML files in " << dirname << termcolor::reset << std::endl;


    return EXIT_SUCCESS;
}