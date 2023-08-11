#include <cstdlib>
#include <filesystem>

#include "termcolor.hpp" // https://github.com/ikalnytskyi/termcolor
#define RYML_SINGLE_HDR_DEFINE_NOW
#include "ryml.hpp"      // https://github.com/biojppm/rapidyaml

namespace fs = std::filesystem;

static const char* fact_types [[maybe_unused]] =
#include "fact/cpp-raw-string-facts.yml"
;

static bool walk_yml_db_directory(const char* dirname);

int main(int argc, char* argv[])
{
    if (argc < 2) {
        std::cout << termcolor::bold << termcolor::bright_red <<
            "Provide path to directory with YAML files" <<
            termcolor::reset << std::endl;
        return EXIT_FAILURE;
    }

    const char* dirname = argv[1];

    if (!fs::exists(dirname)) {
        std::cout << termcolor::bold << dirname << termcolor::bright_red <<
            " does not exist" <<
            termcolor::reset << std::endl;
        return EXIT_FAILURE;
    }

    if (!fs::is_directory(dirname)) {
        std::cout << termcolor::bold << dirname << termcolor::bright_red <<
            " is not directory" <<
            termcolor::reset << std::endl;
        return EXIT_FAILURE;
    }

    std::cout << termcolor::yellow <<
        "Check YAML files in " << dirname << termcolor::reset << std::endl;

    walk_yml_db_directory(dirname);

    ryml::Tree facts_defines_tree =
        ryml::parse_in_arena(ryml::csubstr(fact_types, strlen(fact_types)));

    return EXIT_SUCCESS;
}

static bool check_yml_fact(const fs::path& path);

static bool walk_yml_db_directory(const char* dirname)
{
    for (const fs::directory_entry& dir_entry : fs::recursive_directory_iterator(dirname))
    {
        //std::cout << dir_entry << '\n';
        if (dir_entry.is_regular_file()) {
            if (!check_yml_fact(dir_entry.path())) {
                return false;
            }
        }
    }

    return true;
}

static bool check_yml_fact(const fs::path& path [[maybe_unused]])
{
    //std::string contents = file_get_contents<std::string>(filename);
    //ryml::Tree tree = ryml::parse_in_arena(ryml::to_csubstr(contents));

    return true;
}