import pcsParser

pcs = pcsParser.PCS('../examples/params-lkh.pcs')

with open('../examples/params-lkh-copy.pcs','w') as f_out:
    f_out.write(pcs.printDocument())

pcs2 = pcsParser.PCS('../examples/params-cplex.pcs')

with open('../examples/params-cplex-copy.pcs','w') as f_out:
    f_out.write(pcs2.printDocument())

print('\n' + '*'*50) 
print("ASCENT_CANDIDATES is not a child, so it should always be active, regardless of the configuration passed in. We are passing in an empty configuration and seeing if it is active.")
print("pcs.isActive('ASCENT_CANDIDATES',{})? " + str(pcs.isActive('ASCENT_CANDIDATES',{})))

print('\n' + '*'*50)
print("KICKS is a child, it should only be active if KICK_WALK=NO.")
print("pcs.isActive('KICKS',{'KICK_WALK':'NO'})? " + str(pcs.isActive('KICKS',{'KICK_WALK':'NO'})))

print('\n' + '*'*50)
print("Here we can see it works as well..")
print("pcs.isActive('KICKS',{'KICK_WALK':'YES'})? " + str(pcs.isActive('KICKS',{'KICK_WALK':'YES'})))


print('\n' + '*'*50)
print("Note that MAYBE is not one of the allowed values for it's parent. But we don't check for that.")
try:
    exception = False
    print("pcs.isActive('KICKS',{'KICK_WALK':'MAYBE'})? " + str(pcs.isActive('KICKS',{'KICK_WALK':'MAYBE'})))
except Exception:
    print("An exception was raised")
    exception = True
if(not exception):
    print("No exception was raised")



print('\n' + '*'*50)
print("However, if there is no information specified about it's parents then an exception to be raised because we cannot determine whether or not it is active.")
try:
    exception = False
    print("pcs.isActive('KICKS',{})? " + str(pcs.isActive('KICKS',{})))
except Exception:
    print("An exception was raised")
    exception = True
if(not exception):
    print("No exception was raised")
