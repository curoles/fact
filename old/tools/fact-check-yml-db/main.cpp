#include <cstdlib>
#include <filesystem>
//#include <format>

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

struct Fact final {
    bool checked, valid;
    fs::path file_path;
    ryml::Tree tree;

    inline size_t size_bytes() const {
        return sizeof(checked) + sizeof(valid) +
            strlen(file_path.c_str()) + tree.arena_size();
    }
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
        .valid     = true,
        .file_path = path,
        .tree      = ryml::Tree()
    };

    std::rewind(fp);
    std::string contents(sz + 1, '\0');
    size_t ret = std::fread(contents.data(), 1, sz, fp);
    assert(ret == (size_t)sz);

    std::fclose(fp);

    fact.tree = ryml::parse_in_arena(ryml::to_csubstr(contents));

    ryml::ConstNodeRef root = fact.tree.rootref();

    if (!root.is_map()) {
        std::cout << fact.tree << std::endl <<
            termcolor::bold << termcolor::bright_red << "Error: not a map" <<
            termcolor::reset << std::endl;
        return false;
    }

    if (!root.has_child("$name")) {
        std::cout << fact.tree << std::endl <<
            termcolor::bold << termcolor::bright_red << "Error: has no \"name\"" <<
            termcolor::reset << std::endl;
        return false;
    }

    auto name = root["$name"].val();
    std::string name_str(name.begin(), name.end());

    //std::cout << "add '" << name << "'" << std::endl;
    if (facts.count(name_str)) {
        std::cout << termcolor::bold << termcolor::bright_red <<
            "Error: name \"" << name_str << "\" already exists" <<
            termcolor::reset << std::endl;
        return false;
    }
    facts.emplace(name_str, fact);

    return true;
}

struct Defines {
    std::vector<std::string> types;
};

static bool check_fact(const std::string& name, Fact& fact,
    const ryml::ConstNodeRef& defs, const Defines& dfn, FactsMap& facts);

static bool check_facts(FactsMap& facts)
{
    ryml::Tree defs_tree =
        ryml::parse_in_arena(ryml::csubstr(fact_types, strlen(fact_types)));
    ryml::ConstNodeRef defs = defs_tree.rootref();

    assert(defs.has_child("types"));

    Defines dfn;
    defs["types"] >> dfn.types;

    unsigned int num_checked_facts = 0;

    do {
        num_checked_facts = 0;
        for (auto& fact : facts) {
            num_checked_facts +=
                check_fact(fact.first, fact.second, defs, dfn, facts);
            if (!fact.second.valid) {
                break;
            }
        }
    } while(num_checked_facts);

    num_checked_facts = 0;
    unsigned int num_facts = 0, num_valid_facts = 0;
    size_t size_bytes = 0;


    for (auto& fact_ : facts) {
        const Fact& fact = fact_.second;
        num_checked_facts += fact.checked;
        num_valid_facts += fact.valid;
        num_facts++;
        size_bytes += fact.size_bytes();
    }

    std::cout << "Number of facts:         " <<
        termcolor::bold << num_facts <<
        termcolor::reset << std::endl;
    std::cout << "Number of checked facts: " <<
        termcolor::bold << num_checked_facts <<
        termcolor::reset << std::endl;
    std::cout << "Number of valid facts:   " <<
        termcolor::bold << num_valid_facts <<
        termcolor::reset << std::endl;
    std::cout << "Consumed memory:         " <<
        termcolor::bold << size_bytes <<
        termcolor::reset << std::endl;

    if (num_checked_facts == 0) {
        std::cout << termcolor::bold << termcolor::bright_red <<
        "Error: can't check facts" << termcolor::reset << std::endl;
        return false;
    }

    return true;
}

static void print_error(const std::string& fact_name, const std::string& error_msg)
{
    std::cout << termcolor::bold << termcolor::bright_red <<
        "Error: \"" << fact_name << "\" " << error_msg <<
        termcolor::reset << std::endl;
}

