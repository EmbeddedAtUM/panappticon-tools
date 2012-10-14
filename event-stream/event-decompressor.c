#include <stdlib.h>
#include <stdio.h>
#include "minilzo/minilzo.h"

int main() {
  FILE* stream = stdin; 
  FILE* ostream = stdout;

  int ret;
  unsigned int len;
  lzo_uint uncmp_len;
  size_t remain;

  char* uncompressed;
  char* compressed;

  while (fread(&len, 4, 1, stream)) {
    if (ferror(stream))
      goto errif;
    if (feof(stream))
      goto out;

    compressed = malloc(len);
    if (!compressed)
      goto errmem;
    uncmp_len = 10 * len; // Hopefully 10X is enough...
    uncompressed = malloc(uncmp_len); 
    if (!uncompressed)
      goto errmem;

    remain = len;
    remain -= len * fread(compressed, len, 1, stream);
    if (remain) {
      if (ferror(stream))
	goto errif;
      else if (feof(stream))
	goto erreof;
      else 
	goto err;
    }
    ret = lzo1x_decompress_safe(compressed, len, uncompressed, &uncmp_len, NULL);
    if (ret)
      goto errlzo;
    
    remain = uncmp_len;
    remain -= uncmp_len * fwrite(uncompressed, uncmp_len, 1, ostream);
    if (remain) {
      if (ferror(stream))
	goto errof;
      else
	goto err;
    }
    
    free(compressed);
    compressed = NULL;

    free(uncompressed);
    uncompressed = NULL;
  }

  return 0;
  
 err:
  fprintf(stderr, "Unknown error\n");
  ret = 1;
  goto out;

 errlzo:
  fprintf(stderr, "Decompression error: %d\n", ret);
  ret = 1;
  goto out;

 errof:
  fprintf(stderr, "Error while writing output: %d.\n", ferror(ostream));
  ret = 1;
  goto out;

 errif:
  fprintf(stderr, "Error while reading input: %d.\n", ferror(stream));
  ret = 1;
  goto out;

 erreof:
  fprintf(stderr, "Unexpected end-of-file.\n");
  ret = 1;
  goto out;

 errmem:
  fprintf(stderr, "Failed to allocate memory.\n");
  ret = 1;
  goto out;

 out:
  if (uncompressed)
    free(uncompressed);
  if (compressed)
    free(compressed);
  return ret;
}
