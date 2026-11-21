/* Minimal no-op Hunspell 1.6 C API stub for Mudlet Lite build.
 * Provides the same symbols as real hunspell.h so existing Mudlet code
 * compiles unchanged, but every spell-check call is a no-op.
 */
#ifndef HUNSPELL_STUB_H
#define HUNSPELL_STUB_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct Hunhandle Hunhandle;

static inline Hunhandle* Hunspell_create(const char* /*affpath*/, const char* /*dpath*/) { return (Hunhandle*)1; }
static inline Hunhandle* Hunspell_create_key(const char* /*affpath*/, const char* /*dpath*/, const char* /*key*/) { return (Hunhandle*)1; }
static inline void Hunspell_destroy(Hunhandle* /*pHunspell*/) {}
static inline int Hunspell_spell(Hunhandle* /*pHunspell*/, const char* /*word*/) { return 1; }
static inline int Hunspell_add(Hunhandle* /*pHunspell*/, const char* /*word*/) { return 0; }
static inline int Hunspell_add_with_affix(Hunhandle* /*pHunspell*/, const char* /*word*/, const char* /*affix*/) { return 0; }
static inline int Hunspell_remove(Hunhandle* /*pHunspell*/, const char* /*word*/) { return 0; }
static inline int Hunspell_add_dic(Hunhandle* /*pHunspell*/, const char* /*dpath*/) { return 0; }
static inline const char* Hunspell_get_dic_encoding(Hunhandle* /*pHunspell*/) { return "UTF-8"; }
static inline int Hunspell_suggest(Hunhandle* /*pHunspell*/, char*** /*slst*/, const char* /*word*/) { return 0; }
static inline int Hunspell_analyze(Hunhandle* /*pHunspell*/, char*** /*slst*/, const char* /*word*/) { return 0; }
static inline int Hunspell_stem(Hunhandle* /*pHunspell*/, char*** /*slst*/, const char* /*word*/) { return 0; }
static inline void Hunspell_free_list(Hunhandle* /*pHunspell*/, char*** /*slst*/, int /*n*/) {}

#ifdef __cplusplus
}
#endif

#endif /* HUNSPELL_STUB_H */
