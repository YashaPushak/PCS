import pcsParser

pcs = pcsParser.PCS('../examples/params-lkh.pcs')

with open('../examples/params-lkh-copy.pcs','w') as f_out:
    f_out.write(pcs.printDocument())