static
bool check_fact_integrity(
    const std::string& name,
    Fact& fact,
    FactsMap& facts
);

static
bool check_fact(
    const std::string& name,
    Fact& fact,
    const ryml::ConstNodeRef& defs [[maybe_unused]],
    const Defines& dfn,
    FactsMap& facts
)
{
    if (fact.checked or !fact.valid) {
        return false;
    }

    fact.checked = true;

    ryml::ConstNodeRef root = fact.tree.rootref();

    //std::cout << "name: " << name << std::endl;
    if (!root.has_child("$type")) {
        print_error(name, "does not have type");
        fact.valid = false;
        return true;
    }

    auto fact_type = root["$type"].val();

    if (std::find(dfn.types.begin(), dfn.types.end(), fact_type) == std::end(dfn.types)) {
        std::cout << termcolor::bold << termcolor::bright_red <<
            "Error: \"" << name << "\" bad type " << fact_type <<
            termcolor::reset << std::endl;
        fact.valid = false;
        return true;
    }

    if (fact_type == "alias") {
        if (!root.has_child("$alias")) {
            print_error(name, "alias does not have $alias field");
            fact.valid = false;
            return true;
        }
        auto alias_fact = root["$alias"].val();
        const std::string alias_fact_str(alias_fact.begin(), alias_fact.end());
        if (!facts.count(alias_fact_str)) {
            print_error(name, std::string("alias '") + alias_fact_str + "' does not exist");
            fact.valid = false;
            return true;
        }
        fact.valid = facts[alias_fact_str].valid;
    }
    else {
        fact.valid = check_fact_integrity(name, fact, facts);
    }

    return true;
}

static
bool check_dependee_with_params(
    const std::string& depender_name,
    ryml::ConstNodeRef const& dependee,
    FactsMap& facts
);

static
bool check_fact_integrity(
    const std::string& name,
    Fact& fact,
    FactsMap& facts
)
{
    ryml::ConstNodeRef root = fact.tree.rootref();

    for (ryml::ConstNodeRef const& child : root.children()) {
        auto other = child.key();
        if (other.empty() or other[0] == '$' or other[0] == '\0') {
            continue;
        }
        const std::string other_key(other.begin(), other.end());
        if (facts.count(other_key) == 0) {
            print_error(name, std::string("key fact '") + other_key + "' does not exist");
            return false;
        }
        if (child.has_val()) {
            other = child.val();
            const std::string other_val(other.begin(), other.end());
            if (facts.count(other_val) == 0) {
                print_error(name, std::string("val fact '") + other_val + "' does not exist");
                return false;
            }
        }
        else if (!child.is_map()) {
            print_error(name, std::string("val fact not val and not map"));
            return false;
        }
        else {
            if (!check_dependee_with_params(name, child, facts)) {
                return false;
            }
        }
    }

    //if need re-check fact.checked = false;
    return true;
}

static
bool check_dependee_with_params(
    const std::string& depender_name,
    ryml::ConstNodeRef const& dependee,
    FactsMap& facts
)
{
    if (!dependee.has_child("$name")) {
        print_error(depender_name, "dependee does not have $name");
        return false;
    }
    auto s = dependee["$name"].val();
    const std::string dependee_name(s.begin(), s.end());
    if (facts.count(dependee_name) == 0) {
        print_error(depender_name, std::string("fact '") + dependee_name + "' does not exist");
        return false;
    }
    if (dependee.has_child("$parameters")) {
        const Fact& dependee_fact_ = facts[dependee_name];
        ryml::ConstNodeRef dependee_fact = dependee_fact_.tree.rootref();
        if (!dependee_fact.has_child("$parameters")) {
            print_error(dependee_name, "does not have parameters");
            return false;
        }
        for (ryml::ConstNodeRef const& param : dependee["$parameters"].children()) {
            s = param.key();
            const std::string param_name(s.begin(), s.end());
            if (!dependee_fact["$parameters"].has_child(s)) {
                print_error(dependee_name, "does not have parameter " + param_name);
            }
        }
    }

    return true;
}