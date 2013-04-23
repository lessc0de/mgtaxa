#!/bin/bash
cp /usr/local/projects/GOSII/atovtchi/ref.extra.seqdb/*.fasta* $MGT_DATA/refseq-seqdb/
mgt-icm-classifier --mode train \
--db-imm $MGT_DATA/icm-refseq \
--db-seq $MGT_DATA/refseq-seqdb \
--incremental-work 1 \
--run-mode batchDep \
--lrm-user-options '-P 0413'
