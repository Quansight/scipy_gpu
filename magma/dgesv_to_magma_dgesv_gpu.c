#include <cuda.h>
#include "magma_v2.h"

void dgesv_(int* N, int* NRHS, double* A, int* LDA, int* IPIV, double* B, int* LDB, int* INFO) {
    magma_init();
    magma_queue_t queue = NULL;
    magma_int_t dev = 0;
    magma_queue_create(dev, &queue);

    magma_int_t m = *N;
    magma_int_t n = *NRHS;
    magma_int_t mm = m * m;
    magma_int_t mn = m * n;
    double* d_a;
    double* d_c;
    magma_int_t err;
    magma_int_t* piv, info;
    err = magma_dmalloc(&d_a, mm);
    err = magma_dmalloc(&d_c, mn);
    magma_dsetmatrix(m, m, A, m, d_a, m, queue);
    magma_dsetmatrix(m, n, B, m, d_c, m, queue);
    piv = (magma_int_t*)malloc(m * sizeof(magma_int_t));
    magma_dgesv_gpu(m, n, d_a, m, piv, d_c, m, &info);
    magma_dgetmatrix(m, n, d_c, m, B, m, queue);
    free(piv);
    magma_free(d_a);
    magma_free(d_c);
    magma_queue_destroy(queue);
    magma_finalize();
}
