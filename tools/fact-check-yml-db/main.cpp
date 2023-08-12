#include <cstdlib>
#include <filesystem>

#include "termcolor.hpp" // https://github.com/ikalnytskyi/termcolor
#define RYML_SINGLE_HDR_DEFINE_NOW
#include "ryml.hpp"      // https://github.com/biojppm/rapidyaml

namespace fs = std::filesystem;

static const char* fact_types [[maybe_unused]] =
#include "fact/cpp-raw-string-facts.yml"
;

static bool check_yml_db_directory(const char* dirname);

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

    if (!check_yml_db_directory(dirname)) {
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

struct Fact {
    bool checked, valid;
    fs::path file_path;
    std::string contents;
    ryml::Tree tree;
};

using FactsMap = std::map<std::string, Fact>;

static bool collect_yml_fact(const fs::path& path, FactsMap& facts);
static bool check_facts(FactsMap& facts);

static bool check_yml_db_directory(const char* dirname)
{
    FactsMap facts;

    for (const fs::directory_entry& dir_entry : fs::recursive_directory_iterator(dirname))
    {
        //std::cout << dir_entry << '\n';
        if (dir_entry.is_regular_file()) {
            if (!collect_yml_fact(dir_entry.path(), facts)) {
                return false;
            }
        }
    }

    return check_facts(facts);
}

static bool collect_yml_fact(
    const fs::path& path,
    FactsMap& facts
)
{
    std::FILE* fp = std::fopen(path.c_str(), "rb");
    if (fp == nullptr) {
        std::cout << termcolor::bold << termcolor::bright_red <<
            "Error: can not open " << termcolor::bright_yellow << path <<
            termcolor::reset << std::endl;
        return false;
    }

    std::fseek(fp, 0, SEEK_END);
    long sz = std::ftell(fp);
    if (sz == 0) {
        std::cout << termcolor::bold << termcolor::bright_red <<
            "Error: empty file " << termcolor::bright_yellow << path <<
            termcolor::reset << std::endl;
        std::fclose(fp);
        return false;
    }

    Fact fact {
        .checked   = false,
        .valid     = false,
        .file_path = path,
        .contents  = std::string(sz + 1, '\0'),
        .tree      = ryml::Tree()
    };

    std::rewind(fp);
    size_t ret = std::fread(fact.contents.data(), 1, sz, fp);
    assert(ret == (size_t)sz);

    std::fclose(fp);

    //fact.tree = ryml::parse_in_arena(ryml::to_csubstr(fact.contents));
    fact.tree = ryml::parse_in_place(ryml::to_substr(fact.contents));

    ryml::ConstNodeRef root = fact.tree.rootref();

    if (!root.is_map()) {
        std::cout << fact.tree << std::endl <<
            termcolor::bold << termcolor::bright_red << "Error: not a map " <<
            termcolor::reset << std::endl;
        return false;
    }

    if (!root.has_child("name")) {
        std::cout << fact.tree << std::endl <<
            termcolor::bold << termcolor::bright_red << "Error: has no \"name\" " <<
            termcolor::reset << std::endl;
        return false;
    }

    auto name = root["name"].val();

    //std::cout << "add '" << name << "'" << std::endl;
    facts[std::string(name.begin(), name.end())] = fact;

    return true;
}

static bool check_fact(const std::string& name, Fact& fact, ryml::ConstNodeRef& defs);

static bool check_facts(FactsMap& facts)
{
    ryml::Tree defs_tree =
        ryml::parse_in_arena(ryml::csubstr(fact_types, strlen(fact_types)));
    ryml::ConstNodeRef defs = defs_tree.rootref();

    for (auto& fact : facts) {
        check_fact(fact.first, fact.second, defs);
    }

    return true;
}

static
bool check_fact(
    const std::string& name [[maybe_unused]],
    Fact& fact [[maybe_unused]],
    ryml::ConstNodeRef& defs [[maybe_unused]]
)
{
    //std::cout << "name: " << name << std::endl;

    return true;
}