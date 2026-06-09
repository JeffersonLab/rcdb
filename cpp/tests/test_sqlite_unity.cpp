// Unity translation unit for the SQLite-backed tests.
//
// The vendored SQLiteCpp amalgamation (include/RCDB/SQLiteCpp.h) defines its
// member functions out-of-line WITHOUT `inline`, so it is only safe to pull
// into a single translation unit per binary - exactly how every cpp/examples
// program (each a single .cpp) uses it. The test binary is the only consumer
// that links several object files, so test_Connection.cpp and
// test_SqLiteProvider.cpp - both of which transitively include SQLiteCpp.h -
// would otherwise produce duplicate-symbol link errors.
//
// Compiling them together here makes SQLiteCpp.h's include guard collapse the
// definitions to one copy. The two source files keep their own TEST_CASEs and
// remain editable/standalone for IDEs; CMake compiles this unity file instead
// of the two individually (see cpp/CMakeLists.txt, WITH_SQLITE branch).

#include "test_SqLiteProvider.cpp"
#include "test_Connection.cpp"
