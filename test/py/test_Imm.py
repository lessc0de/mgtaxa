from MGT.Imm import *

inpSeq = \
""">NC_011206.7310 1827501 1828000
AGCCGGCTCTTGGTGCGGGCTGCCATGTTGCGATGCGCCACGCCCTTGCCAACCGTCTTG
TCGATGACCGACTCCGCGGCGCGCAGTGCGCTGCGTGCCTGCTCTTGATCACCGACATGT
ACGGCCTTCAGCACACCCTTCACATAGGTGCGCAAGCGCGACCGCAGGCTGGCATTATGC
AGGCGCCGCTTTTCATTTTGTAATACGCGCTTGCGCGCCTGAGCTGTATTGGCCAACTTT
TACTCTCCATATCTACAATCCCGCGTCTGCGGGAAATGAAGTCGCGTATTCTGGCGCCAA
CGCCCAACCCTGTCAATATCAATGGATTGCAAAAAACCACCCGGCACTACGAAAATGGGG
CGCATGGCCTACTACTCTACTTCGGTCATCACATGTACATGCCCTGGTGCCACCTGTACC
CAAAGTAGGGCGCCTGGCGCCAGAGACCTGCCTTCGCATTGCAAGCGTGATAACAGCATA
TCCAAAGAACAAGCCCCGTC
>NC_011206.7311 1827751 1828250
ATCTACAATCCCGCGTCTGCGGGAAATGAAGTCGCGTATTCTGGCGCCAACGCCCAACCC
TGTCAATATCAATGGATTGCAAAAAACCACCCGGCACTACGAAAATGGGGCGCATGGCCT
ACTACTCTACTTCGGTCATCACATGTACATGCCCTGGTGCCACCTGTACCCAAAGTAGGG
CGCCTGGCGCCAGAGACCTGCCTTCGCATTGCAAGCGTGATAACAGCATATCCAAAGAAC
AAGCCCCGTCCATTCTGACGCGCAAGGCAACACCCTCCTCCCGAAGGCTCACGACCTTCA
ATTTCAGTGCATTCGGCGCTGGGACGCCCAAAACGTCGCCCGGCACGAGATCCTCGGAAC
GAATGGCCACGGTCACCGGCATACCCGGATGCATGCCATACCGAAAACCGGTACGCAGAC
GCCAGCCAGATCCAGCCACCACCATTCCGGCTTCCGTTGCCTCCTCAATGCGCCCCACCA
GGAAATTACGAAACCCCAGC
>NC_011206.7312 1828001 1828500
CATTCTGACGCGCAAGGCAACACCCTCCTCCCGAAGGCTCACGACCTTCAATTTCAGTGC
ATTCGGCGCTGGGACGCCCAAAACGTCGCCCGGCACGAGATCCTCGGAACGAATGGCCAC
GGTCACCGGCATACCCGGATGCATGCCATACCGAAAACCGGTACGCAGACGCCAGCCAGA
TCCAGCCACCACCATTCCGGCTTCCGTTGCCTCCTCAATGCGCCCCACCAGGAAATTACG
AAACCCCAGCAAACGCGCCGCTCCCACAGTGGCGGGTCGTGCAAACACCGCACGGGGAGG
GCCTTCCTGCACAATACGCCCACCCAACAGCACTGCCATGTGATCTGCGAGCATCGCCAG
GTGCGGATCGTGGCTCACCGCCAGCACCGGCACTCCAAAATCGTGGACCTCCCGGATGAG
TTCGTCCAGAATCTCGTCGCGGGTGGCCATGTCCAGCGCCGAGGTAGGCTCGTCCAGCAG
CAGCAGCTCCGGACGCCGGG
"""

imm = Imm("test.imm")

#Neither StringIO nor mmap works - each does not have .fileno
from mmap import mmap
#inp = StringIO(inpSeq)
#inp = mmap(-1, len(inpSeq)+1)
#fastaFile = "test.imm.fasta"
#strToFile(inpSeq,fastaFile)
#imm.train(inp=fastaFile)
out = imm.train()
out.write(inpSeq)
out.close()

print "Testing file to file scoring..."

fastaFile = "test.imm.fasta"
strToFile(inpSeq,fastaFile)
imm.score(inp=fastaFile,out="test.imm.score")

print "Testing file to memory scoring..."

inpScore = imm.score(inp=fastaFile)
print inpScore

print "Testing memory to file scoring..."

inp = imm.score(out="test.imm.score")
inp.write(inpSeq)
inp.close()
#imm.flush()
