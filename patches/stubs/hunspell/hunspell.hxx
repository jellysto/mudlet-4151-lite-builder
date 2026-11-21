/* Minimal no-op Hunspell 1.6 C++ API stub for Mudlet Lite build. */
#ifndef HUNSPELL_STUB_HXX
#define HUNSPELL_STUB_HXX

#include "hunspell.h"
#include <string>
#include <vector>

class Hunspell {
public:
    Hunspell(const char* /*affpath*/, const char* /*dpath*/) {}
    Hunspell(const std::string& /*affpath*/, const std::string& /*dpath*/) {}
    ~Hunspell() {}

    bool spell(const std::string& /*word*/) { return true; }
    int suggest(std::vector<std::string>& /*slst*/, const std::string& /*word*/) { return 0; }
    std::vector<std::string> suggest(const std::string& /*word*/) { return {}; }
    int analyze(std::vector<std::string>& /*slst*/, const std::string& /*word*/) { return 0; }
    int stem(std::vector<std::string>& /*slst*/, const std::string& /*word*/) { return 0; }
    void add(const std::string& /*word*/) {}
    void add_with_affix(const std::string& /*word*/, const std::string& /*affix*/) {}
    void remove(const std::string& /*word*/) {}
    int add_dic(const std::string& /*dpath*/, const char* /*key*/ = nullptr) { return 0; }
    const std::string& get_dic_encoding() const { static const std::string e = "UTF-8"; return e; }
};

#endif /* HUNSPELL_STUB_HXX */
