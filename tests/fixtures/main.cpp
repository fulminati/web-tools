#include <Arduino.h>

// @inject "page.html"
const char page[] = {0x3c, 0x68, 0x31, 0x3e, 0x50, 0x61, 0x67, 0x65, 0x20, 0x30, 0x3c, 0x2f, 0x68, 0x31, 0x3e, 0x0a, 0x0a, 0x3c, 0x70, 0x3e, 0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x3c, 0x2f, 0x70, 0x3e, 0x0a, 0x0a, 0x3c, 0x70, 0x3e, 0x7b, 0x7b, 0x20, 0x63, 0x69, 0x61, 0x6f, 0x20, 0x7d, 0x7d, 0x3c, 0x2f, 0x70, 0x3e, 0x0a, 0x3c, 0x70, 0x3e, 0x7b, 0x7b, 0x20, 0x63, 0x69, 0x61, 0x6f, 0x20, 0x7d, 0x7d, 0x3c, 0x2f, 0x70, 0x3e, 0x0a, 0x0a, 0x3c, 0x70, 0x3e, 0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x3c, 0x2f, 0x70, 0x3e, 0x0a};

String titolo = "Titoilo";


// @inject "index.html"
const String paginaIndex = "<html><body><h1>" + titolo + "</h1></body>";

__cpp_aggregate_nsdmi



