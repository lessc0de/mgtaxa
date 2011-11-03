#!/bin/bash
mgt-icm-classifier --mode make-ref-seqdb \
--inp-ncbi-seq $MGT_NCBI_DB'/refseq/*.fna.gz' \
--db-seq $MGT_DATA/refseq-seqdb-uncomp --run-mode batch \
--lrm-user-options '-P 0413'

